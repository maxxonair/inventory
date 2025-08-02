<script>import Header from "./Header.svelte";
import Toast from "$lib/Toast.svelte";
import { onMount } from "svelte";
import { fetchUser } from "$lib/stores/auth.js";
import "../app.css";

let { children } = $props();
onMount(fetchUser);</script>

<div class="app">
  <Header></Header>

  <main>
    {@render children()}
  </main>

  <!-- <Toast></Toast> -->

</div>

