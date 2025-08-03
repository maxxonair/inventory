<script>
import Header from "./Header.svelte";
import { onMount } from "svelte";
import { fetchUser } from "$lib/stores/auth.js";
import "../app.css";

let { children } = $props();
onMount(fetchUser);
</script>

<div class="flex flex-col min-h-screen">
  <Header></Header>

  <main class="flex bg-gray-50 dark:bg-gray-900 p-4">
    {@render children()}
  </main>

</div>

