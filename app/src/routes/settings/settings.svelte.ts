// ── Privilege helpers (mirrors the logic in the settings pages) ────────────

export type Privilege = 'GUEST' | 'REPORTER' | 'DEVELOPER' | 'MAINTAINER' | 'OWNER';


export const PRIVILEGE_ORDER = ['GUEST', 'REPORTER', 'DEVELOPER', 'MAINTAINER', 'OWNER'];


export const BADGE_COLOR: Record<Privilege, string> = {
  GUEST:      'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
  REPORTER:   'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  DEVELOPER:  'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  MAINTAINER: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
  OWNER:      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
};

// ── PRIVILEGE HELPERS ──────────────────────────────────────────────────────────────

// Maps numeric DB id (0–4) ↔ Privilege string
export function privilegeFromId(id: number): Privilege {
    return PRIVILEGE_ORDER[id] ?? 'GUEST';
  }
export function privilegeToId(p: Privilege): number {
    return PRIVILEGE_ORDER.indexOf(p);
  }