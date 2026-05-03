<script lang="ts">
  import { Button, ButtonGroup } from "flowbite-svelte";
  import { ChevronLeftOutline, ChevronRightOutline } from "flowbite-svelte-icons";

  let { 
    totalItems, 
    itemsPerPage = 50, 
    currentPosition = $bindable(0), 
    showPage = 5 
  } = $props();

  // Reactive calculations (Runes)
  let totalPages = $derived(Math.ceil(totalItems / itemsPerPage));
  let currentPage = $derived(Math.floor(currentPosition / itemsPerPage) + 1);

  let startRange = $derived(currentPosition + 1);
  let endRange = $derived(Math.min(currentPosition + itemsPerPage, totalItems));

  // Calculate which page numbers to display
  let pagesToShow = $derived.by(() => {
    let start = Math.max(1, currentPage - Math.floor(showPage / 2));
    let end = Math.min(start + showPage - 1, totalPages);
    
    // Adjust start if we are near the end of the list
    if (end - start + 1 < showPage) {
      start = Math.max(1, end - showPage + 1);
    }

    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  });

  // Navigation handlers
  const goToPage = (pageNumber: number) => {
    currentPosition = (pageNumber - 1) * itemsPerPage;
  };

  const next = () => {
    if (currentPage < totalPages) currentPosition += itemsPerPage;
  };

  const prev = () => {
    if (currentPage > 1) currentPosition -= itemsPerPage;
  };
</script>

<div class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0" aria-label="Table navigation">
  <!-- Status Text -->
  <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
    Showing
    <span class="font-semibold text-gray-900 dark:text-white">{startRange}-{endRange}</span>
    of
    <span class="font-semibold text-gray-900 dark:text-white">{totalItems}</span>
  </span>

  <!-- Page Buttons -->
  <ButtonGroup>
    <Button onclick={prev} disabled={currentPage === 1}>
      <ChevronLeftOutline size="xs" class="m-1.5" />
    </Button>

    {#each pagesToShow as pageNumber}
      <Button 
        color={currentPage === pageNumber ? 'primary' : 'alternative'}
        onclick={() => goToPage(pageNumber)}
      >
        {pageNumber}
      </Button>
    {/each}

    <Button onclick={next} disabled={currentPage === totalPages}>
      <ChevronRightOutline size="xs" class="m-1.5" />
    </Button>
  </ButtonGroup>
</div>