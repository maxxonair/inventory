<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth.js';
  import { get } from 'svelte/store';
  import {
    Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell,
    Button, Modal, Label, Input, Select, Badge, Spinner, Alert
  } from 'flowbite-svelte';
  import {
    PlusOutline, TrashBinOutline, EditOutline, LockSolid
  } from 'flowbite-svelte-icons';

  // ── Types ──────────────────────────────────────────────────────────────────

  type Privilege = 'GUEST' | 'REPORTER' | 'DEVELOPER' | 'MAINTAINER' | 'OWNER';

  interface AppUser {
    id: number;
    username: string;
    privilege: Privilege;
  }

  // ── Constants ──────────────────────────────────────────────────────────────

  const PRIVILEGE_ORDER: Privilege[] = ['GUEST', 'REPORTER', 'DEVELOPER', 'MAINTAINER', 'OWNER'];

  const BADGE_COLOR: Record<Privilege, string> = {
    GUEST:      'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    REPORTER:   'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    DEVELOPER:  'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    MAINTAINER: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
    OWNER:      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  };

  // ── State ──────────────────────────────────────────────────────────────────

  let currentUser = $state(get(user) as AppUser | null);
  let users       = $state<AppUser[]>([]);
  let loading     = $state(true);
  let errorMsg    = $state('');
  let successMsg  = $state('');

  // Modals
  let showAddModal      = $state(false);
  let showEditModal     = $state(false);
  let showDeleteModal   = $state(false);
  let showPasswordModal = $state(false);

  // Add user form
  let newUsername   = $state('');
  let newPassword   = $state('');
  let newPrivilege  = $state<Privilege>('GUEST');

  // Edit user
  let editTarget    = $state<AppUser | null>(null);
  let editPrivilege = $state<Privilege>('GUEST');

  // Delete user
  let deleteTarget  = $state<AppUser | null>(null);

  // Password change
  let passwordTarget   = $state<AppUser | null>(null);
  let newPasswordValue = $state('');
  let confirmPassword  = $state('');

  // ── Helpers ────────────────────────────────────────────────────────────────

  function rank(p: Privilege) {
    return PRIVILEGE_ORDER.indexOf(p);
  }

  function isAtLeast(p: Privilege) {
    return currentUser ? rank(currentUser.privilege) >= 3 : false;
  }

  function canManage(target: AppUser) {
    if (!currentUser) return false;
    if (currentUser.id === target.id) return false;            // can't edit yourself here
    if (!isAtLeast('MAINTAINER')) return false;                // must be MAINTAINER+
    if (target.privilege === 'OWNER' && !isAtLeast('OWNER')) return false;
    return true;
  }

  function assignablePrivileges(): Privilege[] {
    if (!currentUser) return [];
    if (isAtLeast('OWNER')) return PRIVILEGE_ORDER;
    if (isAtLeast('MAINTAINER')) return PRIVILEGE_ORDER.filter(p => p !== 'OWNER');
    return [];
  }

  function canChangePassword(target: AppUser) {
    if (!currentUser) return false;
    if (currentUser.id === target.id) return true;             // own account always allowed
    return canManage(target);
  }

  function flash(type: 'success' | 'error', msg: string) {
    if (type === 'success') { successMsg = msg; setTimeout(() => successMsg = '', 3000); }
    else                    { errorMsg   = msg; setTimeout(() => errorMsg   = '', 4000); }
  }

  // ── API calls ──────────────────────────────────────────────────────────────

  async function fetchUsers() {
    loading = true;
    try {
      const res = await fetch('/api/users', { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to load users');
      users = await res.json();
    } catch (e: any) {
      flash('error', e.message);
    } finally {
      loading = false;
    }
  }

  async function addUser() {
    if (!newUsername.trim() || !newPassword.trim()) return;
    try {
      const res = await fetch('/api/add_user', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: newUsername, password: newPassword, privilege: newPrivilege }),
      });
      if (!res.ok) throw new Error((await res.json()).error || 'Failed to add user');
      flash('success', `User "${newUsername}" added.`);
      showAddModal = false;
      newUsername = ''; newPassword = ''; newPrivilege = 'GUEST';
      await fetchUsers();
    } catch (e: any) { flash('error', e.message); }
  }

  async function savePrivilege() {
    if (!editTarget) return;
    try {
      const res = await fetch(`/api/users/${editTarget.id}`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ privilege: editPrivilege }),
      });
      if (!res.ok) throw new Error((await res.json()).error || 'Failed to update privilege');
      flash('success', `Privilege updated for "${editTarget.username}".`);
      showEditModal = false;
      await fetchUsers();
    } catch (e: any) { flash('error', e.message); }
  }

  async function deleteUser() {
    if (!deleteTarget) return;
    try {
      const res = await fetch(`/api/delete_user`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: deleteTarget.username }),
      });
      if (!res.ok) throw new Error((await res.json()).error || 'Failed to delete user');
      flash('success', `User "${deleteTarget.username}" deleted.`);
      showDeleteModal = false;
      await fetchUsers();
    } catch (e: any) { flash('error', e.message); }
  }

  async function changePassword() {
    if (!passwordTarget) return;
    if (newPasswordValue !== confirmPassword) {
      flash('error', 'Passwords do not match.');
      return;
    }
    if (newPasswordValue.length < 6) {
      flash('error', 'Password must be at least 6 characters.');
      return;
    }
    try {
      const res = await fetch(`/api/users/${passwordTarget.id}/password`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: newPasswordValue }),
      });
      if (!res.ok) throw new Error((await res.json()).error || 'Failed to change password');
      flash('success', `Password updated for "${passwordTarget.username}".`);
      showPasswordModal = false;
      newPasswordValue = ''; confirmPassword = '';
    } catch (e: any) { flash('error', e.message); }
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  onMount(() => {
    if (!currentUser || !isAtLeast('MAINTAINER')) {
      goto('/');
      return;
    }
    fetchUsers();
  });
