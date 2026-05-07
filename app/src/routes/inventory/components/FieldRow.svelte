<script lang="ts">
  import type { Snippet } from 'svelte';

  let { label, editing, editSlot, viewSlot }: {
    label: string;
    editing: boolean;
    editSlot: Snippet;
    viewSlot: Snippet;
  } = $props();
</script>

<div>
  <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">{label}</p>
  {#if editing}
    {@render editSlot()}
  {:else}
    <div class="text-sm text-gray-800 dark:text-gray-200">
      {@render viewSlot()}
    </div>
  {/if}
</div>