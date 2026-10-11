import { afterEach, expect, it, vi } from "vitest";
import { bindScientificPointerPick } from "./scientificPointerPick";

const cleanups: Array<() => void> = [];
afterEach(() => { cleanups.splice(0).forEach(cleanup => cleanup()); document.body.replaceChildren(); });
function setup() {
  const canvas = document.createElement("canvas"); document.body.append(canvas);
  canvas.getBoundingClientRect = () => ({ left: 0, top: 0, right: 200, bottom: 200, width: 200, height: 200 }) as DOMRect;
  const pick = vi.fn(); const dispose = bindScientificPointerPick(canvas, pick); cleanups.push(dispose);
  const pointer = (type: string, x = 50, values: Record<string, unknown> = {}, target: EventTarget = canvas) => {
    const event = new Event(type, { bubbles: true });
    Object.assign(event, { clientX: x, clientY: 50, pointerId: 1, button: 0, isPrimary: true, ...values });
    target.dispatchEvent(event);
  };
  return { canvas, pick, dispose, pointer };
}
it("selects a primary click but ignores orphan releases, other buttons and outside releases", () => {
  const { pointer, pick } = setup();
  pointer("pointerup");
  pointer("pointerdown", 50, { button: 2 }); pointer("pointerup", 50, { button: 2 });
  pointer("pointerdown", 198); pointer("pointerup", 201);
  expect(pick).not.toHaveBeenCalled();
  pointer("pointerdown"); pointer("pointerup", 52);
  expect(pick).toHaveBeenCalledOnce(); expect(pick).toHaveBeenCalledWith(52, 50);
});
it("does not select after a drag, including a drag returning to its starting point", () => {
  const { pointer, pick } = setup();
  pointer("pointerdown"); pointer("pointermove", 90); pointer("pointermove", 50); pointer("pointerup");
  expect(pick).not.toHaveBeenCalled();
});
it("rejects multi-touch including a second finger outside the canvas, then permits a fresh tap", () => {
  const { pointer, pick } = setup();
  pointer("pointerdown"); pointer("pointerdown", 60, { pointerId: 2, isPrimary: false });
  pointer("pointerup", 60, { pointerId: 2, isPrimary: false }); pointer("pointerup");
  pointer("pointerdown"); pointer("pointerdown", 60, { pointerId: 2, isPrimary: false }, document.body);
  pointer("pointerup"); pointer("pointerup", 60, { pointerId: 2, isPrimary: false }, document.body);
  expect(pick).not.toHaveBeenCalled();
  pointer("pointerdown"); pointer("pointerup"); expect(pick).toHaveBeenCalledOnce();
});
it("invalidates cancelled, interrupted and disposed gestures without consuming events", () => {
  const { canvas, pointer, pick, dispose } = setup();
  for (const interruption of ["pointercancel", "lostpointercapture", "wheel"]) {
    pointer("pointerdown"); pointer(interruption); pointer("pointerup");
  }
  pointer("pointerdown"); window.dispatchEvent(new Event("blur")); pointer("pointerup");
  pointer("pointerdown"); dispose(); pointer("pointerup");
  const event = new Event("pointerdown", { bubbles: true, cancelable: true }); canvas.dispatchEvent(event);
  expect(event.defaultPrevented).toBe(false); expect(pick).not.toHaveBeenCalled();
});
