/** Select on a click/tap, while leaving orbit, pan and multi-touch gestures alone. */
export function bindScientificPointerPick(element: HTMLElement, pick: (x: number, y: number) => void): () => void {
  const view = element.ownerDocument.defaultView;
  if (!view) return () => {};
  const pointers = new Set<number>();
  let candidate: { id: number; x: number; y: number } | null = null;
  const invalidate = () => { candidate = null; };
  const reset = () => { candidate = null; pointers.clear(); };
  const down = (event: PointerEvent) => {
    if (!element.contains(event.target as Node)) { invalidate(); return; }
    const alone = pointers.size === 0;
    pointers.add(event.pointerId);
    candidate = alone && event.button === 0 && event.isPrimary !== false
      ? { id: event.pointerId, x: event.clientX, y: event.clientY } : null;
  };
  const move = (event: PointerEvent) => {
    if (candidate?.id === event.pointerId && Math.hypot(event.clientX - candidate.x, event.clientY - candidate.y) > 5) invalidate();
  };
  const up = (event: PointerEvent) => {
    const start = candidate;
    pointers.delete(event.pointerId);
    invalidate();
    if (!start || start.id !== event.pointerId || pointers.size || event.button !== 0
      || Math.hypot(event.clientX - start.x, event.clientY - start.y) > 5) return;
    const bounds = element.getBoundingClientRect();
    if (bounds.width <= 0 || bounds.height <= 0 || event.clientX < bounds.left || event.clientX > bounds.right
      || event.clientY < bounds.top || event.clientY > bounds.bottom) return;
    pick(event.clientX, event.clientY);
  };
  const cancel = (event: PointerEvent) => { pointers.delete(event.pointerId); invalidate(); };
  // Capture release before OrbitControls relinquishes its pointer capture.
  view.addEventListener("pointerdown", down, true);
  view.addEventListener("pointermove", move, true);
  view.addEventListener("pointerup", up, true);
  view.addEventListener("pointercancel", cancel, true);
  element.addEventListener("lostpointercapture", cancel);
  element.addEventListener("wheel", invalidate, { passive: true });
  view.addEventListener("blur", reset);
  return () => {
    reset();
    view.removeEventListener("pointerdown", down, true);
    view.removeEventListener("pointermove", move, true);
    view.removeEventListener("pointerup", up, true);
    view.removeEventListener("pointercancel", cancel, true);
    element.removeEventListener("lostpointercapture", cancel);
    element.removeEventListener("wheel", invalidate);
    view.removeEventListener("blur", reset);
  };
}
