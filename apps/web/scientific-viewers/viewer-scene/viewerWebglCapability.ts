export function supportsManagedWebGL(): boolean {
  if (typeof window === "undefined" || typeof document === "undefined") return false;
  if (/jsdom/i.test(window.navigator.userAgent)) return false;
  return typeof window.WebGLRenderingContext === "function" || typeof window.WebGL2RenderingContext === "function";
}
