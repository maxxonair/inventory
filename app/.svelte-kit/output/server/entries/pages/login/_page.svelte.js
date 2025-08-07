import { A as push, I as attr_class, F as spread_attributes, G as clsx, K as attr, R as bind_props, D as pop, P as copy_payload, Q as assign_payload, E as head } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import clsx$1 from "clsx";
import "../../../chunks/state.svelte.js";
import { g as getTheme, k as floatingLabelInput } from "../../../chunks/theme.js";
import { B as Button } from "../../../chunks/Button.js";
import { c as createDismissableContext, C as CloseButton } from "../../../chunks/CloseButton.js";
let n = Date.now();
function idGenerator() {
  return (++n).toString(36);
}
function FloatingLabelInput($$payload, $$props) {
  push();
  let {
    children,
    id = idGenerator(),
    value = void 0,
    elementRef = void 0,
    variant = "standard",
    size = "default",
    color = "default",
    class: className,
    classes,
    inputClass,
    labelClass,
    clearable,
    clearableSvgClass,
    clearableColor = "none",
    clearableClass,
    clearableOnClick,
    data = [],
    maxSuggestions = 5,
    onSelect,
    comboClass,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? {
    input: inputClass,
    label: labelClass,
    svg: clearableSvgClass,
    close: clearableClass
  };
  const theme = getTheme("floatingLabelInput");
  const { base, input, label, close, combo } = floatingLabelInput({ variant, size, color });
  const clearAll = () => {
    if (elementRef) {
      elementRef.value = "";
      value = "";
      setTimeout(
        () => {
          elementRef?.focus();
        },
        100
      );
    }
    if (clearableOnClick) clearableOnClick();
  };
  const isCombobox = Array.isArray(data) && data.length > 0;
  createDismissableContext(clearAll);
  if (clearable) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<div tabindex="-1" class="sr-only"></div>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--> <div${attr_class(clsx(base({
    class: clsx$1(isCombobox ? "relative" : "", theme?.base, className)
  })))}><input${spread_attributes(
    {
      id,
      placeholder: " ",
      value,
      ...restProps,
      class: clsx(input({ class: clsx$1(theme?.input, styling.input) }))
    },
    null
  )}/> `);
  if (value !== void 0 && value !== "" && clearable) {
    $$payload.out.push("<!--[-->");
    CloseButton($$payload, {
      class: close({ class: clsx$1(theme?.close, styling.close) }),
      color: clearableColor,
      "aria-label": "Clear search value",
      svgClass: clsx$1(styling.svg)
    });
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--> <label${attr("for", id)}${attr_class(clsx(label({ class: clsx$1(theme?.label, styling.label) })))}>`);
  children($$payload);
  $$payload.out.push(`<!----></label> `);
  {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></div>`);
  bind_props($$props, { value, elementRef });
  pop();
}
function _page($$payload, $$props) {
  push();
  let username = "";
  let password = "";
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    head($$payload2, ($$payload3) => {
      $$payload3.title = `<title>Inventory Login</title>`;
      $$payload3.out.push(`<meta name="description" content="Inventory Login page"/>`);
    });
    $$payload2.out.push(`<div class="flex items-center justify-center min-h-screen bg-gray-100 w-screen h-screen dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"><form class="max-w-sm mx-auto"><div class="mb-5 flex items-center justify-center"><label for="login" class="block mb-2 text-xl text-gray-900 dark:text-gray-200">Inventory Login</label></div> <div class="mb-5">`);
    FloatingLabelInput($$payload2, {
      clearable: true,
      variant: "outlined",
      id: "user",
      name: "user",
      type: "text",
      class: "bg-white dark:bg-slate-900 rounded-lg",
      required: true,
      get value() {
        return username;
      },
      set value($$value) {
        username = $$value;
        $$settled = false;
      },
      children: ($$payload3) => {
        $$payload3.out.push(`<!---->Name`);
      },
      $$slots: { default: true }
    });
    $$payload2.out.push(`<!----></div> <div class="mb-5">`);
    FloatingLabelInput($$payload2, {
      clearable: true,
      variant: "outlined",
      id: "password",
      name: "password",
      type: "password",
      required: true,
      class: "bg-white dark:bg-slate-900 rounded-lg",
      get value() {
        return password;
      },
      set value($$value) {
        password = $$value;
        $$settled = false;
      },
      children: ($$payload3) => {
        $$payload3.out.push(`<!---->Password`);
      },
      $$slots: { default: true }
    });
    $$payload2.out.push(`<!----></div> `);
    Button($$payload2, {
      type: "submit",
      class: " w-full",
      children: ($$payload3) => {
        $$payload3.out.push(`<!---->Login`);
      },
      $$slots: { default: true }
    });
    $$payload2.out.push(`<!----></form></div>`);
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
