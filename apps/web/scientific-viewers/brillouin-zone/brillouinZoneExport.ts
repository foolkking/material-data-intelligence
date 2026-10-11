import { layoutBrillouinZoneLabels } from "./brillouinZoneLabelLayout";
import type { BZExportRequest } from "./brillouinZoneTypes";
import { encodeScientificPng } from "../viewer-scene/scientificPngExport";

export type BZExportLabel = Readonly<{ id: string; text: string; x: number; y: number; selected: boolean }>;

export function composeBrillouinZoneImage(source: HTMLCanvasElement, request: BZExportRequest, labels: readonly BZExportLabel[]): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = request.width * request.pixelRatio;
  canvas.height = request.height * request.pixelRatio;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("BZ_EXPORT_CANVAS_UNAVAILABLE");
  context.scale(request.pixelRatio, request.pixelRatio);
  context.drawImage(source, 0, 0, request.width, request.height);
  const fontSize = Math.min(24, Math.max(14, Math.min(request.width, request.height) / 50));
  context.font = `600 ${fontSize}px Arial, sans-serif`;
  const anchors = labels.map(label => ({ ...label, width: Math.max(fontSize + 12, context.measureText(label.text).width + 16), height: fontSize + 12 }));
  const layout = layoutBrillouinZoneLabels(anchors, request.width, request.height);
  if (layout.overflow.length) throw new Error("BZ_EXPORT_LABELS_DO_NOT_FIT");
  const dark = request.background === "dark";
  const ink = dark ? "#ffd0c8" : "#7d2f28";
  const paper = dark ? "#152731" : "#ffffff";
  context.lineWidth = 1.5;
  context.strokeStyle = ink;
  context.fillStyle = ink;
  for (const point of layout.placed) {
    context.beginPath();
    context.moveTo(point.x, point.y);
    context.lineTo(point.left + point.width / 2, point.top + point.height / 2);
    context.stroke();
    context.beginPath();
    context.arc(point.x, point.y, 2.5, 0, Math.PI * 2);
    context.fill();
  }
  context.textAlign = "center";
  context.textBaseline = "middle";
  for (const point of layout.placed) {
    const label = labels.find(item => item.id === point.id)!;
    context.fillStyle = label.selected ? ink : paper;
    context.fillRect(point.left, point.top, point.width, point.height);
    context.strokeRect(point.left, point.top, point.width, point.height);
    context.fillStyle = label.selected ? paper : ink;
    context.fillText(label.text, point.left + point.width / 2, point.top + point.height / 2);
  }
  return canvas;
}

export async function encodeBrillouinZonePng(canvas: HTMLCanvasElement): Promise<Blob> {
  return encodeScientificPng(canvas, "BZ_EXPORT");
}
