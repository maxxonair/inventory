import { B as setContext, J as getContext, A as push, F as spread_attributes, G as clsx, M as escape_html, I as attr_class, D as pop } from "./index2.js";
import clsx$1 from "clsx";
import { n as closeButton } from "./theme.js";
const DISMISSABLE_KEY = Symbol("dismissable");
function createDismissableContext(onDismiss) {
  const context = { dismiss: onDismiss };
  return setContext(DISMISSABLE_KEY, context);
}
function useDismiss() {
  const context = getContext(DISMISSABLE_KEY);
  return context;
}
function CloseButton($$payload, $$props) {
  push();
  let {
    children,
    color = "gray",
    onclick: onclickorg,
    name = "Close",
    ariaLabel,
    size = "md",
    class: className,
    svgClass,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const { base, svg } = closeButton({ color, size });
  useDismiss();
  if (restProps.href === void 0) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<button${spread_attributes(
      {
        type: "button",
        ...restProps,
        class: clsx(base({ class: clsx$1(className) })),
        "aria-label": ariaLabel ?? name
      },
      null
    )}>`);
    if (name) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<span class="sr-only">${escape_html(name)}</span>`);
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--> `);
    if (children) {
      $$payload.out.push("<!--[-->");
      children($$payload);
      $$payload.out.push(`<!---->`);
    } else {
      $$payload.out.push("<!--[!-->");
      $$payload.out.push(`<svg${attr_class(clsx(svg({ class: svgClass })))} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>`);
    }
    $$payload.out.push(`<!--]--></button>`);
  } else {
    $$payload.out.push("<!--[!-->");
    $$payload.out.push(`<a${spread_attributes(
      {
        ...restProps,
        class: clsx(base({ class: clsx$1(className) })),
        "aria-label": ariaLabel ?? name
      },
      null
    )}>`);
    if (name) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<span class="sr-only">${escape_html(name)}</span>`);
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--> `);
    if (children) {
      $$payload.out.push("<!--[-->");
      children($$payload);
      $$payload.out.push(`<!---->`);
    } else {
      $$payload.out.push("<!--[!-->");
      $$payload.out.push(`<svg${attr_class(clsx(svg()))} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>`);
    }
    $$payload.out.push(`<!--]--></a>`);
  }
  $$payload.out.push(`<!--]-->`);
  pop();
}
export {
  CloseButton as C,
  createDismissableContext as c
};
