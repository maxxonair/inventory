<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth.js';
  import { get } from 'svelte/store';
  import {
    Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell,
    Button, Modal, Label, Input, Spinner, Alert
  } from 'flowbite-svelte';
  import {
    PlusOutline, TrashBinOutline, EditOutline
  } from 'flowbite-svelte-icons';
  import {PRIVILEGE_ORDER, type Privilege, privilegeFromId} from '../settings.svelte';

  // ── Types ──────────────────────────────────────────────────────────────────

  interface AppUser {
    id: number;
    username: string;
    privilege: Privilege;
  }

  interface ItemType {
    id: number;
    name: string;
  }

  // ── State ──────────────────────────────────────────────────────────────────

  // The auth store may hold the raw DB integer for privilege, so normalise it
  // immediately so that isAtLeast() works before fetchItemTypes() is called.
  function normaliseUser(raw: any): AppUser | null {
    if (!raw) return null;
    const priv = raw.privilege ?? raw.user_privileges;
    return {
      id: raw.id,
      username: raw.username,
      privilege: typeof priv === 'number' ? privilegeFromId(priv) : priv as Privilege,
    };
  }

  let currentUser = $state(normaliseUser(get(user)));
  let itemTypes   = $state<ItemType[]>([]);
  let loading     = $state(true);
  let errorMsg    = $state('');
  let successMsg  = $state('');

  // Modals
  let showAddModal    = $state(false);
  let showEditModal    = $state(false);
  let showDeleteModal = $state(false);

  // Add item type form
  let newName = $state('');

  // Edit item type
  let editTarget = $state<ItemType | null>(null);
  let editName   = $state('');

  // Delete item type
  let deleteTarget = $state<ItemType | null>(null);

  // ── Helpers ────────────────────────────────────────────────────────────────

  function rank(p: Privilege) {
    return PRIVILEGE_ORDER.indexOf(p);
  }

  function isAtLeast(p: Privilege) {
    return currentUser ? rank(currentUser.privilege) >= rank(p) : false;
  }

  function flash(type: 'success' | 'error', msg: string) {
    if (type === 'success') { successMsg = msg; setTimeout(() => successMsg = '', 3000); }
    else                    { errorMsg   = msg; setTimeout(() => errorMsg   = '', 4000); }
  }

  async function parseErrorBody(res: Response, fallback: string): Promise<string> {
    const body = await res.json().catch(() => ({}) as any);
    // Backend (FastAPI HTTPException) responds with { detail }
    return body.detail || body.error || fallback;
  }

  // ── API calls ──────────────────────────────────────────────────────────────

  async function fetchItemTypes() {
    loading = true;
    try {
      const res = await fetch('/api/item_types', { credentials: 'include' });
      if (res.status === 401) {goto('/login');}
      if (!res.ok) throw new Error('Failed to load item types');
      itemTypes = await res.json();
    } catch (e: any) {
      flash('error', e.message);
    } finally {
      loading = false;
    }
  }

  async function addItemType() {
    if (!newName.trim()) return;
    try {
      const res = await fetch('/api/add_item_type', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName.trim() }),
      });
      if (res.status === 401) {goto('/login');}
      if (!res.ok) throw new Error(await parseErrorBody(res, 'Failed to add item type'));
      flash('success', `Item type "${newName.trim()}" added.`);
      showAddModal = false;
      newName = '';
      await fetchItemTypes();
    } catch (e: any) { flash('error', e.message); }
  }

  async function saveItemType() {
    if (!editTarget || !editName.trim()) return;
    try {
      const res = await fetch('/api/update_item_type', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: editTarget.id, name: editName.trim() }),
      });
      if (res.status === 401) {goto('/login');}
      if (!res.ok) throw new Error(await parseErrorBody(res, 'Failed to update item type'));
      flash('success', `Item type renamed to "${editName.trim()}".`);
      showEditModal = false;
      await fetchItemTypes();
    } catch (e: any) { flash('error', e.message); }
  }

  async function deleteItemType() {
    if (!deleteTarget) return;
    try {
      const res = await fetch('/api/delete_item_type', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: deleteTarget.id }),
      });
      if (res.status === 401) {goto('/login');}
      if (!res.ok) throw new Error(await parseErrorBody(res, 'Failed to delete item type'));
      flash('success', `Item type "${deleteTarget.name}" deleted.`);
      showDeleteModal = false;
      await fetchItemTypes();
    } catch (e: any) { flash('error', e.message); }
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  onMount(() => {
    if (!currentUser || !isAtLeast('MAINTAINER')) {
      goto('/');
      return;
    }
    fetchItemTypes();
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
    <h1 class="text-2xl font-semibold text-gray-800 dark:text-gray-100">Item Types</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage the list of item type categories available in the inventory</p>
  </div>
  {#if isAtLeast('MAINTAINER')}
    <Button color="primary" onclick={() => showAddModal = true}>
      <PlusOutline class="w-4 h-4 me-2" /> Add Item Type
    </Button>
  {/if}
</div>

<!-- ── Item type table ───────────────────────────────────────────────────────── -->
{#if loading}
  <div class="flex justify-center py-16"><Spinner size="10" /></div>
{:else}
  <div class="rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
    <Table hoverable>
      <TableHead class="bg-gray-50 dark:bg-gray-800">
        <TableHeadCell>Name</TableHeadCell>
        <TableHeadCell class="text-right">Actions</TableHeadCell>
      </TableHead>
      <TableBody>
        {#each itemTypes as t (t.id)}
          <TableBodyRow>
            <TableBodyCell class="font-medium text-gray-800 dark:text-gray-200">
              {t.name}
            </TableBodyCell>
            <TableBodyCell class="text-right">
              <div class="flex justify-end gap-2">
                {#if isAtLeast('MAINTAINER')}
                  <Button size="xs" color="alternative" onclick={() => {
                    editTarget = t;
                    editName = t.name;
                    showEditModal = true;
                  }}>
                    <EditOutline class="w-3.5 h-3.5 me-1" /> Edit
                  </Button>
                  <Button size="xs" color="red" onclick={() => {
                    deleteTarget = t;
                    showDeleteModal = true;
                  }}>
                    <TrashBinOutline class="w-3.5 h-3.5 me-1" /> Delete
                  </Button>
                {/if}
              </div>
            </TableBodyCell>
          </TableBodyRow>
        {/each}
        {#if itemTypes.length === 0}
          <TableBodyRow>
            <TableBodyCell colspan={2} class="text-center text-gray-500 dark:text-gray-400 py-8">
              No item types defined yet.
            </TableBodyCell>
          </TableBodyRow>
        {/if}
      </TableBody>
    </Table>
  </div>
{/if}

<!-- ── Add Item Type Modal ─────────────────────────────────────────────────────── -->
<Modal title="Add Item Type" bind:open={showAddModal} autoclose={false} outsideclose={false}>
  <div class="space-y-4">
    <div>
      <Label for="new-item-type-name" class="mb-1">Name</Label>
      <Input id="new-item-type-name" bind:value={newName} placeholder="e.g. Cable" />
    </div>
  </div>
  {#snippet footer()}
    <Button color="primary" onclick={addItemType}>Add Item Type</Button>
    <Button color="light" onclick={() => { showAddModal = false; newName = ''; }}>Cancel</Button>
  {/snippet}
</Modal>

<!-- ── Edit Item Type Modal ───────────────────────────────────────────────────── -->
<Modal title="Edit Item Type" bind:open={showEditModal} autoclose={false} outsideclose={false}>
  {#if editTarget}
    <div class="space-y-4">
      <Label for="edit-item-type-name" class="mb-1">Name</Label>
      <Input id="edit-item-type-name" bind:value={editName} placeholder="e.g. Cable" />
    </div>
  {/if}
  {#snippet footer()}
    <Button color="primary" onclick={saveItemType}>Save</Button>
    <Button color="light" onclick={() => showEditModal = false}>Cancel</Button>
  {/snippet}
</Modal>

<!-- ── Delete Confirm Modal ───────────────────────────────────────────────────── -->
<Modal title="Delete Item Type" bind:open={showDeleteModal} autoclose={false} outsideclose={false}>
  {#if deleteTarget}
    <p class="text-gray-700 dark:text-gray-300">
      Are you sure you want to delete <strong>{deleteTarget.name}</strong>? This cannot be undone.
    </p>
  {/if}
  {#snippet footer()}
    <Button color="red" onclick={deleteItemType}>Delete</Button>
    <Button color="light" onclick={() => showDeleteModal = false}>Cancel</Button>
  {/snippet}
</Modal>