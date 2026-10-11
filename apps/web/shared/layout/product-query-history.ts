/** Next's patched history API owns its router markers and synchronizes query hooks. */
function productQueryState(extraState: Record<string, unknown> = {}) {
  const state = { ...window.history.state, ...extraState };
  // Passing these markers back makes Next treat a product query change as an
  // internal navigation and skip useSearchParams synchronization.
  delete state.__NA;
  delete state._N;
  delete state.__PRIVATE_NEXTJS_INTERNALS_TREE;
  return state;
}

export function pushProductQuery(href: string, extraState: Record<string, unknown> = {}) {
  window.history.pushState(productQueryState(extraState), "", href);
}

export function replaceProductQuery(href: string) {
  window.history.replaceState(productQueryState(), "", href);
}
