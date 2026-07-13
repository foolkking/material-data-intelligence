export const TRAJECTORY_SCHEMA_VERSION = "phase10g.trajectory.v1";
export const TRAJECTORY_FRAME_SCHEMA_VERSION = "phase10g.trajectory_frame.v1";

export type TrajectoryReferenceResult = {
  valid: boolean;
  errors: string[];
  frameCount: number;
  atomCount: number;
};

const kinds = new Set(["molecular_dynamics", "geometry_optimization", "structure_sequence", "unknown_static_sequence"]);
const modes = new Set(["fractional", "cartesian"]);
const wrappings = new Set(["wrapped", "unwrapped", "unknown"]);
const timeUnits = new Set(["femtosecond", "picosecond"]);
const forbidden = ["http://", "https://", "javascript:", "<script", "<iframe", "eval(", "file://"];
const forbiddenKeys = new Set(["callback", "code", "eval", "function", "html", "iframe", "module", "script", "shader", "src", "texture", "url", "__proto__", "constructor", "prototype"]);

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function triplet(value: unknown): value is number[] {
  return Array.isArray(value) && value.length === 3 && value.every(finite);
}

function latticeValid(value: unknown): boolean {
  if (!Array.isArray(value) || value.length !== 3 || !value.every(triplet)) return false;
  const [a, b, c] = value as number[][];
  const det = a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]);
  const scale = Math.max(...value.map((row) => Math.hypot(...row)));
  return scale > 0 && Math.abs(det) > 1e-12 * scale ** 3;
}

export function fractionalToCartesian(fractional: readonly number[], lattice: readonly (readonly number[])[]): [number, number, number] {
  return [0, 1, 2].map((axis) => fractional[0] * lattice[0][axis] + fractional[1] * lattice[1][axis] + fractional[2] * lattice[2][axis]) as [number, number, number];
}

function scanInert(root: unknown, errors: Set<string>): void {
  const queue: Array<{value: unknown; depth: number; key: string}> = [{value: root, depth: 0, key: ""}];
  let visited = 0;
  while (queue.length > 0) {
    const current = queue.shift()!;
    visited += 1;
    if (visited > 10_000 || current.depth > 8) { errors.add("TRAJECTORY_NESTING_LIMIT_EXCEEDED"); return; }
    if (forbiddenKeys.has(current.key.toLowerCase())) errors.add("TRAJECTORY_EXECUTABLE_FIELD_FORBIDDEN");
    if (typeof current.value === "string") {
      const lowered = current.value.toLowerCase();
      if (forbidden.some((marker) => lowered.includes(marker))) errors.add("TRAJECTORY_EXTERNAL_REFERENCE_FORBIDDEN");
    }
    if (Array.isArray(current.value)) current.value.forEach((value) => queue.push({value, depth: current.depth + 1, key: current.key}));
    else if (record(current.value)) Object.entries(current.value).forEach(([key, value]) => queue.push({value, depth: current.depth + 1, key}));
  }
}

