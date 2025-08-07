import { redirect } from "@sveltejs/kit";
async function load({ fetch, url }) {
  if (url.pathname === "/login") return;
  const res = await fetch("http://localhost:5000/me", {
    credentials: "include"
  });
  if (!res.ok) {
    throw redirect(302, "/login");
  }
  const user = await res.json();
  return { user };
}
export {
  load
};
