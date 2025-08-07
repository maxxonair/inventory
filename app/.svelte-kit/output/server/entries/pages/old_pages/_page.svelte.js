import { P as copy_payload, Q as assign_payload, D as pop, A as push, K as attr } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/state.svelte.js";
import "clsx";
import "../../../chunks/theme.js";
import { T as Textarea } from "../../../chunks/Textarea.js";
function _page($$payload, $$props) {
  push();
  const { user } = $$props;
  console.log(user);
  let name = "";
  let manufacturer = "";
  let details = "";
  let number_items = 1;
  let tags = "";
  let item_type = "";
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    $$payload2.out.push(`<h1 class="headline svelte-1mwir3m">Add New Item</h1> <div class="page-container svelte-1mwir3m"><form class="item-box svelte-1mwir3m">`);
    {
      $$payload2.out.push("<!--[!-->");
    }
    $$payload2.out.push(`<!--]--> `);
    {
      $$payload2.out.push("<!--[!-->");
    }
    $$payload2.out.push(`<!--]--> <input type="text" class="input-field svelte-1mwir3m" placeholder="Name"${attr("value", name)} required/> <input type="text" class="input-field svelte-1mwir3m" placeholder="Manufacturer"${attr("value", manufacturer)}/> <div class="input-text-field svelte-1mwir3m">`);
    Textarea($$payload2, {
      id: "textarea-id",
      class: "my-4 w-full",
      placeholder: "Details",
      rows: 4,
      name: "message",
      textareaClass: "input-text-field",
      get value() {
        return details;
      },
      set value($$value) {
        details = $$value;
        $$settled = false;
      }
    });
    $$payload2.out.push(`<!----></div> <input type="text" placeholder="Type" class="input-field svelte-1mwir3m"${attr("value", item_type)}/> <input type="text" placeholder="Tags" class="input-field svelte-1mwir3m"${attr("value", tags)}/> <label class="label svelte-1mwir3m" for="avatar">Number of items:</label> <input type="number" class="input-field svelte-1mwir3m" placeholder="Details"${attr("value", number_items)} required/> `);
    {
      $$payload2.out.push("<!--[!-->");
      {
        $$payload2.out.push("<!--[!-->");
        $$payload2.out.push(`<button class="toggle-camera-button svelte-1mwir3m">`);
        {
          $$payload2.out.push("<!--[!-->");
          $$payload2.out.push(`Open Camera`);
        }
        $$payload2.out.push(`<!--]--></button>`);
      }
      $$payload2.out.push(`<!--]--> <label class="label svelte-1mwir3m" for="avatar">Or load a picture from file:</label> <input class="upload-button svelte-1mwir3m" type="file" id="avatar" name="avatar" accept="image/png, image/jpeg"/> <button type="submit" class="add-button svelte-1mwir3m" title="Add item to the inventory">Add to Library</button>`);
    }
    $$payload2.out.push(`<!--]--></form></div>`);
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  pop();
}
export {
  _page as default
};
