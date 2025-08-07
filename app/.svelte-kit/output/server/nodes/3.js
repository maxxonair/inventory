import * as universal from '../entries/pages/old_pages/_page.ts.js';

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/old_pages/_page.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/old_pages/+page.ts";
export const imports = ["_app/immutable/nodes/3.XcVMUaf7.js","_app/immutable/chunks/3H4_WFAY.js","_app/immutable/chunks/CfjtbjMP.js","_app/immutable/chunks/Bzak7iHL.js","_app/immutable/chunks/BoK4rymu.js","_app/immutable/chunks/LisNP5KJ.js","_app/immutable/chunks/BhxS6hLT.js","_app/immutable/chunks/o7m2jq1a.js","_app/immutable/chunks/DU5mI3xL.js","_app/immutable/chunks/2tcJcwV0.js","_app/immutable/chunks/8IoxBTPD.js","_app/immutable/chunks/uOfKX_dW.js","_app/immutable/chunks/D554zIEY.js"];
export const stylesheets = ["_app/immutable/assets/theme.CD54FDqW.css","_app/immutable/assets/3.CmA0MnTJ.css"];
export const fonts = [];
