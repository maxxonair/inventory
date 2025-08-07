import { d as dev } from "../../../../chunks/index4.js";
import { redirect } from "@sveltejs/kit";
const csr = dev;
const prerender = true;
async function load({ fetch }) {
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
  csr,
  load,
  prerender
};
