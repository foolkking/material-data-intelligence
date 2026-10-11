import "@testing-library/jest-dom/vitest";
import {fireEvent, render, screen} from "@testing-library/react";
import {expect, it} from "vitest";
import fixture from "../../../../tests/fixtures/volumetric_contract/cubic_constant_scalar.json";
import {validateVolumetricArtifacts} from "./volumetricValidation";
import {buildElfOrbitalProduct, validateElfOrbitalValues} from "./elfOrbitalProduct";
import {DensityScientificDetails} from "./DensityScientificDetails";

function source(quantity: string, unit: string) {
  const validation = validateVolumetricArtifacts(fixture.raw_dataset, fixture.manifest);
  if (!validation.ok) throw new Error("Invalid test fixture");
  const original = validation.bundle;
  const field = {...original.fields[0].field, quantity, unit};
  return {field, bundle:{...original, fields:[{...original.fields[0],field}]}};
}
it("keeps significant range warnings visible while detailed values are collapsed",()=>{
  const {field,bundle}=source("electron_localization_function","dimensionless");
  const orbital=buildElfOrbitalProduct(bundle,validateElfOrbitalValues([-0.2,1.1],"float64","elf",field.contentHash));
  render(<DensityScientificDetails bundle={bundle} field={field} orbital={orbital} charge={null}/>);
  expect(screen.getByText("ELF 超出 0–1，偏差超过数值容差，请核对源数据。")).toBeVisible();
  expect(screen.getByTestId("elf-orbital-statistics")).not.toBeVisible();
  fireEvent.click(screen.getByText("统计与数值校验"));
  expect(screen.getByTestId("elf-orbital-range-status")).toHaveTextContent("源值范围异常");
  expect(screen.getByText("1 / 1")).toBeVisible();
});
it("retains unavailable orbital identity and scientific limits in source details",()=>{
  const {field,bundle}=source("orbital_density","electron/angstrom^3");
  render(<DensityScientificDetails bundle={bundle} field={field} orbital={buildElfOrbitalProduct(bundle)} charge={null}/>);
  fireEvent.click(screen.getByText("来源与科学适用范围"));
  expect(screen.getByTestId("orbital-identity-completeness")).toHaveTextContent("未提供");
  expect(screen.getByText(field.contentHash)).toBeVisible();
  expect(screen.getByTestId("orbital-interpretation-boundary")).toHaveTextContent("不推断单轨道、HOMO/LUMO");
});
it("does not display a previous field's orbital summary",()=>{
  const {field,bundle}=source("orbital_density","electron/angstrom^3");
  render(<DensityScientificDetails bundle={bundle} field={{...field,fieldId:"another"}} orbital={buildElfOrbitalProduct(bundle)} charge={null}/>);
  expect(screen.queryByTestId("elf-orbital-product")).not.toBeInTheDocument();
});
