import { redirect } from "@sveltejs/kit";
const prerender = true;
async function load({ fetch }) {
  const res = await fetch("http://localhost:5000/me", {
    credentials: "include"
  });
  if (!res.ok) {
    throw redirect(302, "/login");
  }
  const response = await res.json();
  const user = response;
  return { user };
}
export {
  load,
  prerender
};
