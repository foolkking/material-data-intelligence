import {expect, it} from "vitest";
import {supportsPairedDensity, updateIsosurfaceLayers} from "./isosurface-layer-controls";
import type {IsosurfaceLayerRequest, ValidatedVolumetricField} from "./volumetricViewerTypes";
const layers: IsosurfaceLayerRequest[] = [{layerId:"positive",isovalue:0.25,sign:"positive"},{layerId:"negative",isovalue:-0.25,sign:"negative"}];

it("keeps opposite values and signs when a locked threshold crosses zero",()=>{
  expect(updateIsosurfaceLayers(layers,"positive",-0.5,true)).toEqual([{layerId:"positive",isovalue:-0.5,sign:"negative"},{layerId:"negative",isovalue:0.5,sign:"positive"}]);
  expect(layers[0].isovalue).toBe(0.25);
});
it("leaves independent layers untouched and ignores nonfinite edits",()=>{
  expect(updateIsosurfaceLayers(layers,"positive",-0.5,false)[1]).toBe(layers[1]);
  expect(updateIsosurfaceLayers(layers,"positive",NaN,true)).toBe(layers);
});
it("only enables paired density controls for the applicable scientific quantities",()=>{
  const field={quantity:"orbital_density",minimum:-0.01,maximum:1,spin:null} as ValidatedVolumetricField;
  expect(supportsPairedDensity(field)).toBe(false);
  expect(supportsPairedDensity({...field,quantity:"charge_density"})).toBe(true);
  expect(supportsPairedDensity({...field,quantity:"electron_localization_function"})).toBe(false);
});
