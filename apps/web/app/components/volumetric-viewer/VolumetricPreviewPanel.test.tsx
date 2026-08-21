import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VolumetricPreviewPanel } from "./VolumetricPreviewPanel";

describe("volumetric preview fallback", () => {
  it("retains inert JSON and manifest access when Worker is unavailable", () => {
    const dataset = { schema_version: "phase10j.volumetric_dataset.v1", grid: { shape: [2,2,2] }, fields: [], payloads: [], security: { renderer_included: false } };
    const manifest = { schema_version: "phase10j.volumetric_manifest.v1", capabilities: { renderer_included: false } };
    const { container } = render(<VolumetricPreviewPanel artifacts={[{ id: "d", type: "volumetric_dataset_json", name: "volumetric_dataset.json", content: dataset }, { id: "m", type: "volumetric_manifest_json", name: "volumetric_manifest.json", content: manifest }] as never} />);
    expect(screen.getByTestId("volumetric-renderer-state")).toHaveTextContent("不支持");
    fireEvent.click(screen.getByRole("tab", { name: "元数据" }));
    expect(screen.getByTestId("volumetric-metadata-json-preview")).toHaveTextContent("phase10j.volumetric_dataset.v1");
    fireEvent.click(screen.getByRole("tab", { name: "数据清单" }));
    expect(screen.getByTestId("volumetric-manifest-preview")).toHaveTextContent("phase10j.volumetric_manifest.v1");
    expect(container.querySelector("canvas, script, iframe")).toBeNull();
  });
});
