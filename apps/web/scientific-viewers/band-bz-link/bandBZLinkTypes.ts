import type { BZArtifactBundle } from "../brillouin-zone/brillouinZoneMapper";
import type { BZVector3 } from "../brillouin-zone/brillouinZoneTypes";

export const BAND_BZ_LINK_SCHEMA_VERSION = "phase10i3.reciprocal_band_bz_link.v1" as const;

export type BandBZLinkBundle = Readonly<{
  band: unknown;
  bandHash: string;
  bz: BZArtifactBundle;
  animation?: unknown;
}>;

export type BandBZPointOccurrence = Readonly<{
  id: string;
  qpointIndex: number;
  segmentIndex: number;
  endpoint: "start" | "end";
  bzPointId: string;
  fractional: BZVector3;
  cartesian: BZVector3;
  residual: number;
}>;

export type BandBZSegmentMapping = Readonly<{
  bandSegmentIndex: number;
  bzSegmentId: string;
  variantId: string;
  direction: "forward" | "reverse";
  distanceStart: number;
  distanceEnd: number;
  discontinuityBefore: boolean;
  startPointId: string;
  endPointId: string;
  residual: number;
}>;

export type BandBZSampleMapping = Readonly<{
  qpointIndex: number;
  segmentIndex: number;
  bzSegmentId: string;
  t: number;
  fractional: BZVector3;
  cartesian: BZVector3;
  pathDistance: number;
  residual: number;
  pointOccurrenceId: string | null;
}>;

export type BandBZBranch = Readonly<{
  branchIndex: number;
  frequencies: readonly number[];
}>;

export type BandBZLinkModel = Readonly<{
  schemaVersion: typeof BAND_BZ_LINK_SCHEMA_VERSION;
  status: "compatible" | "partial";
  bandArtifactHash: string;
  structureIdentity: string;
  reciprocalHash: string;
  bzArtifactHash: string;
  kpathArtifactHash: string;
  primitiveLatticeHash: string;
  convention: "physics_2pi";
  units: "radian_per_angstrom";
  provider: Readonly<{ name: string; version: string; pathConvention: string; equivalence: "exact_ordered_geometry" }>;
  timeReversal: Readonly<{ bz: boolean; band: "undeclared" }>;
  pathVariantId: string;
  reciprocalMatrix: readonly [BZVector3, BZVector3, BZVector3];
  pointOccurrences: readonly BandBZPointOccurrence[];
  segments: readonly BandBZSegmentMapping[];
  samples: readonly BandBZSampleMapping[];
  branches: readonly BandBZBranch[];
  frequencyZeroTolerance: number;
  warnings: readonly string[];
  metrics: Readonly<{ compatibilityMs: number; mappingMs: number; pointMappings: number; segmentMappings: number; sampleMappings: number; numericValues: number }>;
}>;

export type BandBZLinkResult =
  | Readonly<{ ok: true; model: BandBZLinkModel }>
  | Readonly<{ ok: false; errors: readonly string[]; warnings: readonly string[] }>;

export type ReciprocalSelection = Readonly<{
  sourcePanel: "band" | "bz" | "table";
  kind: "high_symmetry_point" | "sampled_reciprocal_point" | "path_segment" | "phonon_mode";
  transactionId: number;
  pinned: boolean;
  bandArtifactHash: string;
  bzArtifactHash: string;
  pathVariantId: string;
  bzPointId?: string;
  bzSegmentId?: string;
  pointOccurrenceId?: string;
  qpointIndex?: number;
  branchIndex?: number;
  modeId?: string;
  frequency?: number;
  t?: number;
  reciprocalFractional?: BZVector3;
  reciprocalCartesian?: BZVector3;
  pathDistance?: number;
  residual?: number;
  discontinuity?: boolean;
}>;

export type ReciprocalSelectionState = Readonly<{
  revision: number;
  hover: ReciprocalSelection | null;
  pinned: ReciprocalSelection | null;
}>;
