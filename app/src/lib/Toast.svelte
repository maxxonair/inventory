<script>
  import { message } from '$lib/stores/auth.js';
  let timeout;

  $: if ($message) {
    clearTimeout(timeout);
    timeout = setTimeout(() => message.set(null), 3000);
  }
</script>

{#if $message}
  <div class="toast">{$message}</div>
{/if}

<style>
  .toast {
    position: fixed;
    top: 1rem;
    right: 1rem;
    background: #333;
    color: white;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    animation: fadein 0.3s ease;
  }

  @keyframes fadein {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
