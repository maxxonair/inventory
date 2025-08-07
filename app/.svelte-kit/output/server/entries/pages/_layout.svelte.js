import clsx$1 from "clsx";
import { E as head, F as spread_attributes, G as clsx, I as attr_class, D as pop, A as push, J as getContext, K as attr, M as escape_html, N as store_get, O as unsubscribe_stores } from "../../chunks/index2.js";
import { p as page } from "../../chunks/index3.js";
import { w as writable } from "../../chunks/index.js";
import { g as goto } from "../../chunks/client.js";
import { g as getTheme, d as darkmode } from "../../chunks/theme.js";
import { B as Button } from "../../chunks/Button.js";
import { twMerge } from "tailwind-merge";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/state.svelte.js";
const user = writable(null);
const message = writable(null);
async function logout() {
  await fetch("http://localhost:5000/logout", {
    method: "POST",
    credentials: "include"
  });
  user.set(null);
  message.set("Logged out");
  goto();
}
function DarkMode($$payload, $$props) {
  push();
  let {
    class: className,
    lightIcon,
    darkIcon,
    size = "md",
    ariaLabel = "Dark mode",
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const theme = getTheme("darkmode");
  const sizes = { sm: "w-4 h-4", md: "w-5 h-5", lg: "w-6 h-6" };
  head($$payload, ($$payload2) => {
    $$payload2.out.push(`<script>
    if ("THEME_PREFERENCE_KEY" in localStorage) {
      localStorage.getItem("THEME_PREFERENCE_KEY") === "dark" ? window.document.documentElement.classList.add("dark") : window.document.documentElement.classList.remove("dark");
    } else {
      if (window.matchMedia("(prefers-color-scheme: dark)").matches) window.document.documentElement.classList.add("dark");
    }
  <\/script><!---->`);
  });
  $$payload.out.push(`<button${spread_attributes(
    {
      "aria-label": ariaLabel,
      type: "button",
      ...restProps,
      class: clsx(darkmode({ class: clsx$1(theme, className) })),
      tabindex: 0
    },
    null
  )}><span class="hidden dark:block">`);
  if (lightIcon) {
    $$payload.out.push("<!--[-->");
    lightIcon($$payload);
    $$payload.out.push(`<!---->`);
  } else {
    $$payload.out.push("<!--[!-->");
    $$payload.out.push(`<svg role="img" aria-label="Light mode"${attr_class(clsx(sizes[size]))} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1
    0 100-2H3a1 1 0 000 2h1z" fill-rule="evenodd" clip-rule="evenodd"></path></svg>`);
  }
  $$payload.out.push(`<!--]--></span> <span class="block dark:hidden">`);
  if (darkIcon) {
    $$payload.out.push("<!--[-->");
    darkIcon($$payload);
    $$payload.out.push(`<!---->`);
  } else {
    $$payload.out.push("<!--[!-->");
    $$payload.out.push(`<svg role="img" aria-label="Dark mode"${attr_class(clsx(sizes[size]))} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path></svg>`);
  }
  $$payload.out.push(`<!--]--></span></button>`);
  pop();
}
function ArrowLeftToBracketOutline($$payload, $$props) {
  push();
  const ctx = getContext("iconCtx") ?? {};
  const sizes = {
    xs: "w-3 h-3",
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
    xl: "w-8 h-8"
  };
  let {
    size = ctx.size || "md",
    color = ctx.color || "currentColor",
    title,
    strokeWidth = ctx.strokeWidth || "2",
    desc,
    class: className,
    ariaLabel = "arrow left to bracket outline",
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  let ariaDescribedby = `${title?.id || ""} ${desc?.id || ""}`;
  const hasDescription = !!(title?.id || desc?.id);
  $$payload.out.push(`<svg${spread_attributes(
    {
      xmlns: "http://www.w3.org/2000/svg",
      fill: "none",
      color,
      ...restProps,
      class: clsx(twMerge(clsx$1("shrink-0", sizes[size], className))),
      "aria-label": ariaLabel,
      "aria-describedby": hasDescription ? ariaDescribedby : void 0,
      viewBox: "0 0 24 24"
    },
    null,
    void 0,
    void 0,
    3
  )}>`);
  if (title?.id && title.title) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<title${attr("id", title.id)}>${escape_html(title.title)}</title>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  if (desc?.id && desc.desc) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<desc${attr("id", desc.id)}>${escape_html(desc.desc)}</desc>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M16 12H4m12 0-4 4m4-4-4-4m3-4h2a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3h-2"></path></svg>`);
  pop();
}
function HomeSolid($$payload, $$props) {
  push();
  const ctx = getContext("iconCtx") ?? {};
  const sizes = {
    xs: "w-3 h-3",
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
    xl: "w-8 h-8"
  };
  let {
    size = ctx.size || "md",
    color = ctx.color || "currentColor",
    title,
    desc,
    class: className,
    ariaLabel = "home solid",
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  let ariaDescribedby = `${title?.id || ""} ${desc?.id || ""}`;
  const hasDescription = !!(title?.id || desc?.id);
  $$payload.out.push(`<svg${spread_attributes(
    {
      xmlns: "http://www.w3.org/2000/svg",
      fill: color,
      ...restProps,
      class: clsx(twMerge(clsx$1("shrink-0", sizes[size], className))),
      "aria-label": ariaLabel,
      "aria-describedby": hasDescription ? ariaDescribedby : void 0,
      viewBox: "0 0 24 24"
    },
    null,
    void 0,
    void 0,
    3
  )}>`);
  if (title?.id && title.title) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<title${attr("id", title.id)}>${escape_html(title.title)}</title>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  if (desc?.id && desc.desc) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<desc${attr("id", desc.id)}>${escape_html(desc.desc)}</desc>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--><path fill-rule="evenodd" d="M11.293 3.293a1 1 0 0 1 1.414 0l6 6 2 2a1 1 0 0 1-1.414 1.414L19 12.414V19a2 2 0 0 1-2 2h-3a1 1 0 0 1-1-1v-3h-2v3a1 1 0 0 1-1 1H7a2 2 0 0 1-2-2v-6.586l-.293.293a1 1 0 0 1-1.414-1.414l2-2 6-6Z" clip-rule="evenodd"></path></svg>`);
  pop();
}
function OpenDoorOutline($$payload, $$props) {
  push();
  const ctx = getContext("iconCtx") ?? {};
  const sizes = {
    xs: "w-3 h-3",
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
    xl: "w-8 h-8"
  };
  let {
    size = ctx.size || "md",
    color = ctx.color || "currentColor",
    title,
    strokeWidth = ctx.strokeWidth || "2",
    desc,
    class: className,
    ariaLabel = "open door outline",
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  let ariaDescribedby = `${title?.id || ""} ${desc?.id || ""}`;
  const hasDescription = !!(title?.id || desc?.id);
  $$payload.out.push(`<svg${spread_attributes(
    {
      xmlns: "http://www.w3.org/2000/svg",
      fill: "none",
      color,
      ...restProps,
      class: clsx(twMerge(clsx$1("shrink-0", sizes[size], className))),
      "aria-label": ariaLabel,
      "aria-describedby": hasDescription ? ariaDescribedby : void 0,
      viewBox: "0 0 24 24"
    },
    null,
    void 0,
    void 0,
    3
  )}>`);
  if (title?.id && title.title) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<title${attr("id", title.id)}>${escape_html(title.title)}</title>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  if (desc?.id && desc.desc) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<desc${attr("id", desc.id)}>${escape_html(desc.desc)}</desc>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M18 18V6h-5v12h5Zm0 0h2M4 18h2.5m3.5-5.5V12M6 6l7-2v16l-7-2V6Z"></path></svg>`);
  pop();
}
function Header($$payload, $$props) {
  push();
  var $$store_subs;
  let isLoggedIn;
  if (!user) {
    goto();
  }
  function reloadPage() {
    window.location.reload();
  }
  function login() {
    goto();
  }
  isLoggedIn = store_get($$store_subs ??= {}, "$user", user) !== null;
  $$payload.out.push(`<header class="dark:bg-slate-900 bg-slate-100 svelte-4eb3dh"><div class="corner svelte-4eb3dh">`);
  DarkMode($$payload, {});
  $$payload.out.push(`<!----></div> <nav class="svelte-4eb3dh"><svg viewBox="0 0 2 3" aria-hidden="true" class="svelte-4eb3dh"><path d="M0,0 L1,2 C1.5,3 1.5,3 2,3 L2,0 Z" class="svelte-4eb3dh"></path></svg> <ul class="svelte-4eb3dh">`);
  if (isLoggedIn) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<li${attr("aria-current", page.url.pathname === "/" ? "home" : void 0)} class="svelte-4eb3dh"><button class="p-2! bg-slate-600 dark:bg-slate-800 text-red-500 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-gray-600 dark:text-red-600 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800">`);
    HomeSolid($$payload, { class: "h-6 w-6", onclick: reloadPage });
    $$payload.out.push(`<!----></button></li>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></ul> <svg viewBox="0 0 2 3" aria-hidden="true" class="svelte-4eb3dh"><path d="M0,0 L0,3 C0.5,3 0.5,3 1,2 L2,0 Z" class="svelte-4eb3dh"></path></svg></nav> <div class="corner svelte-4eb3dh">`);
  Button($$payload, {
    class: "p-2! md-2",
    onclick: isLoggedIn ? logout : login,
    "aria-label": isLoggedIn ? "Logout" : "Login",
    title: isLoggedIn ? "Log out" : "Log in",
    children: ($$payload2) => {
      if (isLoggedIn) {
        $$payload2.out.push("<!--[-->");
        OpenDoorOutline($$payload2, { class: "h-6 w-6" });
      } else {
        $$payload2.out.push("<!--[!-->");
        ArrowLeftToBracketOutline($$payload2, { class: "h-6 w-6" });
      }
      $$payload2.out.push(`<!--]-->`);
    },
    $$slots: { default: true }
  });
  $$payload.out.push(`<!----></div></header>`);
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
function _layout($$payload, $$props) {
  push();
  let { children } = $$props;
  $$payload.out.push(`<div class="flex flex-col min-h-screen">`);
  Header($$payload);
  $$payload.out.push(`<!----> <main class="flex bg-gray-50 dark:bg-gray-900 p-4">`);
  children($$payload);
  $$payload.out.push(`<!----></main></div>`);
  pop();
}
export {
  _layout as default
};
