import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import type { Artifact } from "../../app/lib/planner-api";
import { artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";
import { trajectoryPoint, type TrajectoryPoint } from "./trajectory-selection";

/** Restore only a unique, artifact-bound selection verified against loaded bytes. */
export function resultTrajectoryPoint(artifact: Artifact, facts: readonly Agent2ScientificFact[]): TrajectoryPoint | null {
  const own = facts.filter(fact => fact.source.artifact_id === artifactIdentity(artifact));
  const frames = own.filter(fact => fact.predicate === "trajectory.selected_frame_number");
  if (frames.length !== 1) return null;
  const frame = frames[0];
  const match = /^\/frames\/(0|[1-9]\d*)\/frame_index$/.exec(frame.source.artifact_locator || "");
  const index = Number(match?.[1]);
  if (!match || !Number.isSafeInteger(index) || frame.value !== index + 1 || frame.unit !== "ordinal (1-based)") return null;
  const atoms = own.filter(fact => fact.predicate === "trajectory.selected_atom_number" && fact.subject_ref === frame.subject_ref);
  if (atoms.length > 1) return null;
  let atomId: string | null = null;
  if (atoms.length) {
    const atom = atoms[0];
    const locator = new RegExp(`^/frames/${index}/atom_ids/(0|[1-9]\\d*)$`).exec(atom.source.artifact_locator || "");
    const atomIndex = Number(locator?.[1]);
    if (!locator || !Number.isSafeInteger(atomIndex) || atom.value !== atomIndex + 1 || atom.unit !== "ordinal (1-based)") return null;
    atomId = `atom:${atomIndex}:0.0.0`;
  }
  return trajectoryPoint(artifact.content, `frame:${index}`, atomId)?.point ?? null;
}
