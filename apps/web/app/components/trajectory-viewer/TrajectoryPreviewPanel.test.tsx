import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import fixed from "../../../../../docs/phase10g/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import { TrajectoryPreviewPanel } from "../PlannerWorkbench";

describe("TrajectoryPreviewPanel",()=>{
  it("routes trajectory and manifest artifacts into viewer and inert JSON tabs",async()=>{
    const artifacts=[
      {id:"trajectory",type:"trajectory_json",name:"trajectory.json",content:fixed,metadata:{toolId:"structure.trajectory_viewer",provenance:{formalViewerToolId:"structure.trajectory_viewer"}}},
      {id:"manifest",type:"trajectory_manifest_json",name:"trajectory_manifest.json",content:{schema_version:"phase10g.trajectory_manifest.v1",trajectory_id:fixed.trajectory_id},metadata:{}},
    ] as never;
    render(<TrajectoryPreviewPanel artifacts={artifacts}/>);
    expect(screen.queryByTestId("trajectory-preview-panel")).not.toBeNull();
    expect(screen.getByTestId("trajectory-product-path").textContent).toContain("structure.trajectory_viewer");
    expect(await screen.findByTestId("trajectory-viewer-fallback")).not.toBeNull();
    expect(screen.getByText("TRAJECTORY_VIEWER_UNSUPPORTED")).not.toBeNull();
    await userEvent.click(screen.getByRole("tab",{name:"Trajectory JSON"}));
    expect(screen.getByTestId("trajectory-json-preview").textContent).toContain("phase10g.trajectory.v1");
    await userEvent.click(screen.getByRole("tab",{name:"Manifest"}));
    expect(screen.getByTestId("trajectory-manifest-preview").textContent).toContain("phase10g.trajectory_manifest.v1");
  });

  it("remounts viewer state when a new artifact record reuses the same canonical trajectory",async()=>{
    const artifact=(id:string)=>[{id,type:"trajectory_json",name:"trajectory.json",content:fixed,metadata:{toolId:"structure.trajectory_viewer",provenance:{formalViewerToolId:"structure.trajectory_viewer"}}}] as never;
    const view=render(<TrajectoryPreviewPanel artifacts={artifact("trajectory-job-one")}/>);
    const first=await screen.findByTestId("trajectory-viewer-fallback");
    view.rerender(<TrajectoryPreviewPanel artifacts={artifact("trajectory-job-two")}/>);
    const second=await screen.findByTestId("trajectory-viewer-fallback");
    expect(second).not.toBe(first);
  });
});
