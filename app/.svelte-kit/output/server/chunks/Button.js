import { J as getContext, F as spread_attributes, G as clsx$1, X as element, D as pop, A as push } from "./index2.js";
import clsx from "clsx";
import { g as getTheme, m as button } from "./theme.js";
function Button($$payload, $$props) {
  push();
  const group = getContext("group");
  const ctxDisabled = getContext("disabled");
  let {
    children,
    pill,
    outline = false,
    size = "md",
    color,
    shadow = false,
    tag = "button",
    disabled,
    loading = false,
    class: className,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const theme = getTheme("button");
  let actualSize = group ? "sm" : size;
  let actualColor = color ?? (group ? outline ? "dark" : "alternative" : "primary");
  let isDisabled = Boolean(ctxDisabled) || Boolean(disabled) || loading;
  const { base, outline: outline_, shadow: shadow_ } = button({
    color: actualColor,
    size: actualSize,
    disabled: isDisabled,
    pill,
    group: !!group
  });
  let btnCls = base({
    class: clsx(outline && outline_(), shadow && shadow_(), theme?.base, className)
  });
  if (restProps.href === void 0) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<button${spread_attributes(
      {
        type: "button",
        ...restProps,
        class: clsx$1(btnCls),
        disabled: isDisabled
      },
      null
    )}>`);
    children?.($$payload);
    $$payload.out.push(`<!----> `);
    if (loading) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<svg class="ml-2 h-4 w-4 animate-spin text-white" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>`);
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--></button>`);
  } else {
    $$payload.out.push("<!--[!-->");
    if (restProps.href) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<a${spread_attributes({ ...restProps, class: clsx$1(btnCls), role: "button" }, null)}>`);
      children?.($$payload);
      $$payload.out.push(`<!----></a>`);
    } else {
      $$payload.out.push("<!--[!-->");
      element(
        $$payload,
        tag,
        () => {
          $$payload.out.push(`${spread_attributes({ ...restProps, class: clsx$1(btnCls) }, null)}`);
        },
        () => {
          children?.($$payload);
          $$payload.out.push(`<!---->`);
        }
      );
    }
    $$payload.out.push(`<!--]-->`);
  }
  $$payload.out.push(`<!--]-->`);
  pop();
}
export {
  Button as B
};
