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

  <Toast></Toast>

  <!-- <footer>

	</footer> -->
</div>


<!-- <style>
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: #303030;
  }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 1rem;
    width: 100%;
    max-width: 64rem;
    margin: 0 auto;
    box-sizing: border-box;
  }

  /* footer {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 12px;
  }

  footer a {
    font-weight: bold;
  }

  @media (min-width: 480px) {
    footer {
      padding: 12px 0;
    }
  } */
</style> -->