</script>

<!-- ── Alerts ───────────────────────────────────────────────────────────────── -->
{#if successMsg}
  <Alert color="green" class="mb-4">{successMsg}</Alert>
{/if}
{#if errorMsg}
  <Alert color="red" class="mb-4">{errorMsg}</Alert>
{/if}

<!-- ── Header row ────────────────────────────────────────────────────────────── -->
<div class="flex items-center justify-between mb-6">
  <div>
    <h1 class="text-2xl font-semibold text-gray-800 dark:text-gray-100">User Management</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage users and their privilege levels</p>
  </div>
  {#if isAtLeast('MAINTAINER')}
    <Button color="alternative" onclick={() => showAddModal = true}>
      <PlusOutline class="w-4 h-4 me-2" /> Add User
    </Button>
  {/if}
</div>

<!-- ── User table ────────────────────────────────────────────────────────────── -->
{#if loading}
  <div class="flex justify-center py-16"><Spinner size="10" /></div>
{:else}
  <div class="rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
    <Table hoverable>
      <TableHead class="bg-gray-50 dark:bg-gray-800">
        <TableHeadCell>Username</TableHeadCell>
        <TableHeadCell>Privilege</TableHeadCell>
        <TableHeadCell class="text-right">Actions</TableHeadCell>
      </TableHead>
      <TableBody>
        {#each users as u (u.id)}
          <TableBodyRow class={u.id === currentUser?.id ? 'bg-sky-50 dark:bg-sky-950' : ''}>
            <TableBodyCell class="font-medium text-gray-800 dark:text-gray-200">
              {u.username}
              {#if u.id === currentUser?.id}
                <span class="ml-2 text-xs text-sky-500">(you)</span>
              {/if}
            </TableBodyCell>
            <TableBodyCell>
              <span class="px-2 py-1 rounded-full text-xs font-semibold {BADGE_COLOR[u.privilege]}">
                {u.privilege}
              </span>
            </TableBodyCell>
            <TableBodyCell class="text-right">
              <div class="flex justify-end gap-2">
                <!-- Change password -->
                {#if canChangePassword(u)}
                  <Button size="xs" color="alternative" onclick={() => {
                    passwordTarget = u;
                    newPasswordValue = ''; confirmPassword = '';
                    showPasswordModal = true;
                  }}>
                    <LockSolid class="w-3.5 h-3.5 me-1" /> Password
                  </Button>
                {/if}
                <!-- Edit privilege -->
                {#if canManage(u)}
                  <Button size="xs" color="alternative" onclick={() => {
                    editTarget = u;
                    editPrivilege = u.privilege;
                    showEditModal = true;
                  }}>
                    <EditOutline class="w-3.5 h-3.5 me-1" /> Edit
                  </Button>
                  <Button size="xs" color="red" onclick={() => {
                    deleteTarget = u;
                    showDeleteModal = true;
                  }}>
                    <TrashBinOutline class="w-3.5 h-3.5 me-1" /> Delete
                  </Button>
                {/if}
              </div>
            </TableBodyCell>
          </TableBodyRow>
        {/each}
      </TableBody>
    </Table>
  </div>
{/if}

<!-- ── Add User Modal ─────────────────────────────────────────────────────────── -->
<Modal title="Add User" bind:open={showAddModal} autoclose={false}>
  <div class="space-y-4">
    <div>
      <Label for="new-username" class="mb-1">Username</Label>
      <Input id="new-username" bind:value={newUsername} placeholder="Enter username" />
    </div>
    <div>
      <Label for="new-password" class="mb-1">Initial Password</Label>
      <Input id="new-password" type="password" bind:value={newPassword} placeholder="Enter password" />
    </div>
    <div>
      <Label for="new-privilege" class="mb-1">Privilege Level</Label>
      <Select id="new-privilege" bind:value={newPrivilege}>
        {#each assignablePrivileges() as p}
          <option value={p}>{p}</option>
        {/each}
      </Select>
    </div>
  </div>
  {#snippet footer()}
    <Button color="alternative" onclick={addUser}>Add User</Button>
    <Button color="light" onclick={() => showAddModal = false}>Cancel</Button>
  {/snippet}
</Modal>

<!-- ── Edit Privilege Modal ───────────────────────────────────────────────────── -->
<Modal title="Edit Privilege" bind:open={showEditModal} autoclose={false}>
  {#if editTarget}
    <div class="space-y-4">
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Changing privilege for <strong>{editTarget.username}</strong>
      </p>
      <div>
        <Label for="edit-privilege" class="mb-1">Privilege Level</Label>
        <Select id="edit-privilege" bind:value={editPrivilege}>
          {#each assignablePrivileges() as p}
            <option value={p}>{p}</option>
          {/each}
        </Select>
      </div>
    </div>
  {/if}
  {#snippet footer()}
    <Button color="alternative" onclick={savePrivilege}>Save</Button>
    <Button color="light" onclick={() => showEditModal = false}>Cancel</Button>
  {/snippet}
</Modal>

<!-- ── Delete Confirm Modal ───────────────────────────────────────────────────── -->
<Modal title="Delete User" bind:open={showDeleteModal} autoclose={false}>
  {#if deleteTarget}
    <p class="text-gray-700 dark:text-gray-300">
      Are you sure you want to delete <strong>{deleteTarget.username}</strong>? This cannot be undone.
    </p>
  {/if}
  {#snippet footer()}
    <Button color="red" onclick={deleteUser}>Delete</Button>
    <Button color="light" onclick={() => showDeleteModal = false}>Cancel</Button>
  {/snippet}
</Modal>

<!-- ── Change Password Modal ──────────────────────────────────────────────────── -->
<Modal title="Change Password" bind:open={showPasswordModal} autoclose={false}>
  {#if passwordTarget}
    <div class="space-y-4">
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {passwordTarget.id === currentUser?.id ? 'Change your password' : `Set new password for ${passwordTarget.username}`}
      </p>
      <div>
        <Label for="new-pw" class="mb-1">New Password</Label>
        <Input id="new-pw" type="password" bind:value={newPasswordValue} placeholder="Min. 6 characters" />
      </div>
      <div>
        <Label for="confirm-pw" class="mb-1">Confirm Password</Label>
        <Input id="confirm-pw" type="password" bind:value={confirmPassword} placeholder="Repeat password" />
      </div>
    </div>
  {/if}
  {#snippet footer()}
    <Button color="alternative" onclick={changePassword}>Update Password</Button>
    <Button color="light" onclick={() => showPasswordModal = false}>Cancel</Button>
  {/snippet}
</Modal>
