import { M as escape_html, K as attr, D as pop, A as push } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/state.svelte.js";
function _page($$payload, $$props) {
  push();
  const { user } = $$props;
  const streamUrl = "http://localhost:5050";
  let error_msg = "";
  {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<div class="page-container svelte-b59ev0"><label for="id" class="label svelte-b59ev0">Place QR code in front of the scanner camera!</label> <label for="id" class="label svelte-b59ev0">${escape_html(error_msg)}</label> <img${attr("src", streamUrl)} alt="Camera Stream" class="camera-stream svelte-b59ev0"/></div>`);
  }
  $$payload.out.push(`<!--]-->`);
  pop();
}
export {
  _page as default
};
