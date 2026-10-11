import { expect, it } from "vitest";
import fixed from "../../../../tests/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import type { Artifact } from "../../app/lib/planner-api";
import { resultTrajectoryPoint } from "./result-trajectory-selection";

const artifact = { artifactId: "saved-trajectory", content: fixed } as Artifact;
const frame: Agent2ScientificFact = {fact_id:"frame",predicate:"trajectory.selected_frame_number",subject_ref:"selection-1",value:12,unit:"ordinal (1-based)",source:{artifact_id:"saved-trajectory",artifact_locator:"/frames/11/frame_index"}};
const atom: Agent2ScientificFact = {fact_id:"atom",predicate:"trajectory.selected_atom_number",subject_ref:"selection-1",value:2,unit:"ordinal (1-based)",source:{artifact_id:"saved-trajectory",artifact_locator:"/frames/11/atom_ids/1"}};

it("restores the persisted selected frame and source atom", () => {
  expect(resultTrajectoryPoint(artifact, [frame, atom])).toEqual({frameIndex:11,atom:{siteIndex:1,imageOffset:[0,0,0]}});
  expect(resultTrajectoryPoint(artifact, [frame])).toEqual({frameIndex:11,atom:null});
});

it("never borrows selection from another artifact or unrelated subject", () => {
  expect(resultTrajectoryPoint({...artifact,artifactId:"other"}, [frame, atom])).toBeNull();
  expect(resultTrajectoryPoint(artifact, [frame,{...atom,subject_ref:"other"}])).toEqual({frameIndex:11,atom:null});
});

it("does not choose an arbitrary frame from multiple selections", () => {
  expect(resultTrajectoryPoint(artifact,[frame,{...frame,fact_id:"other",value:1,source:{...frame.source,artifact_locator:"/frames/0/frame_index"}}])).toBeNull();
});

it("rejects stale, inconsistent, and out-of-range locators", () => {
  for (const bad of [{...frame,value:11},{...frame,unit:"count"},{...frame,value:13,source:{...frame.source,artifact_locator:"/frames/12/frame_index"}}]) {
    expect(resultTrajectoryPoint(artifact,[bad])).toBeNull();
  }
  expect(resultTrajectoryPoint(artifact,[frame,{...atom,value:999}])).toBeNull();
  expect(resultTrajectoryPoint(artifact,[frame,{...atom,value:5,source:{...atom.source,artifact_locator:"/frames/11/atom_ids/4"}}])).toBeNull();
});
