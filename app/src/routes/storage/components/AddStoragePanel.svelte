<script lang="ts">


  let { 
    onAdd, 
    onCancel = () => {}
  } = $props();
  
  // --- Form State ---
  let name = $state("");
  let description = $state("");

</script>

<div class="p-4 bg-yellow-100 text-yellow-800 rounded">
  Storage location management coming soon!
</div>
