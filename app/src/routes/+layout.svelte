<script>
import Header from "./Header.svelte";
import { onMount } from "svelte";
import { fetchUser } from "$lib/stores/auth.js";
import "../app.css";

let { children } = $props();
onMount(fetchUser);
</script>

<div class="flex flex-col min-h-screen overflow-x-hidden">
  <Header></Header>

<main class="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900 px-2 sm:px-4 md:px-6 lg:px-8">
    {@render children()}
  </main>
</div>

