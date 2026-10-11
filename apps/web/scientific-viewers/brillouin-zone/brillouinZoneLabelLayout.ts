export type BZLabelAnchor = Readonly<{ id: string; x: number; y: number; width: number; height: number }>;
export type BZLabelPlacement = BZLabelAnchor & Readonly<{ left: number; top: number }>;

const GAP = 4;

export function layoutBrillouinZoneLabels(anchors: readonly BZLabelAnchor[], width: number, height: number) {
  const placed: BZLabelPlacement[] = [];
  const overflow: string[] = [];
  if (width <= 0 || height <= 0) return { placed, overflow };
  for (const anchor of anchors) {
    if (![anchor.x, anchor.y, anchor.width, anchor.height].every(Number.isFinite)) continue;
    if (anchor.x < 0 || anchor.x > width || anchor.y < 0 || anchor.y > height) continue;
    let best: BZLabelPlacement | undefined;
    let bestDistance = Infinity;
    // Try nearby positions first, keeping the scientific marker at its true projection.
    for (let radius = 28; radius <= 196; radius += 28) {
      for (let angle = -Math.PI / 4; angle < 7 * Math.PI / 4; angle += Math.PI / 4) {
        const left = Math.max(GAP, Math.min(width - anchor.width - GAP, anchor.x + Math.cos(angle) * radius - anchor.width / 2));
        const top = Math.max(GAP, Math.min(height - anchor.height - GAP, anchor.y + Math.sin(angle) * radius - anchor.height / 2));
        if (left + anchor.width > width - GAP || top + anchor.height > height - GAP) continue;
        const next = { ...anchor, left, top };
        if (placed.some(item => overlaps(next, item))) continue;
        if (anchors.some(point => point.x >= left - GAP && point.x <= left + anchor.width + GAP && point.y >= top - GAP && point.y <= top + anchor.height + GAP)) continue;
        const distance = Math.hypot(left + anchor.width / 2 - anchor.x, top + anchor.height / 2 - anchor.y);
        if (distance < bestDistance) { best = next; bestDistance = distance; }
      }
      if (best) break;
    }
    if (best) placed.push(best);
    else overflow.push(anchor.id);
  }
  return { placed, overflow };
}

function overlaps(a: BZLabelPlacement, b: BZLabelPlacement) {
  return a.left < b.left + b.width + GAP && a.left + a.width + GAP > b.left
    && a.top < b.top + b.height + GAP && a.top + a.height + GAP > b.top;
}
