import type {IsosurfaceLayerRequest, ValidatedVolumetricField} from "./volumetricViewerTypes";

export function supportsPairedDensity(field: ValidatedVolumetricField | null | undefined) {
  return Boolean(field && (field.spin?.channel === "spin_difference" || field.quantity === "charge_density" && field.minimum < 0 && field.maximum > 0));
}

export function updateIsosurfaceLayers(layers: IsosurfaceLayerRequest[], layerId: string, value: number, paired: boolean): IsosurfaceLayerRequest[] {
  if (!Number.isFinite(value) || !layers.some(layer => layer.layerId === layerId)) return layers;
  return layers.map(layer => {
    if (layer.layerId !== layerId && !(paired && layers.length === 2)) return layer;
    const next = layer.layerId === layerId ? value : -value;
    return {...layer, isovalue: next, sign: next < 0 ? "negative" : "positive"};
  });
}
