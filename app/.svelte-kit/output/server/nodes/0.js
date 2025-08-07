import * as universal from '../entries/pages/_layout.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.js";
export const imports = ["_app/immutable/nodes/0.Du_JJLYk.js","_app/immutable/chunks/DU5mI3xL.js","_app/immutable/chunks/2tcJcwV0.js","_app/immutable/chunks/CfjtbjMP.js","_app/immutable/chunks/Bzak7iHL.js","_app/immutable/chunks/BoK4rymu.js","_app/immutable/chunks/o7m2jq1a.js","_app/immutable/chunks/LisNP5KJ.js","_app/immutable/chunks/YtgobVKg.js","_app/immutable/chunks/rMFyZai9.js","_app/immutable/chunks/CB7ZvMWT.js","_app/immutable/chunks/8IoxBTPD.js","_app/immutable/chunks/uOfKX_dW.js","_app/immutable/chunks/t7qXoh_M.js","_app/immutable/chunks/BTmSotT-.js"];
export const stylesheets = ["_app/immutable/assets/theme.CD54FDqW.css","_app/immutable/assets/0.DpdaPjeN.css"];
export const fonts = ["_app/immutable/assets/fira-mono-cyrillic-ext-400-normal.FAIU8e3o.woff2","_app/immutable/assets/fira-mono-cyrillic-ext-400-normal.Co4MVjrD.woff","_app/immutable/assets/fira-mono-cyrillic-400-normal.BJkDdjbt.woff2","_app/immutable/assets/fira-mono-cyrillic-400-normal.DUd3efVn.woff","_app/immutable/assets/fira-mono-greek-ext-400-normal.Be4g_LSk.woff2","_app/immutable/assets/fira-mono-greek-ext-400-normal.BQ5yw6bY.woff","_app/immutable/assets/fira-mono-greek-400-normal.ftNhKy_S.woff2","_app/immutable/assets/fira-mono-greek-400-normal.B_0AmgK7.woff","_app/immutable/assets/fira-mono-symbols2-400-normal.C6JptOil.woff2","_app/immutable/assets/fira-mono-symbols2-400-normal.CpeG9ob9.woff","_app/immutable/assets/fira-mono-latin-ext-400-normal.B2gPvaNr.woff2","_app/immutable/assets/fira-mono-latin-ext-400-normal.CbD3vWRE.woff","_app/immutable/assets/fira-mono-latin-400-normal.DVTTRLHv.woff2","_app/immutable/assets/fira-mono-latin-400-normal.C3FQ26ho.woff"];
