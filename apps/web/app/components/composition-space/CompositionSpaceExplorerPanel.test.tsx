import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { CompositionSpaceExplorerPanel } from "./CompositionSpaceExplorerPanel";
import { compositionSpaceArtifact, compositionSpacePayload } from "./testFixtures";

describe("CompositionSpaceExplorerPanel", () => {
  it("renders backend-provided PCA, clusters, comparison and bounded tables", () => {
    render(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact()]} />);
    const panel = screen.getByTestId("composition-space-explorer");
    expect(panel).toHaveTextContent("Composition Space Explorer");
    expect(panel).toHaveTextContent("95%");
    expect(screen.getByRole("img", { name: "PCA composition scatter colored by cluster" })).toBeTruthy();
    expect(screen.getByTestId("composition-space-clusters")).toHaveTextContent("Cl-Na");
    expect(screen.getByTestId("composition-space-outliers")).toHaveTextContent("0.72");
    expect(screen.getByTestId("composition-space-comparison")).toHaveTextContent("exploratory_combined_projection");
    expect(panel).toHaveTextContent("do not establish structural similarity");
  });

  it("selects a stable sampleKey with the keyboard and shows source-bound values", () => {
    render(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact()]} />);
    const point = screen.getByRole("button", { name: /s2, NaCl/ });
    fireEvent.keyDown(point, { key: "Enter" });
    const inspector = screen.getByTestId("composition-space-sample-inspector");
    expect(inspector).toHaveTextContent("s2");
    expect(inspector).toHaveTextContent("obj_table");
    expect(inspector).toHaveTextContent("NaCl");
    expect(inspector).toHaveTextContent("band_gap");
    expect(inspector).toHaveTextContent("regression:model:absolute_error");
    expect(point).toHaveAttribute("aria-pressed", "true");
  });

  it("uses displayPointKeys for identity and order while treating sample references as informational", () => {
    const payload = compositionSpacePayload();
    payload.displayPointKeys = ["obj_table:s3", "obj_table:s1"];
    payload.displaySampleRefs = ["informational-only-value"];
    render(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact(payload)]} />);
    const points = within(screen.getByRole("img", { name: "PCA composition scatter colored by cluster" })).getAllByRole("button");
    expect(points).toHaveLength(2);
    expect(points[0]).toHaveAccessibleName(/s3, Li2O/);
    expect(points[1]).toHaveAccessibleName(/s1, Si/);
  });

  it("uses only allowlisted artifact color modes without recomputing science", async () => {
    const user = userEvent.setup();
    render(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact()]} />);
    const selector = screen.getByRole("combobox", { name: "Color by" });
    await user.selectOptions(selector, "property:band_gap");
    expect(screen.getByRole("img", { name: "PCA composition scatter colored by property:band_gap" })).toBeTruthy();
    expect(screen.getByText(/band_gap: 1.1 to 3.2 eV/)).toBeTruthy();
    await user.selectOptions(selector, "ml:regression:model:absolute_error");
    expect(screen.getByText(/regression:model:absolute_error: 0.1 to 0.6/)).toBeTruthy();
  });

  it("renders malicious artifact labels as inert text", () => {
    const payload = compositionSpacePayload();
    payload.points[0].formula = "<img src=x onerror=alert(1)>";
    const { container } = render(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact(payload)]} />);
    fireEvent.click(screen.getByRole("button", { name: /s1/ }));
    expect(screen.getByTestId("composition-space-sample-inspector")).toHaveTextContent("<img src=x onerror=alert(1)>");
    expect(container.querySelector("img, script, iframe, canvas")).toBeNull();
  });

  it("rejects unsupported, executable, invalid-key and over-cap artifacts", () => {
    const unsupported = compositionSpacePayload();
    unsupported.schemaVersion = "unknown";
    const { rerender } = render(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact(unsupported)]} />);
    expect(screen.getByTestId("composition-space-invalid")).toHaveTextContent("COMPOSITION_SPACE_SCHEMA_UNSUPPORTED");

    const unsafe = compositionSpacePayload();
    unsafe.security.artifactJavaScript = true;
    rerender(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact(unsafe)]} />);
    expect(screen.getByTestId("composition-space-invalid")).toHaveTextContent("COMPOSITION_SPACE_SECURITY_DECLARATION_INVALID");

    const invalidBinding = compositionSpacePayload();
    invalidBinding.displayPointKeys[0] = "obj_table:missing";
    rerender(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact(invalidBinding)]} />);
    expect(screen.getByTestId("composition-space-invalid")).toHaveTextContent("COMPOSITION_SPACE_DISPLAY_BINDING_INVALID");

    const overCap = compositionSpacePayload();
    overCap.displayPointKeys = Array.from({ length: 10_001 }, (_, index) => `obj_table:s${index}`);
    rerender(<CompositionSpaceExplorerPanel artifacts={[compositionSpaceArtifact(overCap)]} />);
    const fallback = screen.getByTestId("composition-space-invalid");
    expect(fallback).toHaveTextContent("COMPOSITION_SPACE_PREVIEW_CAP_EXCEEDED");
    expect(within(fallback).getByText("Artifact JSON")).toBeTruthy();
  });
});