export function validateTrajectoryReference(payload: unknown): TrajectoryReferenceResult {
  const errors = new Set<string>();
  if (!record(payload)) return {valid: false, errors: ["TRAJECTORY_SCHEMA_INVALID"], frameCount: 0, atomCount: 0};
  if (payload.schema_version !== TRAJECTORY_SCHEMA_VERSION) errors.add("TRAJECTORY_SCHEMA_UNSUPPORTED");
  if (!kinds.has(String(payload.kind))) errors.add("TRAJECTORY_KIND_UNSUPPORTED");
  if (!modes.has(String(payload.coordinate_mode))) errors.add("TRAJECTORY_COORDINATE_MODE_INVALID");
  if (!wrappings.has(String(payload.position_wrapping))) errors.add("TRAJECTORY_POSITION_WRAPPING_INVALID");
  if (payload.atom_identity_mode !== "stable_index") errors.add("TRAJECTORY_ATOM_IDENTITY_MODE_INVALID");
  if (JSON.stringify(payload.periodic_boundary) !== "[true,true,true]" && JSON.stringify(payload.periodic_boundary) !== "[false,false,false]") errors.add("TRAJECTORY_PERIODIC_BOUNDARY_INVALID");

  const atoms = record(payload.atoms) ? payload.atoms : {};
  const atomCount = typeof atoms.count === "number" && Number.isInteger(atoms.count) ? atoms.count : 0;
  const atomRecords = Array.isArray(atoms.records) ? atoms.records : [];
  if (atomCount < 1 || atomCount > 4096 || atomRecords.length !== atomCount) errors.add("TRAJECTORY_ATOM_COUNT_MISMATCH");
  const labels = new Set<string>();
  atomRecords.forEach((atom, index) => {
    if (!record(atom) || atom.atom_id !== index || atom.occupancy !== 1) errors.add("TRAJECTORY_ATOM_ID_INVALID");
    if (record(atom) && typeof atom.label === "string") {
      if (labels.has(atom.label)) errors.add("TRAJECTORY_LABEL_DUPLICATE");
      labels.add(atom.label);
    }
  });

  const frames = Array.isArray(payload.frames) ? payload.frames : [];
  if (frames.length < 1) errors.add("TRAJECTORY_EMPTY");
  if (frames.length > 10000 || frames.length * atomCount * 3 > 12_000_000) errors.add("TRAJECTORY_COORDINATE_VALUE_LIMIT_EXCEEDED");
  const properties = record(payload.properties) ? payload.properties : {};
  let previousTime: number | null = null;
  let previousStep: number | null = null;
  frames.forEach((frameValue, frameIndex) => {
    if (!record(frameValue)) { errors.add("TRAJECTORY_FRAME_FIELDS_INVALID"); return; }
    if (frameValue.schema_version !== TRAJECTORY_FRAME_SCHEMA_VERSION || frameValue.frame_index !== frameIndex) errors.add("TRAJECTORY_FRAME_INDEX_INVALID");
    if (JSON.stringify(frameValue.atom_ids) !== JSON.stringify(Array.from({length: atomCount}, (_, index) => index))) errors.add("TRAJECTORY_SPECIES_MISMATCH");
    const positions = frameValue.positions;
    if (Array.isArray(positions) && positions.length !== atomCount) errors.add("TRAJECTORY_ATOM_COUNT_MISMATCH");
    if (!Array.isArray(positions) || positions.length !== atomCount || !positions.every(triplet)) errors.add("TRAJECTORY_POSITION_SHAPE_INVALID");
    if (payload.position_wrapping === "wrapped" && payload.coordinate_mode === "fractional" && Array.isArray(positions) && positions.some((p) => triplet(p) && p.some((v) => v < -1e-9 || v >= 1 + 1e-9))) errors.add("TRAJECTORY_WRAPPED_POSITION_OUT_OF_RANGE");
    if (payload.lattice_mode === "fixed" && frameValue.lattice !== null) errors.add("TRAJECTORY_LATTICE_UNEXPECTED");
    if (payload.lattice_mode === "variable" && frameValue.lattice === null) errors.add("TRAJECTORY_LATTICE_REQUIRED");
    else if (payload.lattice_mode === "variable" && !latticeValid(frameValue.lattice)) errors.add("TRAJECTORY_LATTICE_SINGULAR");
    for (const name of ["velocities", "forces"] as const) {
      const expected = properties[name] === true;
      if ((frameValue[name] !== null) !== expected) errors.add("TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT");
      if (expected && (!Array.isArray(frameValue[name]) || frameValue[name].length !== atomCount || !(frameValue[name] as unknown[]).every(triplet))) errors.add(`TRAJECTORY_${name === "velocities" ? "VELOCITY" : "FORCE"}_SHAPE_INVALID`);
    }
    const time = frameValue.time;
    if (payload.kind === "molecular_dynamics" && !finite(time)) errors.add("TRAJECTORY_TIME_MISSING");
    if (finite(time) && previousTime !== null && time < previousTime) errors.add("TRAJECTORY_TIME_NONMONOTONIC");
    if (finite(time)) previousTime = time;
    const step = frameValue.step;
    if (typeof step === "number" && previousStep !== null && step < previousStep) errors.add("TRAJECTORY_STEP_NONMONOTONIC");
    if (typeof step === "number") previousStep = step;
  });
  if (payload.lattice_mode === "fixed" && !latticeValid(payload.fixed_lattice)) errors.add("TRAJECTORY_LATTICE_SINGULAR");
  if (payload.lattice_mode === "variable" && payload.fixed_lattice !== null) errors.add("TRAJECTORY_LATTICE_UNEXPECTED");
  const time = record(payload.time) ? payload.time : {};
  if (payload.kind === "molecular_dynamics" && !timeUnits.has(String(time.unit))) errors.add("TRAJECTORY_TIME_UNIT_UNSUPPORTED");
  scanInert(payload, errors);
  return {valid: errors.size === 0, errors: [...errors].sort(), frameCount: frames.length, atomCount};
}
