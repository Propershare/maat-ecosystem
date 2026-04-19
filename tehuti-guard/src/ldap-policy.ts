/**
 * LDAP Policy Enforcement for TehutiGuard
 * Maat-Aligned Three-Ring Governance via LDAP Groups
 */

import { PolicyDecision, PolicyContext } from './types';

export interface LDAPGroup {
  name: string;
  maatRole: 'inner-ring' | 'middle-ring' | 'outer-ring';
}

export interface LDAPUser {
  uid: string;
  groups: string[];
  maatRole?: string;
}

/**
 * Map LDAP groups to three-ring governance permissions
 */
export const LDAP_GROUP_MAPPING: Record<string, LDAPGroup> = {
  'inner-ring': {
    name: 'inner-ring',
    maatRole: 'inner-ring'
  },
  'middle-ring': {
    name: 'middle-ring',
    maatRole: 'middle-ring'
  },
  'outer-ring': {
    name: 'outer-ring',
    maatRole: 'outer-ring'
  },
  'agents': {
    name: 'agents',
    maatRole: 'outer-ring' // Agents have full access
  },
  'admins': {
    name: 'admins',
    maatRole: 'outer-ring' // Admins have full access
  }
};

/**
 * Get user's Maat role from LDAP groups
 */
export function getMaatRoleFromLDAPGroups(groups: string[]): 'inner-ring' | 'middle-ring' | 'outer-ring' {
  // Check groups in priority order (outer > middle > inner)
  if (groups.includes('outer-ring') || groups.includes('admins') || groups.includes('agents')) {
    return 'outer-ring';
  }
  if (groups.includes('middle-ring')) {
    return 'middle-ring';
  }
  if (groups.includes('inner-ring')) {
    return 'inner-ring';
  }
  
  // Default to inner-ring (most restrictive)
  return 'inner-ring';
}

/**
 * Get permissions for a Maat role
 */
export function getPermissionsForMaatRole(role: 'inner-ring' | 'middle-ring' | 'outer-ring'): {
  read: boolean;
  write: boolean;
  execute: boolean;
  propose: boolean;
} {
  switch (role) {
    case 'inner-ring':
      return {
        read: true,
        write: false,
        execute: false,
        propose: false
      };
    case 'middle-ring':
      return {
        read: true,
        write: false,
        execute: false,
        propose: true
      };
    case 'outer-ring':
      return {
        read: true,
        write: true,
        execute: true,
        propose: true
      };
  }
}

/**
 * Enforce policy based on LDAP group membership
 */
export function enforceLDAPPolicy(
  context: PolicyContext,
  ldapUser: LDAPUser
): PolicyDecision {
  const maatRole = getMaatRoleFromLDAPGroups(ldapUser.groups);
  const permissions = getPermissionsForMaatRole(maatRole);
  
  // Check action against permissions
  let allowed = false;
  let reason = '';
  
  switch (context.action) {
    case 'read':
      allowed = permissions.read;
      reason = permissions.read 
        ? `Read allowed for ${maatRole} role`
        : `Read denied for ${maatRole} role`;
      break;
    case 'write':
      allowed = permissions.write;
      reason = permissions.write
        ? `Write allowed for ${maatRole} role`
        : `Write denied for ${maatRole} role (use propose instead)`;
      break;
    case 'execute':
      allowed = permissions.execute;
      reason = permissions.execute
        ? `Execute allowed for ${maatRole} role`
        : `Execute denied for ${maatRole} role`;
      break;
    case 'propose':
      allowed = permissions.propose;
      reason = permissions.propose
        ? `Propose allowed for ${maatRole} role`
        : `Propose denied for ${maatRole} role`;
      break;
    default:
      allowed = false;
      reason = `Unknown action: ${context.action}`;
  }
  
  return {
    allowed,
    reason,
    maatRole,
    permissions,
    metadata: {
      ldapUser: ldapUser.uid,
      ldapGroups: ldapUser.groups,
      action: context.action,
      resource: context.resource
    }
  };
}

/**
 * Query LDAP for user groups
 * Implements actual LDAP query using ldapjs
 */
export async function queryLDAPUserGroups(uid: string): Promise<string[]> {
  try {
    // Dynamic import to avoid requiring ldapjs at module load time
    const ldap = await import('ldapjs');
    
    // LDAP server configuration from environment
    const LDAP_HOST = process.env.LDAP_HOST || '127.0.0.1';
    const LDAP_PORT = parseInt(process.env.LDAP_PORT || '389');
    const LDAP_BASE = process.env.LDAP_BASE || 'dc=tehuti,dc=lab';
    const LDAP_ADMIN = process.env.LDAP_ADMIN || 'cn=admin,dc=tehuti,dc=lab';
    const LDAP_PASSWORD = process.env.LDAP_ADMIN_PASSWORD || '';
    
    // Create LDAP client
    const client = ldap.createClient({
      url: `ldap://${LDAP_HOST}:${LDAP_PORT}`
    });
    
    return new Promise((resolve, reject) => {
      // Bind as admin
      client.bind(LDAP_ADMIN, LDAP_PASSWORD, (err) => {
        if (err) {
          client.unbind();
          reject(new Error(`LDAP bind failed: ${err.message}`));
          return;
        }
        
        // Search for user
        const searchOptions = {
          filter: `(uid=${uid})`,
          scope: 'sub',
          attributes: ['memberOf', 'maatRole']
        };
        
        const groups: string[] = [];
        
        client.search(`ou=users,${LDAP_BASE}`, searchOptions, (err, res) => {
          if (err) {
            client.unbind();
            reject(new Error(`LDAP search failed: ${err.message}`));
            return;
          }
          
          res.on('searchEntry', (entry) => {
            // Extract groups from memberOf attribute
            const memberOf = entry.attributes.find(attr => attr.type === 'memberOf');
            if (memberOf && memberOf.vals) {
              for (const groupDn of memberOf.vals) {
                // Extract CN from DN (e.g., "cn=outer-ring,ou=groups,dc=tehuti,dc=lab" -> "outer-ring")
                const cnMatch = groupDn.match(/^cn=([^,]+)/i);
                if (cnMatch) {
                  groups.push(cnMatch[1]);
                }
              }
            }
            
            // Also check maatRole attribute
            const maatRole = entry.attributes.find(attr => attr.type === 'maatRole');
            if (maatRole && maatRole.vals && maatRole.vals.length > 0) {
              // maatRole can be inner-ring, middle-ring, or outer-ring
              const role = maatRole.vals[0];
              if (!groups.includes(role)) {
                groups.push(role);
              }
            }
          });
          
          res.on('error', (err) => {
            client.unbind();
            reject(new Error(`LDAP search error: ${err.message}`));
          });
          
          res.on('end', () => {
            client.unbind();
            resolve(groups);
          });
        });
      });
    });
  } catch (error) {
    // If ldapjs is not available, return empty array and log warning
    console.warn(`LDAP query failed (ldapjs may not be installed): ${error}`);
    return [];
  }
}

