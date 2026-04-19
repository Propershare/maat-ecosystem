/**
 * Three-Ring Governance System
 * Maat-Aligned Permission Structure
 */

export type MaatRole = 'inner-ring' | 'middle-ring' | 'outer-ring';

export interface ThreeRingPolicy {
  role: MaatRole;
  description: string;
  permissions: {
    read: boolean;
    write: boolean;
    execute: boolean;
    propose: boolean;
  };
  resources: string[];
}

/**
 * Three-ring governance definitions
 */
export const THREE_RING_GOVERNANCE: Record<MaatRole, ThreeRingPolicy> = {
  'inner-ring': {
    role: 'inner-ring',
    description: 'Canon - Read-only access to protected resources',
    permissions: {
      read: true,
      write: false,
      execute: false,
      propose: false
    },
    resources: [
      'jarvis/maat-graphs/',  // Canon resources
    ]
  },
  'middle-ring': {
    role: 'middle-ring',
    description: 'Scholarship - Can propose changes, read-only access',
    permissions: {
      read: true,
      write: false,
      execute: false,
      propose: true
    },
    resources: [
      'jarvis/rbg-library/',  // Scholarship resources
    ]
  },
  'outer-ring': {
    role: 'outer-ring',
    description: 'Monetized - Full access to monetized resources',
    permissions: {
      read: true,
      write: true,
      execute: true,
      propose: true
    },
    resources: [
      'jarvis/monetization/',  // Monetized resources
      'maatlangchain/',
      'tehuti-lab-webui/',
    ]
  }
};

/**
 * Check if a resource is accessible by a role
 */
export function isResourceAccessible(role: MaatRole, resource: string): boolean {
  const policy = THREE_RING_GOVERNANCE[role];
  
  // Check if resource matches any of the role's allowed resources
  return policy.resources.some(allowedResource => 
    resource.startsWith(allowedResource)
  );
}

/**
 * Get policy for a role
 */
export function getPolicyForRole(role: MaatRole): ThreeRingPolicy {
  return THREE_RING_GOVERNANCE[role];
}

