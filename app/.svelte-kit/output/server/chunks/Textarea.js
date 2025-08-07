import { A as push, I as attr_class, G as clsx, F as spread_attributes, M as escape_html, R as bind_props, D as pop } from "./index2.js";
import clsx$1 from "clsx";
import { g as getTheme, j as textarea } from "./theme.js";
import { c as createDismissableContext, C as CloseButton } from "./CloseButton.js";
function Textarea($$payload, $$props) {
  push();
  let {
    header,
    footer,
    addon,
    value = void 0,
    elementRef = void 0,
    divClass,
    innerClass,
    headerClass,
    footerClass,
    addonClass,
    disabled,
    class: className,
    classes,
    clearable,
    clearableSvgClass,
    clearableColor = "none",
    clearableClass,
    clearableOnClick,
    textareaClass,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? {
    div: divClass,
    inner: innerClass,
    header: headerClass,
    footer: footerClass,
    addon: addonClass,
    close: clearableClass,
    svg: clearableSvgClass
  };
  const theme = getTheme("textarea");
  let hasHeader = !!header;
  let hasFooter = !!footer;
  let hasAddon = !!addon;
  let wrapped = hasHeader || hasFooter || hasAddon;
  const {
    div,
    base,
    wrapper,
    inner,
    header: headerCls,
    footer: footerCls,
    addon: addonCls,
    close
  } = textarea({ wrapped, hasHeader, hasFooter });
  const clearAll = () => {
    if (elementRef) {
      elementRef.value = "";
      value = void 0;
    }
    if (clearableOnClick) clearableOnClick();
  };
  createDismissableContext(clearAll);
  $$payload.out.push(`<div${attr_class(clsx(div({ class: clsx$1(theme?.div, styling.div) })))}>`);
  if (!wrapped) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<textarea${spread_attributes(
      {
        disabled,
        ...restProps,
        class: clsx(wrapper({ class: clsx$1(className, classes?.wrapper) }))
      },
      null
    )}>`);
    const $$body = escape_html(value);
    if ($$body) {
      $$payload.out.push(`${$$body}`);
    }
    $$payload.out.push(`</textarea>`);
  } else {
    $$payload.out.push("<!--[!-->");
    $$payload.out.push(`<div${attr_class(clsx(wrapper({ class: clsx$1(theme?.wrapper, classes?.wrapper) })))}>`);
    if (header) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<div${attr_class(clsx(headerCls({ class: clsx$1(theme?.header, styling.header) })))}>`);
      header($$payload);
      $$payload.out.push(`<!----></div>`);
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--> <div${attr_class(clsx(inner({ class: clsx$1(theme?.inner, styling.inner) })))}>`);
    if (addon) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<div${attr_class(clsx(addonCls({ class: clsx$1(theme?.addon, styling.addon) })))}>`);
      addon($$payload);
      $$payload.out.push(`<!----></div>`);
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--> <textarea${spread_attributes(
      {
        disabled,
        ...restProps,
        class: clsx(base({ class: clsx$1(theme?.base, className) }))
      },
      null
    )}>`);
    const $$body_1 = escape_html(value);
    if ($$body_1) {
      $$payload.out.push(`${$$body_1}`);
    }
    $$payload.out.push(`</textarea></div> `);
    if (footer) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<div${attr_class(clsx(footerCls({ class: clsx$1(theme?.footer, styling.footer) })))}>`);
      footer($$payload);
      $$payload.out.push(`<!----></div>`);
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--></div>`);
  }
  $$payload.out.push(`<!--]--> `);
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
  $$payload.out.push(`<!--]--></div>`);
  bind_props($$props, { value, elementRef });
  pop();
}
export {
  Textarea as T
};
