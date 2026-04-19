/**
 * Type definitions for TehutiGuard
 */

export interface PolicyContext {
  action: 'read' | 'write' | 'execute' | 'propose';
  resource: string;
  user?: string;
  metadata?: Record<string, any>;
}

export interface PolicyDecision {
  allowed: boolean;
  reason: string;
  maatRole?: 'inner-ring' | 'middle-ring' | 'outer-ring';
  permissions?: {
    read: boolean;
    write: boolean;
    execute: boolean;
    propose: boolean;
  };
  metadata?: Record<string, any>;
}

