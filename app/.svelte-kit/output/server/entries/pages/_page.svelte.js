import { A as push, B as setContext, F as spread_attributes, G as clsx$1, D as pop, P as copy_payload, Q as assign_payload, R as bind_props, S as spread_props, I as attr_class, T as attr_style, U as stringify, K as attr, V as ensure_array_like, M as escape_html, J as getContext, W as maybe_selected, X as element, Y as sanitize_props, Z as fallback, _ as slot, E as head } from "../../chunks/index2.js";
import "../../chunks/client.js";
import clsx from "clsx";
import { g as getTheme, b as buttonGroup, a as dropdown, c as dropdownGroup, e as drawer, t as tableSearch, f as checkbox, i as input, l as label, s as select, h as list } from "../../chunks/theme.js";
import { B as Button } from "../../chunks/Button.js";
import * as dom from "@floating-ui/dom";
import { c as createDismissableContext, C as CloseButton } from "../../chunks/CloseButton.js";
import { T as Textarea } from "../../chunks/Textarea.js";
import { twMerge } from "tailwind-merge";
const linear = (x) => x;
function cubic_out(t) {
  const f = t - 1;
  return f * f * f + 1;
}
function split_css_unit(value) {
  const split = typeof value === "string" && value.match(/^\s*(-?[\d.]+)([^\s]*)\s*$/);
  return split ? [parseFloat(split[1]), split[2] || "px"] : [
    /** @type {number} */
    value,
    "px"
  ];
}
function fade(node, { delay = 0, duration = 400, easing = linear } = {}) {
  const o = +getComputedStyle(node).opacity;
  return {
    delay,
    duration,
    easing,
    css: (t) => `opacity: ${t * o}`
  };
}
function fly(node, { delay = 0, duration = 400, easing = cubic_out, x = 0, y = 0, opacity = 0 } = {}) {
  const style = getComputedStyle(node);
  const target_opacity = +style.opacity;
  const transform = style.transform === "none" ? "" : style.transform;
  const od = target_opacity * (1 - opacity);
  const [x_value, x_unit] = split_css_unit(x);
  const [y_value, y_unit] = split_css_unit(y);
  return {
    delay,
    duration,
    easing,
    css: (t, u) => `
			transform: ${transform} translate(${(1 - t) * x_value}${x_unit}, ${(1 - t) * y_value}${y_unit});
			opacity: ${target_opacity - od * u}`
  };
}
function ButtonGroup($$payload, $$props) {
  push();
  let {
    children,
    size = "md",
    disabled,
    class: className,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const theme = getTheme("buttonGroup");
  let groupClass = buttonGroup({ size, class: clsx(theme, className) });
  setContext("group", size);
  setContext("disabled", disabled);
  $$payload.out.push(`<div${spread_attributes({ ...restProps, class: clsx$1(groupClass), role: "group" }, null)}>`);
  children($$payload);
  $$payload.out.push(`<!----></div>`);
  pop();
}
function Dropdown($$payload, $$props) {
  push();
  let {
    children,
    simple = false,
    placement = "bottom",
    offset = 2,
    class: className,
    activeUrl = "",
    isOpen = false,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const theme = getTheme("dropdown");
  const base = dropdown({ class: clsx(theme, className) });
  const activeUrlStore = { value: "" };
  setContext("activeUrl", activeUrlStore);
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    Popper($$payload2, spread_props([
      restProps,
      {
        placement,
        offset,
        class: base,
        get isOpen() {
          return isOpen;
        },
        set isOpen($$value) {
          isOpen = $$value;
          $$settled = false;
        },
        children: ($$payload3) => {
          if (simple) {
            $$payload3.out.push("<!--[-->");
            DropdownGroup($$payload3, {
              children: ($$payload4) => {
                children($$payload4);
                $$payload4.out.push(`<!---->`);
              },
              $$slots: { default: true }
            });
          } else {
            $$payload3.out.push("<!--[!-->");
            children($$payload3);
            $$payload3.out.push(`<!---->`);
          }
          $$payload3.out.push(`<!--]-->`);
        },
        $$slots: { default: true }
      }
    ]));
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  bind_props($$props, { isOpen });
  pop();
}
function DropdownGroup($$payload, $$props) {
  push();
  let { children, class: className, $$slots, $$events, ...restProps } = $$props;
  const theme = getTheme("dropdownGroup");
  $$payload.out.push(`<ul${spread_attributes(
    {
      ...restProps,
      class: clsx$1(dropdownGroup({ class: clsx(theme, className) }))
    },
    null
  )}>`);
  children($$payload);
  $$payload.out.push(`<!----></ul>`);
  pop();
}
function sineIn(t) {
  const v = Math.cos(t * Math.PI * 0.5);
  if (Math.abs(v) < 1e-14) return 1;
  else return 1 - v;
}
function Drawer($$payload, $$props) {
  push();
  let {
    children,
    hidden = void 0,
    activateClickOutside = true,
    position,
    width,
    backdrop = true,
    backdropClass,
    placement = "left",
    class: className,
    classes,
    transitionParams,
    transitionType = fly,
    bodyScrolling = false,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? { backdrop: backdropClass };
  const theme = getTheme("drawer");
  const { base, backdrop: backdropCls } = drawer({ position, placement, width, backdrop });
  let innerWidth = -1;
  let innerHeight = -1;
  let x = placement === "left" ? -320 : placement === "right" ? innerWidth + 320 : void 0;
  let y = placement === "top" ? -100 : placement === "bottom" ? innerHeight + 100 : void 0;
  Object.assign({}, { x, y, duration: 200, easing: sineIn });
  function close(ev) {
  }
  createDismissableContext(close);
  if (!hidden) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<div role="presentation"${attr_class(clsx$1(backdropCls({ class: clsx(theme?.backdrop, styling.backdrop) })))}${attr_style(bodyScrolling ? "pointer-events: none;" : "")}></div> <div${spread_attributes(
      {
        ...restProps,
        class: clsx$1(base({ class: clsx(theme?.base, className) })),
        tabindex: "-1"
      },
      null
    )}>`);
    children?.($$payload);
    $$payload.out.push(`<!----></div>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  bind_props($$props, { hidden });
  pop();
}
function Arrow($$payload, $$props) {
  push();
  let {
    placement = "top",
    cords,
    strategy = "absolute",
    class: className = ""
  } = $$props;
  $$payload.out.push(`<div${attr_class(`popover-arrow clip pointer-events-none block h-[10px] w-[10px] border-b border-l border-inherit bg-inherit text-inherit ${stringify(className)}`)}></div>`);
  pop();
}
function Popper($$payload, $$props) {
  push();
  let {
    triggeredBy,
    triggerDelay = 200,
    trigger = "click",
    placement = "top",
    offset = 8,
    arrow = false,
    yOnly = false,
    strategy = "absolute",
    reference,
    middlewares = [dom.flip(), dom.shift()],
    onbeforetoggle: _onbeforetoggle,
    ontoggle: _ontoggle,
    class: className = "",
    arrowClass = "",
    isOpen = false,
    transitionParams,
    transition = fade,
    children,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  let arrowParams = { placement, cords: { x: 0, y: 0 }, strategy };
  $$payload.out.push(`<div hidden></div> `);
  if (isOpen) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<div${spread_attributes(
      {
        popover: "manual",
        role: "tooltip",
        class: clsx$1(clsx(className)),
        ...restProps
      },
      null,
      { "overflow-visible": true }
    )}>`);
    children($$payload);
    $$payload.out.push(`<!----> `);
    if (arrow) {
      $$payload.out.push("<!--[-->");
      Arrow($$payload, spread_props([arrowParams, { class: arrowClass }]));
    } else {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--></div>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  bind_props($$props, { isOpen });
  pop();
}
function TableSearch($$payload, $$props) {
  push();
  let {
    children,
    header,
    footer,
    divClass,
    inputValue = void 0,
    striped = false,
    hoverable = false,
    customColor = "",
    color = "default",
    innerDivClass,
    inputClass,
    searchClass,
    svgDivClass,
    svgClass,
    tableClass,
    class: className,
    classes,
    placeholder = "Search",
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? {
    root: divClass,
    inner: innerDivClass,
    input: inputClass,
    search: searchClass,
    svgDiv: svgDivClass,
    svg: svgClass
  };
  const theme = getTheme("tableSearch");
  const themeColor = color === "custom" ? "default" : color;
  const { root, inner, search, svgDiv, svg, input: input2, table } = tableSearch({ color: themeColor, striped, hoverable });
  const tableCls = table({ class: clsx(tableClass, theme?.table, className) });
  const finalTableClass = color === "custom" && customColor ? clsx(tableCls, customColor) : tableCls;
  const tableSearchCtx = { striped, hoverable, color };
  setContext("tableCtx", tableSearchCtx);
  $$payload.out.push(`<div${attr_class(clsx$1(root({ class: clsx(theme?.root, styling.root) })))}><div${attr_class(clsx$1(inner({ class: clsx(theme?.inner, styling.inner) })))}><label for="table-search" class="sr-only">Search</label> <div${attr_class(clsx$1(search({ class: clsx(theme?.search, styling.search) })))}><div${attr_class(clsx$1(svgDiv({ class: clsx(theme?.svgDiv, styling.svgDiv) })))}><svg${attr_class(clsx$1(svg({ class: clsx(theme?.svg, styling.svg) })))} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path></svg></div> <input${attr("value", inputValue)} type="text" id="table-search"${attr_class(clsx$1(input2({ class: clsx(theme?.input, styling.input) })))}${attr("placeholder", placeholder)}/></div> `);
  if (header) {
    $$payload.out.push("<!--[-->");
    header($$payload);
    $$payload.out.push(`<!---->`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></div> <table${spread_attributes({ ...restProps, class: clsx$1(finalTableClass) }, null)}>`);
  if (children) {
    $$payload.out.push("<!--[-->");
    children($$payload);
    $$payload.out.push(`<!---->`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></table> `);
  if (footer) {
    $$payload.out.push("<!--[-->");
    footer($$payload);
    $$payload.out.push(`<!---->`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></div>`);
  bind_props($$props, { inputValue });
  pop();
}
function Checkbox($$payload, $$props) {
  push();
  let {
    children,
    color = "primary",
    custom,
    inline,
    tinted,
    rounded,
    group = [],
    choices = [],
    checked = false,
    indeterminate,
    classes,
    class: className,
    divClass,
    disabled = false,
    value,
    labelProps = {},
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? { div: divClass };
  const theme = getTheme("checkbox");
  const disabledValue = disabled === null ? void 0 : disabled;
  const { base, div: divStyle } = checkbox({
    color,
    tinted,
    custom,
    rounded,
    inline,
    disabled: disabledValue
  });
  function renderLabel(choice) {
    if (!choice) return "";
    if (children) {
      return children(choice);
    }
    return choice.label || "";
  }
  if (choices.length > 0) {
    $$payload.out.push("<!--[-->");
    const each_array = ensure_array_like(choices);
    $$payload.out.push(`<!--[-->`);
    for (let i = 0, $$length = each_array.length; i < $$length; i++) {
      let choice = each_array[i];
      $$payload.out.push(`<div${attr_class(clsx$1(divStyle({ class: clsx(theme?.div, styling.div) })))}>`);
      Label($$payload, spread_props([
        { show: true },
        labelProps,
        {
          children: ($$payload2) => {
            $$payload2.out.push(`<input${spread_attributes(
              {
                type: "checkbox",
                value: choice.value,
                checked: choice.checked ?? false,
                disabled,
                checked: group.includes(choice.value),
                ...restProps,
                class: clsx$1(base({ class: clsx(theme?.base, className) }))
              },
              null
            )}/> ${escape_html(renderLabel(choice))}`);
          },
          $$slots: { default: true }
        }
      ]));
      $$payload.out.push(`<!----></div>`);
    }
    $$payload.out.push(`<!--]-->`);
  } else {
    $$payload.out.push("<!--[!-->");
    $$payload.out.push(`<div${attr_class(clsx$1(divStyle({ class: clsx(theme?.div, styling.div) })))}>`);
    Label($$payload, spread_props([
      { show: true },
      labelProps,
      {
        children: ($$payload2) => {
          $$payload2.out.push(`<input${spread_attributes(
            {
              type: "checkbox",
              value,
              checked,
              indeterminate,
              disabled,
              ...restProps,
              class: clsx$1(base({ class: clsx(theme?.base, className) }))
            },
            null
          )}/> `);
          if (children) {
            $$payload2.out.push("<!--[-->");
            children($$payload2, { value, checked, disabled });
            $$payload2.out.push(`<!---->`);
          } else {
            $$payload2.out.push("<!--[!-->");
          }
          $$payload2.out.push(`<!--]-->`);
        },
        $$slots: { default: true }
      }
    ]));
    $$payload.out.push(`<!----></div>`);
  }
  $$payload.out.push(`<!--]-->`);
  bind_props($$props, { group, checked });
  pop();
}
function Input($$payload, $$props) {
  push();
  let {
    children,
    left,
    right,
    value = void 0,
    elementRef = void 0,
    clearable = false,
    size,
    color = "default",
    class: className,
    classes,
    wrapperClass,
    leftClass,
    rightClass,
    divClass,
    clearableSvgClass,
    clearableColor = "none",
    clearableClass,
    clearableOnClick,
    data = [],
    maxSuggestions = 5,
    onSelect,
    comboClass,
    comboItemClass,
    onInput,
    onFocus,
    onBlur,
    onKeydown,
    oninput,
    onfocus,
    onblur,
    onkeydown,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? {
    wrapper: wrapperClass,
    left: leftClass,
    right: rightClass,
    div: divClass,
    svg: clearableSvgClass,
    close: clearableClass
  };
  const theme = getTheme("input");
  const isCombobox = Array.isArray(data) && data.length > 0;
  let background = getContext("background");
  let group = getContext("group");
  let isGroup = !!group;
  let _size = size || clampSize(group?.size) || "md";
  const _color = color === "default" && background ? "tinted" : color;
  const {
    base,
    input: inputCls,
    left: leftCls,
    right: rightCls,
    close,
    combo,
    comboItem
  } = input({ size: _size, color: _color, grouped: isGroup });
  const clearAll = () => {
    if (elementRef) {
      const input2 = elementRef;
      input2.value = "";
      value = "";
      setTimeout(
        () => {
          input2.focus();
        },
        100
      );
    }
    if (clearableOnClick) clearableOnClick();
  };
  createDismissableContext(clearAll);
  function inputContent($$payload2) {
    if (left) {
      $$payload2.out.push("<!--[-->");
      $$payload2.out.push(`<div${attr_class(clsx$1(leftCls({ class: clsx(theme?.left, styling.left) })))}>`);
      left($$payload2);
      $$payload2.out.push(`<!----></div>`);
    } else {
      $$payload2.out.push("<!--[!-->");
    }
    $$payload2.out.push(`<!--]--> `);
    if (children) {
      $$payload2.out.push("<!--[-->");
      children($$payload2, { ...restProps, class: inputCls() });
      $$payload2.out.push(`<!---->`);
    } else {
      $$payload2.out.push("<!--[!-->");
      $$payload2.out.push(`<input${spread_attributes(
        {
          ...restProps,
          value,
          class: clsx$1(inputCls({ class: clsx(theme?.input, className) }))
        },
        null
      )}/> `);
      if (value !== void 0 && value !== "" && clearable) {
        $$payload2.out.push("<!--[-->");
        CloseButton($$payload2, {
          class: close({ class: clsx(theme?.close, styling.close) }),
          color: clearableColor,
          "aria-label": "Clear search value",
          svgClass: clsx(styling.svg)
        });
      } else {
        $$payload2.out.push("<!--[!-->");
      }
      $$payload2.out.push(`<!--]-->`);
    }
    $$payload2.out.push(`<!--]--> `);
    if (right) {
      $$payload2.out.push("<!--[-->");
      $$payload2.out.push(`<div${attr_class(clsx$1(rightCls({ class: clsx(theme?.right, styling.right) })))}>`);
      right($$payload2);
      $$payload2.out.push(`<!----></div>`);
    } else {
      $$payload2.out.push("<!--[!-->");
    }
    $$payload2.out.push(`<!--]-->`);
  }
  if (clearable) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<div tabindex="-1" class="sr-only"></div>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--> `);
  if (isCombobox) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<div${attr_class(clsx$1(clsx(isCombobox ? "relative w-full" : "", theme?.wrapper, styling.wrapper)))}>`);
    if (right || left || clearable) {
      $$payload.out.push("<!--[-->");
      $$payload.out.push(`<div${attr_class(clsx$1(base({ class: clsx(theme?.base, styling.div) })))}>`);
      inputContent($$payload);
      $$payload.out.push(`<!----></div>`);
    } else {
      $$payload.out.push("<!--[!-->");
      inputContent($$payload);
    }
    $$payload.out.push(`<!--]--> `);
    {
      $$payload.out.push("<!--[!-->");
    }
    $$payload.out.push(`<!--]--></div>`);
  } else {
    $$payload.out.push("<!--[!-->");
    if (group) {
      $$payload.out.push("<!--[-->");
      inputContent($$payload);
    } else {
      $$payload.out.push("<!--[!-->");
      if (right || left || clearable) {
        $$payload.out.push("<!--[-->");
        $$payload.out.push(`<div${attr_class(clsx$1(base({ class: clsx(theme?.base, styling.div) })))}>`);
        inputContent($$payload);
        $$payload.out.push(`<!----></div>`);
      } else {
        $$payload.out.push("<!--[!-->");
        inputContent($$payload);
      }
      $$payload.out.push(`<!--]-->`);
    }
    $$payload.out.push(`<!--]-->`);
  }
  $$payload.out.push(`<!--]-->`);
  bind_props($$props, { value, elementRef });
  pop();
}
function clampSize(s) {
  return s && s === "xs" ? "sm" : s === "xl" ? "lg" : s;
}
function Label($$payload, $$props) {
  push();
  let {
    children,
    color = "gray",
    show = true,
    class: className,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const theme = getTheme("label");
  let base = label({ color, class: clsx(theme, className) });
  if (show) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<label${spread_attributes({ ...restProps, class: clsx$1(base) }, null)}>`);
    children($$payload);
    $$payload.out.push(`<!----></label>`);
  } else {
    $$payload.out.push("<!--[!-->");
    children($$payload);
    $$payload.out.push(`<!---->`);
  }
  $$payload.out.push(`<!--]-->`);
  pop();
}
function Select($$payload, $$props) {
  push();
  let {
    children,
    items,
    value = void 0,
    elementRef = void 0,
    underline,
    size = "md",
    disabled,
    placeholder = "Choose option ...",
    clearable,
    clearableColor = "none",
    clearableOnClick,
    onClear,
    clearableSvgClass,
    clearableClass,
    selectClass,
    class: className,
    classes,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const styling = classes ?? {
    select: selectClass,
    svg: clearableSvgClass,
    close: clearableClass
  };
  const theme = getTheme("select");
  const { base, select: select$1, close } = select({ underline, size, disabled });
  const clearAll = () => {
    if (elementRef) {
      elementRef.value = "";
      elementRef.dispatchEvent(new Event("change", { bubbles: true }));
    }
    value = "";
    if (onClear) onClear();
    if (clearableOnClick) clearableOnClick();
  };
  createDismissableContext(clearAll);
  $$payload.out.push(`<div${attr_class(clsx$1(base({ class: clsx(theme?.base, className) })))}><select${spread_attributes(
    {
      disabled,
      ...restProps,
      class: clsx$1(select$1({ class: clsx(theme?.select, styling.select) }))
    },
    null
  )}>`);
  $$payload.select_value = {
    ...restProps,
    value,
    class: select$1({ class: clsx(theme?.select, styling.select) })
  }?.value;
  if (placeholder) {
    $$payload.out.push("<!--[-->");
    $$payload.out.push(`<option disabled${attr("selected", value === "" || value === void 0, true)} value=""${maybe_selected($$payload, "")}>${escape_html(placeholder)}</option>`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  if (items) {
    $$payload.out.push("<!--[-->");
    const each_array = ensure_array_like(items);
    $$payload.out.push(`<!--[-->`);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let item = each_array[$$index];
      $$payload.out.push(`<option${attr("value", item.value)}${maybe_selected($$payload, item.value)}${attr("disabled", item.disabled, true)}>${escape_html(item.name)}</option>`);
    }
    $$payload.out.push(`<!--]-->`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  if (children) {
    $$payload.out.push("<!--[-->");
    children($$payload);
    $$payload.out.push(`<!---->`);
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]-->`);
  $$payload.select_value = void 0;
  $$payload.out.push(`</select> `);
  if (value !== void 0 && value !== "" && clearable) {
    $$payload.out.push("<!--[-->");
    CloseButton($$payload, {
      class: close({ class: clsx(theme?.close, styling.close) }),
      color: clearableColor,
      "aria-label": "Clear search value",
      svgClass: clsx(styling.svg),
      disabled
    });
  } else {
    $$payload.out.push("<!--[!-->");
  }
  $$payload.out.push(`<!--]--></div>`);
  bind_props($$props, { value, elementRef });
  pop();
}
function List($$payload, $$props) {
  push();
  let {
    children,
    tag = "ul",
    isContenteditable = false,
    position = "inside",
    ctxClass,
    class: className,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const theme = getTheme("list");
  let contextClass = ctxClass || "";
  setContext("ctxClass", () => contextClass);
  let classList = list({ position, tag, class: clsx(theme, className) });
  element(
    $$payload,
    tag,
    () => {
      $$payload.out.push(`${spread_attributes(
        {
          ...restProps,
          class: clsx$1(classList),
          contenteditable: isContenteditable
        },
        null
      )}`);
    },
    () => {
      children($$payload);
      $$payload.out.push(`<!---->`);
    }
  );
  pop();
}
function Li($$payload, $$props) {
  push();
  let {
    children,
    icon,
    class: className,
    $$slots,
    $$events,
    ...restProps
  } = $$props;
  const getCtxClass = getContext("ctxClass");
  let liCls = clsx(getCtxClass(), icon && "flex items-center", className);
  $$payload.out.push(`<li${spread_attributes({ ...restProps, class: clsx$1(liCls) }, null)}>`);
  children($$payload);
  $$payload.out.push(`<!----></li>`);
  pop();
}
function CartPlusAltOutline($$payload, $$props) {
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
    ariaLabel = "cart plus alt outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M4 4h1.5L8 16m0 0h8m-8 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm8 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm.75-3H7.5M11 7H6.312M17 4v6m-3-3h6"></path></svg>`);
  pop();
}
function ChevronDownOutline($$payload, $$props) {
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
    ariaLabel = "chevron down outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="m8 10 4 4 4-4"></path></svg>`);
  pop();
}
function ChevronLeftOutline($$payload, $$props) {
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
    ariaLabel = "chevron left outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="m14 8-4 4 4 4"></path></svg>`);
  pop();
}
function ChevronRightOutline($$payload, $$props) {
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
    ariaLabel = "chevron right outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="m10 16 4-4-4-4"></path></svg>`);
  pop();
}
function CloseOutline($$payload, $$props) {
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
    ariaLabel = "close outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M6 18 17.94 6M18 18 6.06 6"></path></svg>`);
  pop();
}
function FilterSolid($$payload, $$props) {
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
    ariaLabel = "filter solid",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path d="M5.05 3C3.291 3 2.352 5.024 3.51 6.317l5.422 6.059v4.874c0 .472.227.917.613 1.2l3.069 2.25c1.01.742 2.454.036 2.454-1.2v-7.124l5.422-6.059C21.647 5.024 20.708 3 18.95 3H5.05Z"></path></svg>`);
  pop();
}
function FolderArrowRightOutline($$payload, $$props) {
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
    ariaLabel = "folder arrow right outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M13.5 8H4m4 6h8m0 0-2-2m2 2-2 2M4 6v13a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1h-5.032a1 1 0 0 1-.768-.36l-1.9-2.28a1 1 0 0 0-.768-.36H5a1 1 0 0 0-1 1Z"></path></svg>`);
  pop();
}
function MinusOutline($$payload, $$props) {
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
    ariaLabel = "minus outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M5 12h14"></path></svg>`);
  pop();
}
function PlusOutline($$payload, $$props) {
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
    ariaLabel = "plus outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M5 12h14m-7 7V5"></path></svg>`);
  pop();
}
function PrinterOutline($$payload, $$props) {
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
    ariaLabel = "printer outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M16.444 18H19a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h2.556M17 11V5a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v6h10ZM7 15h10v4a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1v-4Z"></path></svg>`);
  pop();
}
function QrCodeOutline($$payload, $$props) {
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
    ariaLabel = "qr code outline",
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
      class: clsx$1(twMerge(clsx("shrink-0", sizes[size], className))),
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
  $$payload.out.push(`<!--]--><path stroke="currentColor" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M4 4h6v6H4V4Zm10 10h6v6h-6v-6Zm0-10h6v6h-6V4Zm-4 10h.01v.01H10V14Zm0 4h.01v.01H10V18Zm-3 2h.01v.01H7V20Zm0-4h.01v.01H7V16Zm-3 2h.01v.01H4V18Zm0-4h.01v.01H4V14Z"></path><path stroke="currentColor" stroke-linejoin="round"${attr("stroke-width", strokeWidth)} d="M7 7h.01v.01H7V7Zm10 10h.01v.01H17V17Z"></path></svg>`);
  pop();
}
function Section($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  push();
  let sectionClass = fallback($$props["sectionClass"], "relative py-6 sm:py-10");
  let name = fallback($$props["name"], "default");
  const sectionClasses = {
    advancedTable: { div: "mx-auto max-w-screen-xl px-4 lg:px-12" },
    blog: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    blogTemplate: { div: "flex justify-between px-4 mx-auto max-w-screen-xl" },
    comment: { div: "max-w-2xl mx-auto px-4" },
    contact: { div: "py-8 lg:py-16 px-4 mx-auto max-w-screen-md" },
    content: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    contentwithimg: {
      div: "gap-16 items-center py-8 px-4 mx-auto max-w-screen-xl lg:grid lg:grid-cols-2 lg:py-16 lg:px-6"
    },
    crudcreateform: { div: "py-8 px-4 mx-auto max-w-2xl lg:py-16" },
    crudcreatedrawer: { div: "h-80" },
    crudreadsection: { div: "py-8 px-4 mx-auto max-w-2xl lg:py-16" },
    cta: { div: "py-8 px-4 mx-auto max-w-screen-xl sm:py-16 lg:px-6" },
    ctawithimg: {
      div: "gap-8 items-center py-8 px-4 mx-auto max-w-screen-xl xl:gap-16 md:grid md:grid-cols-2 sm:py-16 lg:px-6"
    },
    default: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    faq: { div: "py-8 px-4 mx-auto max-w-screen-xl sm:py-16 lg:px-6" },
    feature: { div: "py-8 px-4 mx-auto max-w-screen-xl sm:py-16 lg:px-6" },
    forgotpassword: {
      div: "flex flex-col items-center justify-center px-6 py-8 mx-auto  lg:py-0"
    },
    headingwithctabutton: { div: "py-8 px-4 mx-auto max-w-screen-xl sm:py-16 lg:px-6" },
    heroDefault: {
      div: "py-8 px-4 mx-auto max-w-screen-xl text-center lg:py-16 lg:px-12"
    },
    heroVisual: {
      div: "grid max-w-screen-xl px-4 py-8 mx-auto lg:gap-8 xl:gap-0 lg:py-16 lg:grid-cols-12"
    },
    login: {
      div: "flex flex-col items-center justify-center px-6 py-8 mx-auto lg:py-0"
    },
    logos: { div: "py-8 lg:py-16 mx-auto max-w-screen-xl px-4" },
    maintenance: {
      div: "py-8 px-4 mx-auto max-w-screen-md text-center lg:py-16 lg:px-12"
    },
    newsletter: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    none: { div: "" },
    page500: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    page404: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    portfolio: {
      div: "max-w-screen-xl px-4 py-8 mx-auto lg:px-6 sm:py-16 lg:py-24"
    },
    pricing: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    register: {
      div: "flex flex-col items-center justify-center px-6 py-8 mx-auto lg:py-0"
    },
    reset: {
      div: "flex flex-col items-center justify-center px-6 py-8 mx-auto lg:py-0"
    },
    schedule: {
      div: "max-w-screen-xl px-4 py-8 mx-auto lg:px-6 sm:py-16 lg:py-24"
    },
    social: {
      div: "max-w-screen-xl px-4 py-8 mx-auto text-center lg:py-16 lg:px-6"
    },
    tableheader: { div: "max-w-screen-xl px-4 mx-auto lg:px-12 w-full" },
    team: { div: "py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6" },
    testimonial: {
      div: "max-w-screen-xl px-4 py-8 mx-auto text-center lg:py-16 lg:px-6"
    }
  };
  $$payload.out.push(`<section${attr_class(clsx$1(twMerge(sectionClass, $$sanitized_props.classSection)))}><div${attr_class(clsx$1(twMerge(sectionClasses[name]["div"], $$sanitized_props.classDiv)))}><!---->`);
  slot($$payload, $$props, "default", {});
  $$payload.out.push(`<!----></div></section>`);
  bind_props($$props, { sectionClass, name });
  pop();
}
function _page($$payload, $$props) {
  push();
  let { user } = $$props;
  let divClass = "bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden";
  let innerDivClass = "flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 p-4";
  let searchClass = "w-full md:w-1/2 relative";
  let searchTerm = "";
  let currentPosition = 0;
  const itemsPerPage = 50;
  const showPage = 5;
  let totalPages = 0;
  let pagesToShow = [];
  let totalItems = 0;
  let startPage;
  let endPage = 10;
  let items = [];
  let filteredItems = items.filter((item) => Object.values(item).some((value) => String(value).toLowerCase().includes(searchTerm.toLowerCase())));
  const updateDataAndPagination = () => {
    let currentPageItems2 = filteredItems.slice(currentPosition, currentPosition + itemsPerPage);
    renderPagination(currentPageItems2.length);
  };
  const loadNextPage = () => {
    if (currentPosition + itemsPerPage < filteredItems.length) {
      currentPosition += itemsPerPage;
      updateDataAndPagination();
    }
  };
  const loadPreviousPage = () => {
    if (currentPosition - itemsPerPage >= 0) {
      currentPosition -= itemsPerPage;
      updateDataAndPagination();
    }
  };
  const renderPagination = (totalItems2) => {
    totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    const currentPage = Math.ceil((currentPosition + 1) / itemsPerPage);
    startPage = currentPage - Math.floor(showPage / 2);
    startPage = Math.max(1, startPage);
    endPage = Math.min(startPage + showPage - 1, totalPages);
    pagesToShow = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
  };
  const goToPage = (pageNumber) => {
    currentPosition = (pageNumber - 1) * itemsPerPage;
    updateDataAndPagination();
  };
  let startRange = currentPosition + 1;
  let endRange = Math.min(currentPosition + itemsPerPage, totalItems);
  let currentPageItems = filteredItems.slice(currentPosition, currentPosition + itemsPerPage);
  let hidden = true;
  let showAddItemPanel = false;
  let showScannerPanel = false;
  const scannerStreamUrl = "http://127.0.0.1:5050";
  let categories = [
    { value: "", name: "Select Type" },
    { value: "Fabric", name: "Fabric" },
    { value: "Flooring", name: "Flooring" },
    { value: "Furniture", name: "Furniture" },
    { value: "Curtains", name: "Curtains" },
    { value: "Tiles", name: "Tiles" }
  ];
  const handleCancel = () => {
    hidden = true;
  };
  const toggleAddItemPanel = () => {
    hidden = !hidden;
    showAddItemPanel = true;
    showScannerPanel = false;
  };
  const toggleScannerPanel = () => {
    hidden = !hidden;
    showAddItemPanel = false;
    showScannerPanel = true;
  };
  let name = "";
  let manufacturer = "";
  let details = "";
  let number_items = 1;
  let image = "";
  let tags = "";
  let streamUrl = "http://127.0.0.1:5050";
  const media_url = "http://127.0.0.1:5000/media/";
  let description = "";
  let item_type = "";
  let location = "";
  let check_out_poc = "";
  let check_out_date = "";
  let is_checked_out = 0;
  let camera_error = "";
  let selectedItemId = null;
  let showCameraStream = false;
  const item_type_filter_options = ["Flooring", "Curtain"];
  let selectedTypes = [];
  function toggleType(type) {
    if (selectedTypes.includes(type)) {
      selectedTypes = selectedTypes.filter((t) => t !== type);
    } else {
      selectedTypes = [...selectedTypes, type];
    }
  }
  function showErrorAlertFnct() {
    setTimeout(
      () => {
      },
      12e4
    );
  }
  async function addItem() {
    if (!name) {
      showErrorAlertFnct();
    } else {
      let date_now = /* @__PURE__ */ new Date();
      let date_added = date_now.toISOString();
      const res = await fetch("http://localhost:5000/add_item", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          manufacturer,
          details,
          item_type,
          number_items,
          image,
          description,
          location,
          date_added,
          check_out_poc,
          check_out_date,
          is_checked_out,
          tags
        })
      });
      if (!res.ok) {
        showErrorAlertFnct();
      } else {
        toggleAddItemPanel();
        window.location.reload();
      }
    }
  }
  async function capture_image() {
    const res = await fetch("http://localhost:5050/capture_image", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    if (!res.ok) {
      camera_error = "Image capture failed!";
    } else {
      image = await res.json();
      showCameraStream = false;
    }
  }
  function toggleCameraVisibility() {
    if (showCameraStream == true) {
      showCameraStream = false;
    } else {
      showCameraStream = true;
    }
  }
  async function checkoutItem(itemId) {
    const res = await fetch("http://localhost:5000/checkout_item", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId })
    });
    if (!res.ok) ;
    const index = items.findIndex((i) => i.id === itemId);
    if (index !== -1) {
      items[index] = {
        ...items[index],
        is_checked_out: true,
        check_out_poc: "you",
        check_out_date: (/* @__PURE__ */ new Date()).toLocaleDateString()
      };
    }
  }
  async function returnItem(itemId) {
    const res = await fetch("http://localhost:5000/return_item", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId })
    });
    if (!res.ok) ;
    const index = items.findIndex((i) => i.id === itemId);
    if (index !== -1) {
      items[index] = {
        ...items[index],
        is_checked_out: false,
        check_out_poc: null,
        check_out_date: null
      };
    }
  }
  async function printLabel(itemId) {
    const res = await fetch("http://localhost:5000/print_label", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId })
    });
    if (!res.ok) {
      error = "Printing Label failed";
    }
  }
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    head($$payload2, ($$payload3) => {
      $$payload3.title = `<title>Inventory</title>`;
      $$payload3.out.push(`<meta name="description" content="Page to add new item"/>`);
    });
    Section($$payload2, {
      name: "advancedTable",
      sectionClass: "w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5",
      children: ($$payload3) => {
        {
          let header = function($$payload4) {
            $$payload4.out.push(`<div class="flex w-full flex-shrink-0 flex-col items-stretch justify-end space-y-2 md:w-auto md:flex-row md:items-center md:space-y-0 md:space-x-3">`);
            {
              $$payload4.out.push("<!--[!-->");
            }
            $$payload4.out.push(`<!--]--> `);
            Button($$payload4, {
              onclick: toggleScannerPanel,
              children: ($$payload5) => {
                QrCodeOutline($$payload5, { class: "mr-2 h-3.5 w-3.5" });
                $$payload5.out.push(`<!----> Scan QR`);
              },
              $$slots: { default: true }
            });
            $$payload4.out.push(`<!----> `);
            Button($$payload4, {
              color: "alternative",
              children: ($$payload5) => {
                $$payload5.out.push(`<!---->More`);
                ChevronDownOutline($$payload5, { class: "ml-2 h-3 w-3 " });
                $$payload5.out.push(`<!---->`);
              },
              $$slots: { default: true }
            });
            $$payload4.out.push(`<!----> `);
            Dropdown($$payload4, {
              simple: true,
              class: "w-44 divide-y divide-gray-100",
              children: ($$payload5) => {
                {
                  $$payload5.out.push("<!--[!-->");
                }
                $$payload5.out.push(`<!--]-->`);
              },
              $$slots: { default: true }
            });
            $$payload4.out.push(`<!----> `);
            Button($$payload4, {
              color: "alternative",
              disabled: true,
              children: ($$payload5) => {
                $$payload5.out.push(`<!---->Filter`);
                FilterSolid($$payload5, { class: "ml-2 h-3 w-3 " });
                $$payload5.out.push(`<!---->`);
              },
              $$slots: { default: true }
            });
            $$payload4.out.push(`<!----> `);
            Dropdown($$payload4, {
              class: "w-48 space-y-2 p-3 text-sm",
              children: ($$payload5) => {
                $$payload5.out.push(`<h6 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Choose item type</h6> `);
                List($$payload5, {
                  tag: "dl",
                  children: ($$payload6) => {
                    const each_array = ensure_array_like(item_type_filter_options);
                    $$payload6.out.push(`<!--[-->`);
                    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
                      let type_option = each_array[$$index];
                      Li($$payload6, {
                        children: ($$payload7) => {
                          Checkbox($$payload7, {
                            checked: selectedTypes.includes(type_option),
                            onchange: () => toggleType(type_option),
                            children: ($$payload8) => {
                              $$payload8.out.push(`<!---->${escape_html(type_option)}`);
                            },
                            $$slots: { default: true }
                          });
                        },
                        $$slots: { default: true }
                      });
                    }
                    $$payload6.out.push(`<!--]-->`);
                  },
                  $$slots: { default: true }
                });
                $$payload5.out.push(`<!---->`);
              },
              $$slots: { default: true }
            });
            $$payload4.out.push(`<!----></div>`);
          }, footer = function($$payload4) {
            $$payload4.out.push(`<div class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0" aria-label="Table navigation"><span class="text-sm font-normal text-gray-500 dark:text-gray-400">Showing <span class="font-semibold text-gray-900 dark:text-white">${escape_html(startRange)}-${escape_html(endRange)}</span> of <span class="font-semibold text-gray-900 dark:text-white">${escape_html(totalItems)}</span></span> `);
            ButtonGroup($$payload4, {
              children: ($$payload5) => {
                const each_array_1 = ensure_array_like(pagesToShow);
                Button($$payload5, {
                  onclick: loadPreviousPage,
                  disabled: currentPosition === 0,
                  children: ($$payload6) => {
                    ChevronLeftOutline($$payload6, { size: "xs", class: "m-1.5" });
                  },
                  $$slots: { default: true }
                });
                $$payload5.out.push(`<!----> <!--[-->`);
                for (let $$index_2 = 0, $$length = each_array_1.length; $$index_2 < $$length; $$index_2++) {
                  let pageNumber = each_array_1[$$index_2];
                  Button($$payload5, {
                    onclick: () => goToPage(pageNumber),
                    children: ($$payload6) => {
                      $$payload6.out.push(`<!---->${escape_html(pageNumber)}`);
                    },
                    $$slots: { default: true }
                  });
                }
                $$payload5.out.push(`<!--]--> `);
                Button($$payload5, {
                  onclick: loadNextPage,
                  disabled: totalPages === endPage,
                  children: ($$payload6) => {
                    ChevronRightOutline($$payload6, { size: "xs", class: "m-1.5" });
                  },
                  $$slots: { default: true }
                });
                $$payload5.out.push(`<!---->`);
              },
              $$slots: { default: true }
            });
            $$payload4.out.push(`<!----></div>`);
          };
          TableSearch($$payload3, {
            placeholder: "Search",
            hoverable: true,
            divClass,
            innerDivClass,
            searchClass,
            get inputValue() {
              return searchTerm;
            },
            set inputValue($$value) {
              searchTerm = $$value;
              $$settled = false;
            },
            header,
            footer,
            children: ($$payload4) => {
              const each_array_2 = ensure_array_like(currentPageItems);
              $$payload4.out.push(`<div class="product-grid p-2 svelte-1mbcpir"><!--[-->`);
              for (let $$index_1 = 0, $$length = each_array_2.length; $$index_1 < $$length; $$index_1++) {
                let item = each_array_2[$$index_1];
                if (selectedItemId === item.id) {
                  $$payload4.out.push("<!--[-->");
                  $$payload4.out.push(`<div type="overlay" class="w-full"><div class="rounded-lg expanded w-full centered mb-6 p-4 dark:bg-slate-800 bg-slate-200 border dark:border-slate-400 border-slate-800"><div class="relative flex items-center justify-between w-full"><div class="flex justify-center"><h2 class="mb-4 text-xl inline-flex font-bold items-center px-8 text-gray-800 dark:text-slate-300 border border-cyan-950 dark:border-cyan-400 rounded-lg">${escape_html(item.name)}</h2></div> <div class="flex justify-center mt-auto">`);
                  if (item.is_checked_out) {
                    $$payload4.out.push("<!--[-->");
                    $$payload4.out.push(`<label for="borrowed" class="mb-2 p-2 bg-red-500 text-slate-900 font-semibold border border-red-900 rounded-lg">Checked out by ${escape_html(item.check_out_poc)} since ${escape_html(item.check_out_date)}</label>`);
                  } else {
                    $$payload4.out.push("<!--[!-->");
                    $$payload4.out.push(`<label for="available" class="mb-2 p-2 bg-green-500 text-slate-800 font-semibold border border-slate-900 rounded-lg">Available</label>`);
                  }
                  $$payload4.out.push(`<!--]--></div> `);
                  CloseButton($$payload4, {
                    onclick: () => selectedItemId = null,
                    class: "mb-4 dark:text-white"
                  });
                  $$payload4.out.push(`<!----></div> <div class="mb-6 grid gap-6 md:grid-cols-2"><div class="mb-6 flex flex-col items-center p-2 col-span-1"><div class="flex items-center justify-center"><img${attr("src", `${media_url}${item.image}.png`)}${attr("alt", item.image)} class="w-full border rounded-lg border-slate-900"/></div></div> <form class="p-2"><div class="mb-2 grid gap-2 md:grid-cols-2"><div>`);
                  {
                    $$payload4.out.push("<!--[!-->");
                    Label($$payload4, {
                      for: "name",
                      class: "mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg",
                      children: ($$payload5) => {
                        $$payload5.out.push(`<span class="text-red-500">Name:</span> ${escape_html(item.name)}`);
                      },
                      $$slots: { default: true }
                    });
                  }
                  $$payload4.out.push(`<!--]--></div> <div>`);
                  {
                    $$payload4.out.push("<!--[!-->");
                    Label($$payload4, {
                      for: "name",
                      class: "mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg",
                      children: ($$payload5) => {
                        $$payload5.out.push(`<span class="text-red-500">Manufacturer:</span> ${escape_html(item.manufacturer)}`);
                      },
                      $$slots: { default: true }
                    });
                  }
                  $$payload4.out.push(`<!--]--></div> <div class="mb-4">`);
                  {
                    $$payload4.out.push("<!--[!-->");
                    Label($$payload4, {
                      class: "mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg",
                      children: ($$payload5) => {
                        $$payload5.out.push(`<span class="text-red-500">Count:</span> ${escape_html(item.number_items)}`);
                      },
                      $$slots: { default: true }
                    });
                  }
                  $$payload4.out.push(`<!--]--></div> <div>`);
                  {
                    $$payload4.out.push("<!--[!-->");
                    Label($$payload4, {
                      class: "mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg",
                      children: ($$payload5) => {
                        $$payload5.out.push(`<span class="text-red-500">Type:</span> ${escape_html(item.item_type)}`);
                      },
                      $$slots: { default: true }
                    });
                  }
                  $$payload4.out.push(`<!--]--></div> `);
                  {
                    $$payload4.out.push("<!--[!-->");
                    $$payload4.out.push(`<div>`);
                    Label($$payload4, {
                      for: "storage",
                      class: "mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg",
                      children: ($$payload5) => {
                        $$payload5.out.push(`<span class="text-red-500">Storage location:</span> ${escape_html(item.location)}`);
                      },
                      $$slots: { default: true }
                    });
                    $$payload4.out.push(`<!----></div>`);
                  }
                  $$payload4.out.push(`<!--]--> <div>`);
                  {
                    $$payload4.out.push("<!--[!-->");
                    Label($$payload4, {
                      for: "storage",
                      class: "mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg",
                      children: ($$payload5) => {
                        $$payload5.out.push(`<span class="text-red-500">Tags:</span> ${escape_html(item.tags)}`);
                      },
                      $$slots: { default: true }
                    });
                  }
                  $$payload4.out.push(`<!--]--></div> <div>`);
                  {
                    $$payload4.out.push("<!--[-->");
                    if (item.details) {
                      $$payload4.out.push("<!--[-->");
                      Label($$payload4, {
                        class: "mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg",
                        children: ($$payload5) => {
                          $$payload5.out.push(`<span class="text-red-500">Details:</span> ${escape_html(item.details)}`);
                        },
                        $$slots: { default: true }
                      });
                    } else {
                      $$payload4.out.push("<!--[!-->");
                      Label($$payload4, {
                        class: "mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg",
                        children: ($$payload5) => {
                          $$payload5.out.push(`<span class="text-red-500">Details:</span> N/A`);
                        },
                        $$slots: { default: true }
                      });
                    }
                    $$payload4.out.push(`<!--]-->`);
                  }
                  $$payload4.out.push(`<!--]--></div></div> <div>`);
                  {
                    $$payload4.out.push("<!--[!-->");
                  }
                  $$payload4.out.push(`<!--]--></div> <div class="bottom-0 left-0 flex w-full justify-start space-x-4 pb-4 md:px-4">`);
                  {
                    $$payload4.out.push("<!--[!-->");
                    {
                      $$payload4.out.push("<!--[!-->");
                      if (item.is_checked_out) {
                        $$payload4.out.push("<!--[-->");
                        Button($$payload4, {
                          color: "green",
                          onclick: () => returnItem(selectedItemId),
                          class: "mb-4",
                          children: ($$payload5) => {
                            FolderArrowRightOutline($$payload5, { type: "return-button", class: "me-2 h-5 w-5" });
                            $$payload5.out.push(`<!----> return item`);
                          },
                          $$slots: { default: true }
                        });
                      } else {
                        $$payload4.out.push("<!--[!-->");
                        Button($$payload4, {
                          onclick: () => checkoutItem(selectedItemId),
                          class: "mb-4",
                          children: ($$payload5) => {
                            CartPlusAltOutline($$payload5, { type: "return-button", class: "me-2 h-5 w-5" });
                            $$payload5.out.push(`<!----> borrow`);
                          },
                          $$slots: { default: true }
                        });
                      }
                      $$payload4.out.push(`<!--]--> `);
                      Button($$payload4, {
                        onclick: () => printLabel(selectedItemId),
                        class: "mb-4",
                        children: ($$payload5) => {
                          PrinterOutline($$payload5, { type: "print-button", class: "me-2 h-5 w-5" });
                          $$payload5.out.push(`<!----> print label`);
                        },
                        $$slots: { default: true }
                      });
                      $$payload4.out.push(`<!----> `);
                      {
                        $$payload4.out.push("<!--[!-->");
                      }
                      $$payload4.out.push(`<!--]--> `);
                      Button($$payload4, {
                        color: "light",
                        onclick: () => selectedItemId = null,
                        class: "mb-4 dark:text-white",
                        children: ($$payload5) => {
                          CloseOutline($$payload5, { type: "print-button", class: "me-2 h-5 w-5" });
                          $$payload5.out.push(`<!----> close`);
                        },
                        $$slots: { default: true }
                      });
                      $$payload4.out.push(`<!---->`);
                    }
                    $$payload4.out.push(`<!--]-->`);
                  }
                  $$payload4.out.push(`<!--]--></div></form></div></div></div>`);
                } else {
                  $$payload4.out.push("<!--[!-->");
                  if (!selectedItemId) {
                    $$payload4.out.push("<!--[-->");
                    $$payload4.out.push(`<div class="mb-6 h-full flex-col items-center justify-start border rounded-lg border-inherit bg-slate-100 dark:bg-slate-700 p-2"><div class="flex justify-center mt-auto">`);
                    if (item.is_checked_out) {
                      $$payload4.out.push("<!--[-->");
                      $$payload4.out.push(`<label for="red" class="mb-2 p-2 bg-red-500 text-slate-900 font-semibold border border-red-500 rounded-lg">Checked out by ${escape_html(item.check_out_poc)} since ${escape_html(item.check_out_date)}</label>`);
                    } else {
                      $$payload4.out.push("<!--[!-->");
                      $$payload4.out.push(`<label for="green" class="mb-2 p-2 bg-green-500 text-slate-800 font-semibold border border-green-500 rounded-lg">Available</label>`);
                    }
                    $$payload4.out.push(`<!--]--></div> <img${attr("src", `${media_url}${item.image}.png`)}${attr("alt", item.name)} class="mb-6 w-full max-w-96 border rounded-lg border-slate-900"/> <div class="p-2 text-orange-500 font-bold">${escape_html(item.name)}</div> `);
                    if (item.manufacturer) {
                      $$payload4.out.push("<!--[-->");
                      $$payload4.out.push(`<div class="p-2 text-slate-900 dark:text-slate-200">by ${escape_html(item.manufacturer)}</div>`);
                    } else {
                      $$payload4.out.push("<!--[!-->");
                      $$payload4.out.push(`<div class="p-2 text-slate-900 dark:text-slate-200">Manufactuer N/A</div>`);
                    }
                    $$payload4.out.push(`<!--]--> `);
                    if (item.item_type) {
                      $$payload4.out.push("<!--[-->");
                      $$payload4.out.push(`<div class="p-2 text-slate-900 dark:text-slate-200">Type: ${escape_html(item.item_type)}</div>`);
                    } else {
                      $$payload4.out.push("<!--[!-->");
                    }
                    $$payload4.out.push(`<!--]--></div>`);
                  } else {
                    $$payload4.out.push("<!--[!-->");
                  }
                  $$payload4.out.push(`<!--]-->`);
                }
                $$payload4.out.push(`<!--]-->`);
              }
              $$payload4.out.push(`<!--]--></div>`);
            },
            $$slots: { header: true, footer: true, default: true }
          });
        }
      },
      $$slots: { default: true }
    });
    $$payload2.out.push(`<!----> `);
    Section($$payload2, {
      name: "crudcreatedrawer",
      children: ($$payload3) => {
        Drawer($$payload3, {
          id: "sidebar4",
          class: "w-1/2",
          get hidden() {
            return hidden;
          },
          set hidden($$value) {
            hidden = $$value;
            $$settled = false;
          },
          children: ($$payload4) => {
            if (showAddItemPanel) {
              $$payload4.out.push("<!--[-->");
              $$payload4.out.push(`<div class="flex items-center justify-between"><h5 id="drawer-label" class="mb-6 inline-flex items-center text-base font-semibold text-gray-500 uppercase dark:text-gray-400">New Item</h5> `);
              CloseButton($$payload4, { onclick: handleCancel, class: "mb-4 dark:text-white" });
              $$payload4.out.push(`<!----></div> <form action="#" class="mb-2">`);
              if (showCameraStream) {
                $$payload4.out.push("<!--[-->");
                $$payload4.out.push(`<div class="mb-6 flex flex-col items-center p-2 col-span-1">`);
                Label($$payload4, {
                  for: "name",
                  class: "mb-2 block p-2",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Record item image`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Button($$payload4, {
                  class: "w-full border mb-2 ",
                  onclick: capture_image,
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->capture image`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> <img${attr("src", streamUrl)} alt="Opening camera stream ..." class="text-slate-800 dark:text-slate-400 border rounded-lg mb-2"/> `);
                Button($$payload4, {
                  color: "light",
                  class: "w-full mb-2",
                  onclick: toggleCameraVisibility,
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->close camera`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Label($$payload4, {
                  class: "b-2 block",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->${escape_html(camera_error)}`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----></div>`);
              } else {
                $$payload4.out.push("<!--[!-->");
                $$payload4.out.push(`<div class="mb-4 p-2 gap-1"><div class="mb-4 grid gap-2 md:grid-cols-2">`);
                if (image) {
                  $$payload4.out.push("<!--[-->");
                  $$payload4.out.push(`<div class="w-full flex justify-center"><img${attr("src", `${media_url}${image}.png`)}${attr("alt", image)} class="max-w-[220px] max-h-[220px]"/></div>`);
                } else {
                  $$payload4.out.push("<!--[!-->");
                  $$payload4.out.push(`<div class="bg-slate-900 flex justify-center max-w-[220px] max-h-[220px] min-w-[220px] min-h-[220px]"></div>`);
                }
                $$payload4.out.push(`<!--]--> <div class="mb-6"><div class="mb-6">`);
                Label($$payload4, {
                  for: "name",
                  class: "mb-2 block",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Name`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Input($$payload4, {
                  id: "name",
                  name: "name",
                  required: true,
                  placeholder: "Item name",
                  get value() {
                    return name;
                  },
                  set value($$value) {
                    name = $$value;
                    $$settled = false;
                  }
                });
                $$payload4.out.push(`<!----></div> <div class="mb-6">`);
                Label($$payload4, {
                  for: "manufacturer",
                  class: "mb-2 block",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Manufacturer`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Input($$payload4, {
                  id: "manufacturer",
                  name: "manufacturer",
                  placeholder: "Item manufacturer",
                  get value() {
                    return manufacturer;
                  },
                  set value($$value) {
                    manufacturer = $$value;
                    $$settled = false;
                  }
                });
                $$payload4.out.push(`<!----></div></div> <div class="mb-6 w-full">`);
                Label($$payload4, {
                  for: "number_items",
                  class: "mb-2 block",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Number of Items`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> <div class="relative items-center mb-6">`);
                ButtonGroup($$payload4, {
                  children: ($$payload5) => {
                    Button($$payload5, {
                      type: "button",
                      id: "decrement-button",
                      onclick: () => number_items -= 1,
                      children: ($$payload6) => {
                        MinusOutline($$payload6, {});
                      },
                      $$slots: { default: true }
                    });
                    $$payload5.out.push(`<!----> `);
                    Input($$payload5, {
                      type: "number",
                      id: "quantity-input",
                      "aria-describedby": "helper-text-explanation",
                      placeholder: "1",
                      required: true,
                      class: "w-20",
                      get value() {
                        return number_items;
                      },
                      set value($$value) {
                        number_items = $$value;
                        $$settled = false;
                      }
                    });
                    $$payload5.out.push(`<!----> `);
                    Button($$payload5, {
                      type: "button",
                      id: "increment-button",
                      onclick: () => number_items += 1,
                      children: ($$payload6) => {
                        PlusOutline($$payload6, {});
                      },
                      $$slots: { default: true }
                    });
                    $$payload5.out.push(`<!---->`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----></div></div> <div class="mb-6">`);
                Label($$payload4, {
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Item Type `);
                    Select($$payload5, {
                      class: "mt-2",
                      items: categories,
                      get value() {
                        return item_type;
                      },
                      set value($$value) {
                        item_type = $$value;
                        $$settled = false;
                      }
                    });
                    $$payload5.out.push(`<!---->`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----></div> <div class="mb-6">`);
                Label($$payload4, {
                  for: "location",
                  class: "mb-2 block",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Storage Location`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Input($$payload4, {
                  id: "location",
                  name: "location",
                  placeholder: "Storage location",
                  get value() {
                    return location;
                  },
                  set value($$value) {
                    location = $$value;
                    $$settled = false;
                  }
                });
                $$payload4.out.push(`<!----></div> <div class="mb-6">`);
                Label($$payload4, {
                  for: "tags",
                  class: "mb-2 block",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Tags`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Input($$payload4, {
                  id: "tags",
                  name: "tags",
                  placeholder: "Tags",
                  get value() {
                    return tags;
                  },
                  set value($$value) {
                    tags = $$value;
                    $$settled = false;
                  }
                });
                $$payload4.out.push(`<!----></div></div> <div class="mb-2 justify-center w-full">`);
                Label($$payload4, {
                  for: "description",
                  class: "mb-2",
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->Description`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Textarea($$payload4, {
                  id: "message",
                  class: "w-full",
                  placeholder: "Enter a detailed item description here",
                  rows: 1,
                  name: "message",
                  get value() {
                    return details;
                  },
                  set value($$value) {
                    details = $$value;
                    $$settled = false;
                  }
                });
                $$payload4.out.push(`<!----></div> <div class="items-center justify-center w-full" role="region"><label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-16 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"><div class="flex flex-col items-center justify-center pt-5 pb-6"><p class="mb-2 text-xs text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p> <p class="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG</p></div> <input id="dropzone-file" type="file" class="hidden"/></label></div></div> <div class="bottom-0 left-0 flex w-full justify-center space-x-4 pb-4 md:absolute md:px-4">`);
                Button($$payload4, {
                  type: "submit",
                  class: "w-full",
                  onclick: addItem,
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->add item`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Button($$payload4, {
                  type: "camera",
                  class: "w-full",
                  onclick: toggleCameraVisibility,
                  children: ($$payload5) => {
                    $$payload5.out.push(`<!---->open camera`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----> `);
                Button($$payload4, {
                  class: "w-full",
                  color: "light",
                  onclick: handleCancel,
                  children: ($$payload5) => {
                    $$payload5.out.push(`<svg aria-hidden="true" class="-ml-1 h-5 w-5 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg> cancel`);
                  },
                  $$slots: { default: true }
                });
                $$payload4.out.push(`<!----></div>`);
              }
              $$payload4.out.push(`<!--]--></form>`);
            } else {
              $$payload4.out.push("<!--[!-->");
              if (showScannerPanel) {
                $$payload4.out.push("<!--[-->");
                $$payload4.out.push(`<div class="flex items-center justify-between"><h5 id="drawer-label" class="mb-6 inline-flex items-center text-base font-semibold text-gray-500 uppercase dark:text-gray-400">Scanner</h5> `);
                CloseButton($$payload4, { onclick: handleCancel, class: "mb-4 dark:text-white" });
                $$payload4.out.push(`<!----></div> <div class="page-container"><label for="id" class="mb-6 inline-flex items-center text-base text-gray-500 dark:text-gray-400">Place QR code in front of the scanner camera!</label> <img${attr("src", scannerStreamUrl)} alt="Starting Camera Stream ... " class="text-slate-200"/></div>`);
              } else {
                $$payload4.out.push("<!--[!-->");
              }
              $$payload4.out.push(`<!--]-->`);
            }
            $$payload4.out.push(`<!--]-->`);
          },
          $$slots: { default: true }
        });
      },
      $$slots: { default: true }
    });
    $$payload2.out.push(`<!---->`);
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
