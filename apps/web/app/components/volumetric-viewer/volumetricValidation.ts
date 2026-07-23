import type {
  ValidatedVolumetricBundle,
  ValidatedVolumetricChunk,
  ValidatedVolumetricField,
  ValidatedVolumetricGrid,
  ValidatedVolumetricPayload,
  ValidatedVolumetricRelationship,
  VolumeMatrix3,
  VolumeVector3,
  VolumetricValidationResult,
} from "./volumetricViewerTypes";

type JsonRecord = Record<string, unknown>;

const SHA256 = /^[0-9a-f]{64}$/;
const SAFE_ID = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$/;
const FORBIDDEN_KEYS = new Set(["__proto__", "callback", "code", "constructor", "eval", "function", "html", "iframe", "module", "prototype", "script", "shader", "src", "texture", "url", "urls"]);
const FORBIDDEN_MARKERS = ["http://", "https://", "javascript:", "<script", "<iframe", "file://", "new function", "eval("];

const DATASET_KEYS = ["schema_version", "dataset_id", "grid", "payloads", "fields", "relationships", "provenance", "warnings", "caps", "security", "content_hash"];
const GRID_KEYS = ["schema_version", "grid_id", "coordinate_space", "length_unit", "shape", "origin_cartesian", "origin_fractional", "step_matrix", "sample_location", "boundary_conditions", "endpoint_policy", "structure_binding", "domain_extent_matrix", "voxel_volume", "tolerance_policy", "security", "content_hash"];
const PAYLOAD_KEYS = ["schema_version", "payload_id", "encoding", "dtype", "endianness", "stored_component_count", "flatten_order", "grid_shape", "logical_shape", "value_count", "uncompressed_bytes", "compressed_bytes", "media_type", "artifact_name", "inline_values", "chunks", "compression", "logical_sha256", "storage_sha256", "storage_layout_hash", "security"];
const FIELD_KEYS = ["schema_version", "field_id", "field_name", "grid_id", "grid_content_hash", "payload_id", "payload_logical_sha256", "quantity", "custom_quantity", "value_kind", "field_rank", "logical_component_count", "stored_component_count", "component_labels", "component_basis", "unit", "normalization_semantics", "integral_semantics", "spin", "potential_reference", "complex_semantics", "statistics", "provenance", "warnings", "security", "content_hash"];
const MANIFEST_KEYS = ["schema_version", "manifest_id", "dataset_id", "dataset_content_hash", "schema_versions", "artifacts", "capabilities", "external_resources", "executable_assets", "preview_mode", "caps", "security", "content_hash"];
const NORMALIZATIONS = new Set(["source_native","normalized_to_unit_integral","normalized_to_electron_count","normalized_to_charge","not_normalized","unknown"]);
const INTEGRALS = new Set(["electron_count","elementary_charge","magnetic_moment","cell_average","zero_by_definition","not_physically_interpreted","unknown"]);
const RELATIONSHIP_KINDS = new Set(["total_equals_up_plus_down","spin_difference_equals_up_minus_down","vector_magnitude","complex_norm_density"]);

export function validateVolumetricArtifacts(datasetValue: unknown, manifestValue: unknown): VolumetricValidationResult {
  const errors: string[] = [];
  if (!record(datasetValue) || !exactKeys(datasetValue, DATASET_KEYS) || datasetValue.schema_version !== "phase10j.volumetric_dataset.v1") {
    return failure("VOLUME_VIEWER_CONTRACT_INVALID", ["VOLUME_DATASET_SCHEMA_INVALID"]);
  }
  if (!record(manifestValue) || !exactKeys(manifestValue, MANIFEST_KEYS) || manifestValue.schema_version !== "phase10j.volumetric_manifest.v1") {
    return failure("VOLUME_VIEWER_CONTRACT_INVALID", ["VOLUME_MANIFEST_SCHEMA_INVALID"]);
  }
  try {
    scanInert(datasetValue);
    scanInert(manifestValue);
  } catch {
    return failure("VOLUME_VIEWER_CONTRACT_INVALID", ["VOLUME_EXECUTABLE_METADATA_FORBIDDEN"]);
  }
  if (!canonicalSecurity(datasetValue.security) || !canonicalSecurity(manifestValue.security)) errors.push("VOLUME_SECURITY_INVALID");
  if (!Array.isArray(manifestValue.external_resources) || manifestValue.external_resources.length || !Array.isArray(manifestValue.executable_assets) || manifestValue.executable_assets.length) errors.push("VOLUME_MANIFEST_SECURITY_INVALID");
  if (!record(manifestValue.capabilities) || manifestValue.capabilities.renderer_included !== false || manifestValue.capabilities.isosurface_included !== false || manifestValue.capabilities.slice_included !== false) errors.push("VOLUME_MANIFEST_SECURITY_INVALID");
  if (manifestValue.dataset_id !== datasetValue.dataset_id || manifestValue.dataset_content_hash !== datasetValue.content_hash) errors.push("VOLUME_MANIFEST_DATASET_MISMATCH");
  if (!safeId(datasetValue.dataset_id) || !sha(datasetValue.content_hash) || !sha(manifestValue.content_hash)) errors.push("VOLUME_CONTENT_HASH_MISMATCH");

  const grid = validateGrid(datasetValue.grid, errors);
  const payloadValues = Array.isArray(datasetValue.payloads) ? datasetValue.payloads : [];
  const fieldValues = Array.isArray(datasetValue.fields) ? datasetValue.fields : [];
  if (!grid || payloadValues.length < 1 || payloadValues.length !== fieldValues.length || payloadValues.length > 8) errors.push("VOLUME_DATASET_CAP_EXCEEDED");
  const payloads = payloadValues.map((value) => validatePayload(value, errors)).filter((value): value is ValidatedVolumetricPayload => value !== null);
  const payloadById = new Map(payloads.map((payload) => [payload.payloadId, payload]));
  const fields = fieldValues.map((value) => validateField(value, errors)).filter((value): value is ValidatedVolumetricField => value !== null);
  if (new Set(payloads.map((value) => value.payloadId)).size !== payloads.length || new Set(fields.map((value) => value.fieldId)).size !== fields.length) errors.push("VOLUME_CANONICAL_ORDER_INVALID");
  if (payloads.map((value) => value.payloadId).join("|") !== [...payloads].sort((a,b)=>a.payloadId.localeCompare(b.payloadId)).map((value)=>value.payloadId).join("|")) errors.push("VOLUME_CANONICAL_ORDER_INVALID");
  if (fields.map((value) => value.fieldId).join("|") !== [...fields].sort((a,b)=>a.fieldId.localeCompare(b.fieldId)).map((value)=>value.fieldId).join("|")) errors.push("VOLUME_CANONICAL_ORDER_INVALID");
  const fieldIds = new Set(fields.map((field) => field.fieldId));
  const relationshipValues = Array.isArray(datasetValue.relationships) ? datasetValue.relationships : [];
  const relationships = relationshipValues.map((value) => validateRelationship(value, fieldIds, errors)).filter((value): value is ValidatedVolumetricRelationship => value !== null);
  if (relationships.map((value) => value.relationshipId).join("|") !== [...relationships].sort((a,b)=>a.relationshipId.localeCompare(b.relationshipId)).map((value)=>value.relationshipId).join("|")) errors.push("VOLUME_RELATIONSHIP_INVALID");
  validateDerivedCollinearSemantics(fields, relationships, errors);

  const compatibility = fields.map((field) => {
    const payload = payloadById.get(field.payloadId);
    const reasons: string[] = [];
    if (!payload) reasons.push("binding_mismatch");
    if (grid && field.gridId !== grid.gridId) reasons.push("binding_mismatch");
    if (field.valueKind !== "real" || field.fieldRank !== "scalar" || field.storedComponentCount !== 1) reasons.push("real_scalar_required");
    if (grid?.sampleLocation !== "node") reasons.push("node_samples_required");
    if (grid?.shape.some((value) => value < 2)) reasons.push("grid_axis_too_small");
    return payload ? Object.freeze({ field, payload, supported: reasons.length === 0, reasons: Object.freeze(reasons) }) : null;
  }).filter((value): value is NonNullable<typeof value> => value !== null);
  if (compatibility.length !== fields.length) errors.push("VOLUME_FIELD_PAYLOAD_MISMATCH");
  const artifactEntries = Array.isArray(manifestValue.artifacts) ? manifestValue.artifacts : [];
  const artifactNames: string[] = [];
  for (const entry of artifactEntries) {
    if (!record(entry) || !exactKeys(entry, ["name", "kind", "media_type", "bytes", "sha256", "schema_version"]) || typeof entry.name !== "string" || !safeArtifactName(entry.name) || !positiveInteger(entry.bytes) || !sha(entry.sha256)) {
      errors.push("VOLUME_MANIFEST_REFERENCE_INVALID");
    } else artifactNames.push(entry.name);
  }
  if (artifactNames.length !== new Set(artifactNames).size || artifactNames.join("|") !== [...artifactNames].sort().join("|")) errors.push("VOLUME_MANIFEST_REFERENCE_INVALID");
  const warningValues = Array.isArray(datasetValue.warnings) && datasetValue.warnings.every((item) => typeof item === "string") ? datasetValue.warnings as string[] : [];
  if (!grid || errors.length) return failure("VOLUME_VIEWER_CONTRACT_INVALID", errors);
  const provenance = record(datasetValue.provenance) ? datasetValue.provenance : {};
  const bundle: ValidatedVolumetricBundle = Object.freeze({
    datasetId: String(datasetValue.dataset_id),
    datasetContentHash: String(datasetValue.content_hash),
    sourceFormat: typeof provenance.source_format === "string" ? provenance.source_format : "unknown",
    sourceSha256: sha(provenance.source_sha256) ? String(provenance.source_sha256) : "0".repeat(64),
    grid,
    fields: Object.freeze(compatibility),
    relationships: Object.freeze(relationships),
    warnings: Object.freeze([...warningValues]),
    manifestContentHash: String(manifestValue.content_hash),
    artifactNames: Object.freeze(artifactNames),
  });
  return Object.freeze({ ok: true, bundle });
}

function validateGrid(value: unknown, errors: string[]): ValidatedVolumetricGrid | null {
  if (!record(value) || !exactKeys(value, GRID_KEYS) || value.schema_version !== "phase10j.volumetric_grid.v1" || value.coordinate_space !== "real_cartesian" || value.length_unit !== "angstrom") { errors.push("VOLUME_GRID_SCHEMA_INVALID"); return null; }
  const shape = int3(value.shape); const origin = vector3(value.origin_cartesian); const steps = matrix3(value.step_matrix);
  const boundaries = string3(value.boundary_conditions);
  if (!shape || shape.some((item) => item < 1 || item > 512) || !origin || !steps || !boundaries || boundaries.some((item) => item !== "periodic" && item !== "non_periodic") || new Set(boundaries).size !== 1) { errors.push("VOLUME_GRID_SCHEMA_INVALID"); return null; }
  if (!wellConditioned(steps)) { errors.push("VOLUME_GRID_BASIS_ILL_CONDITIONED"); return null; }
  if (!safeId(value.grid_id) || !sha(value.content_hash) || !["node","cell_center"].includes(String(value.sample_location)) || !["excluded","included","not_applicable"].includes(String(value.endpoint_policy))) errors.push("VOLUME_GRID_SCHEMA_INVALID");
  const periodic = boundaries[0] === "periodic";
  let binding: ValidatedVolumetricGrid["structureBinding"] = null;
  if (periodic) {
    const source = value.structure_binding;
    if (!record(source) || !exactKeys(source, ["structure_sha256","lattice_sha256","lattice_matrix","basis_role"]) || !sha(source.structure_sha256) || !sha(source.lattice_sha256) || source.basis_role !== "canonical_structure_cell") errors.push("VOLUME_STRUCTURE_BINDING_INVALID");
    else {
      const lattice = matrix3(source.lattice_matrix);
      if (!lattice || !wellConditioned(lattice)) errors.push("VOLUME_STRUCTURE_BINDING_INVALID");
      else binding = Object.freeze({ structureSha256:String(source.structure_sha256), latticeSha256:String(source.lattice_sha256), latticeMatrix:lattice });
    }
    if (value.endpoint_policy !== "excluded") errors.push("VOLUME_ENDPOINT_POLICY_INVALID");
  } else if (value.structure_binding !== null) errors.push("VOLUME_NONPERIODIC_BINDING_INVALID");
  return Object.freeze({ schemaVersion:"phase10j.volumetric_grid.v1", gridId:String(value.grid_id), contentHash:String(value.content_hash), shape, origin, stepMatrix:steps, sampleLocation:value.sample_location as "node"|"cell_center", boundaryConditions:boundaries as ValidatedVolumetricGrid["boundaryConditions"], endpointPolicy:value.endpoint_policy as ValidatedVolumetricGrid["endpointPolicy"], periodic, structureBinding:binding });
}

function validatePayload(value: unknown, errors: string[]): ValidatedVolumetricPayload | null {
  if (!record(value) || !exactKeys(value, PAYLOAD_KEYS) || value.schema_version !== "phase10j.volumetric_payload.v1") { errors.push("VOLUME_PAYLOAD_SCHEMA_INVALID"); return null; }
  const shape=int3(value.grid_shape); const dtype=value.dtype; const encoding=value.encoding; const components=value.stored_component_count;
  if (!shape || !["float32","float64"].includes(String(dtype)) || !["inline_json","raw_binary","gzip_binary","chunked_binary"].includes(String(encoding)) || value.endianness!=="little" || value.flatten_order!=="ijkc_component_fastest" || components!==1 && components!==2 && components!==3) { errors.push("VOLUME_PAYLOAD_LAYOUT_INVALID"); return null; }
  const count=shape[0]*shape[1]*shape[2]*Number(components); const bytes=count*(dtype==="float32"?4:8);
  if (!Number.isSafeInteger(count) || value.value_count!==count || value.uncompressed_bytes!==bytes || !positiveInteger(value.compressed_bytes) || !sha(value.logical_sha256) || !sha(value.storage_sha256) || value.payload_id!==`payload:${String(value.logical_sha256)}`) errors.push("VOLUME_PAYLOAD_BYTE_MISMATCH");
  const chunks: ValidatedVolumetricChunk[]=[];
  if (encoding==="chunked_binary") {
    if (!Array.isArray(value.chunks) || !value.chunks.length || value.chunks.length>256) errors.push("VOLUME_CHUNK_CAP_EXCEEDED");
    else value.chunks.forEach((item,index)=>{if(!record(item)||item.chunk_id!==`chunk:${String(index).padStart(4,"0")}`||!positiveInteger(item.i_end)||!Number.isSafeInteger(item.i_start)||Number(item.i_start)<0||Number(item.i_end)<=Number(item.i_start)||!safeArtifactName(item.artifact_name)||!["raw_binary","gzip_binary"].includes(String(item.encoding))||!positiveInteger(item.uncompressed_bytes)||!positiveInteger(item.compressed_bytes)||!sha(item.logical_sha256)||!sha(item.storage_sha256)){errors.push("VOLUME_CHUNK_ORDER_INVALID");return;}chunks.push(Object.freeze({chunkId:String(item.chunk_id),iStart:Number(item.i_start),iEnd:Number(item.i_end),artifactName:String(item.artifact_name),encoding:item.encoding as "raw_binary"|"gzip_binary",mediaType:String(item.media_type),uncompressedBytes:Number(item.uncompressed_bytes),compressedBytes:Number(item.compressed_bytes),logicalSha256:String(item.logical_sha256),storageSha256:String(item.storage_sha256)}));});
  }
  const inline = encoding==="inline_json"&&Array.isArray(value.inline_values)&&value.inline_values.length===count&&value.inline_values.every(finite) ? Object.freeze(value.inline_values.map(Number)) : null;
  if (encoding==="inline_json"&&!inline) errors.push("VOLUME_INLINE_PAYLOAD_INVALID");
  if ((encoding==="raw_binary"||encoding==="gzip_binary")&&!safeArtifactName(value.artifact_name)) errors.push("VOLUME_BINARY_PAYLOAD_INVALID");
  return Object.freeze({schemaVersion:"phase10j.volumetric_payload.v1",payloadId:String(value.payload_id),encoding:encoding as ValidatedVolumetricPayload["encoding"],dtype:dtype as "float32"|"float64",gridShape:shape,valueCount:count,uncompressedBytes:bytes,compressedBytes:Number(value.compressed_bytes),logicalSha256:String(value.logical_sha256),storageSha256:String(value.storage_sha256),artifactName:typeof value.artifact_name==="string"?value.artifact_name:null,inlineValues:inline,chunks:Object.freeze(chunks)});
}

function validateField(value: unknown, errors: string[]): ValidatedVolumetricField | null {
  if (!record(value)||!exactKeys(value,FIELD_KEYS)||value.schema_version!=="phase10j.volumetric_field.v1"||!safeId(value.field_id)||!safeId(value.grid_id)||!safeId(value.payload_id)||!sha(value.content_hash)||typeof value.field_name!=="string"||value.field_name.length>96) { errors.push("VOLUME_FIELD_SCHEMA_INVALID"); return null; }
  const statistics=record(value.statistics)?value.statistics:null;
  const componentCandidate=statistics&&Array.isArray(statistics.stored_components)?statistics.stored_components[0]:null;
  const components=record(componentCandidate)?componentCandidate:null;
  const unit=record(value.unit)?value.unit:null;
  const provenance=record(value.provenance)?value.provenance:null;
  const transformations=provenance&&Array.isArray(provenance.transformations)?provenance.transformations:null;
  if(!components||![components.minimum,components.maximum,components.mean,components.standard_deviation,components.rms,components.integral].every(finite)||!unit||typeof unit.canonical_unit!=="string"||typeof unit.source_unit!=="string"||!NORMALIZATIONS.has(String(value.normalization_semantics))||!INTEGRALS.has(String(value.integral_semantics))||!provenance||!sha(provenance.source_sha256)||typeof provenance.producer!=="string"||typeof provenance.producer_version!=="string"||!transformations||!transformations.every((item)=>record(item)&&exactKeys(item,["kind","detail"])&&typeof item.kind==="string"&&typeof item.detail==="string"&&item.detail.length<=160)) {errors.push("VOLUME_STATISTICS_INVALID");return null;}
  const spin=validateSpin(value.spin,errors);
  const potentialReference=validatePotentialReference(value.potential_reference,String(unit.canonical_unit),errors);
  const minimum=Number(components.minimum),maximum=Number(components.maximum);if(minimum>maximum)errors.push("VOLUME_STATISTICS_INVALID");
  const warnings=Array.isArray(value.warnings)&&value.warnings.every((item)=>typeof item==="string")?Object.freeze([...value.warnings] as string[]):Object.freeze([] as string[]);
  return Object.freeze({schemaVersion:"phase10j.volumetric_field.v1",fieldId:String(value.field_id),fieldName:String(value.field_name),gridId:String(value.grid_id),payloadId:String(value.payload_id),quantity:String(value.quantity),valueKind:value.value_kind as "real"|"complex",fieldRank:value.field_rank as "scalar"|"vector",storedComponentCount:Number(value.stored_component_count),unit:String(unit.canonical_unit),sourceUnit:String(unit.source_unit),normalizationSemantics:String(value.normalization_semantics) as ValidatedVolumetricField["normalizationSemantics"],integralSemantics:String(value.integral_semantics) as ValidatedVolumetricField["integralSemantics"],spin,potentialReference,provenance:Object.freeze({sourceSha256:String(provenance.source_sha256),producer:String(provenance.producer),producerVersion:String(provenance.producer_version),transformations:Object.freeze(transformations.map((item)=>Object.freeze({kind:String((item as JsonRecord).kind),detail:String((item as JsonRecord).detail)})))}),minimum,maximum,mean:Number(components.mean),standardDeviation:Number(components.standard_deviation),rms:Number(components.rms),integral:Number(components.integral),warnings,contentHash:String(value.content_hash)});
}

function validatePotentialReference(value:unknown,unit:string,errors:string[]):ValidatedVolumetricField["potentialReference"]{
  if(value===null)return null;
  if(!record(value)||!exactKeys(value,["kind","reference_value","reference_unit","shift_applied","shift_amount","source_metadata"])||!["absolute_declared","cell_average_zero","vacuum_reference","fermi_reference","source_defined","unknown"].includes(String(value.kind))||value.reference_unit!==unit||!finite(value.reference_value)||typeof value.shift_applied!=="boolean"||!finite(value.shift_amount)||typeof value.source_metadata!=="string"||value.source_metadata.length>128||(!value.shift_applied&&value.shift_amount!==0)){errors.push("VOLUME_POTENTIAL_REFERENCE_INVALID");return null;}
  return Object.freeze({kind:value.kind as NonNullable<ValidatedVolumetricField["potentialReference"]>["kind"],referenceValue:Number(value.reference_value),referenceUnit:String(value.reference_unit),shiftApplied:value.shift_applied,shiftAmount:Number(value.shift_amount),sourceMetadata:value.source_metadata});
}

function validateSpin(value:unknown,errors:string[]):ValidatedVolumetricField["spin"]{
  if(value===null)return null;
  if(!record(value)||!exactKeys(value,["representation","channel","component_basis","sign_convention","source_convention"])||!["collinear","non_collinear"].includes(String(value.representation))||!["total","spin_up","spin_down","spin_difference","magnetization_x","magnetization_y","magnetization_z","magnetization_vector"].includes(String(value.channel))||typeof value.sign_convention!=="string"||typeof value.source_convention!=="string"||value.sign_convention.length>128||value.source_convention.length>128){errors.push("VOLUME_SPIN_SEMANTICS_INVALID");return null;}
  return Object.freeze({representation:value.representation as "collinear"|"non_collinear",channel:value.channel as NonNullable<ValidatedVolumetricField["spin"]>["channel"],signConvention:value.sign_convention,sourceConvention:value.source_convention});
}

function validateRelationship(value:unknown,fieldIds:Set<string>,errors:string[]):ValidatedVolumetricRelationship|null{
  if(!record(value)||!exactKeys(value,["relationship_id","kind","input_field_ids","output_field_id","status","residual"])||!safeId(value.relationship_id)||!RELATIONSHIP_KINDS.has(String(value.kind))||!["declared","validated","unverified"].includes(String(value.status))||!finite(value.residual)||!Array.isArray(value.input_field_ids)||!value.input_field_ids.length||value.input_field_ids.some((item)=>typeof item!=="string"||!fieldIds.has(item))||typeof value.output_field_id!=="string"||!fieldIds.has(value.output_field_id)){errors.push("VOLUME_RELATIONSHIP_INVALID");return null;}
  return Object.freeze({relationshipId:String(value.relationship_id),kind:value.kind as ValidatedVolumetricRelationship["kind"],inputFieldIds:Object.freeze([...value.input_field_ids] as string[]),outputFieldId:value.output_field_id,status:value.status as ValidatedVolumetricRelationship["status"],residual:Number(value.residual)});
}

function validateDerivedCollinearSemantics(fields: readonly ValidatedVolumetricField[], relationships: readonly ValidatedVolumetricRelationship[], errors: string[]) {
  const byChannel = new Map(fields.flatMap((field) => field.spin ? [[field.spin.channel, field] as const] : []));
  const up = byChannel.get("spin_up");
  const down = byChannel.get("spin_down");
  const total = fields.find((field) => field.quantity === "electron_density" && field.fieldName === "total");
  const difference = byChannel.get("spin_difference");
  const formulas: Record<string, string> = { spin_up: "COLLINEAR_SPIN_UP_V1", spin_down: "COLLINEAR_SPIN_DOWN_V1" };
  for (const channel of ["spin_up", "spin_down"] as const) {
    const field = byChannel.get(channel);
    if (!field) continue;
    const formula = formulas[channel];
    const hasFormula = field.quantity === "spin_density"
      && field.unit === "electron/angstrom^3"
      && field.normalizationSemantics === "source_native"
      && field.integralSemantics === "electron_count"
      && field.provenance.transformations.some((item) => item.kind === "component_remapping" && item.detail.startsWith(`${formula}:`));
    if (!hasFormula) errors.push("VOLUME_DERIVED_FIELD_INVALID");
  }
  const relationKinds = new Set(relationships.map((relationship) => relationship.kind));
  if (relationKinds.size !== relationships.length) errors.push("VOLUME_RELATIONSHIP_INVALID");
  if (!up && !down && relationKinds.size) { errors.push("VOLUME_RELATIONSHIP_INVALID"); return; }
  if ((up || down) && (!up || !down || !total || !difference)) { errors.push("VOLUME_DERIVED_FIELD_INVALID"); return; }
  if (!up || !down || !total || !difference) return;
  const expected = [
    ["spin_difference_equals_up_minus_down", difference.fieldId, "collinear:spin_difference_equals_up_minus_down:v1"],
    ["total_equals_up_plus_down", total.fieldId, "collinear:total_equals_up_plus_down:v1"],
  ] as const;
  for (const [kind, outputFieldId, relationshipId] of expected) {
    const relationship = relationships.find((item) => item.kind === kind);
    if (!relationship || relationship.relationshipId !== relationshipId || relationship.status !== "validated" || Math.abs(relationship.residual) > 1e-12 || relationship.outputFieldId !== outputFieldId || relationship.inputFieldIds.length !== 2 || relationship.inputFieldIds[0] !== up.fieldId || relationship.inputFieldIds[1] !== down.fieldId) {
      errors.push("VOLUME_RELATIONSHIP_INVALID");
    }
  }
}

function failure(code:"VOLUME_VIEWER_CONTRACT_INVALID", errors:string[]):VolumetricValidationResult{return Object.freeze({ok:false,code,errors:Object.freeze([...new Set(errors)].sort())});}
function record(value:unknown):value is JsonRecord{return typeof value==="object"&&value!==null&&!Array.isArray(value)&&Object.getPrototypeOf(value)!==null;}
function exactKeys(value:JsonRecord,keys:readonly string[]){const actual=Object.keys(value).sort();return actual.length===keys.length&&actual.every((item,index)=>item===[...keys].sort()[index]);}
function finite(value:unknown){return typeof value==="number"&&Number.isFinite(value);}
function positiveInteger(value:unknown){return Number.isSafeInteger(value)&&Number(value)>0;}
function safeId(value:unknown){return typeof value==="string"&&SAFE_ID.test(value);}
function sha(value:unknown){return typeof value==="string"&&SHA256.test(value);}
function safeArtifactName(value:unknown){return typeof value==="string"&&value.length>0&&value.length<=128&&!value.includes("/")&&!value.includes("\\")&&!value.includes("..")&&SAFE_ID.test(value);}
function vector3(value:unknown):VolumeVector3|null{return Array.isArray(value)&&value.length===3&&value.every(finite)?Object.freeze(value.map(Number) as [number,number,number]):null;}
function int3(value:unknown):readonly[number,number,number]|null{return Array.isArray(value)&&value.length===3&&value.every(positiveInteger)?Object.freeze(value.map(Number) as [number,number,number]):null;}
function string3(value:unknown):readonly[string,string,string]|null{return Array.isArray(value)&&value.length===3&&value.every((item)=>typeof item==="string")?Object.freeze([...value] as [string,string,string]):null;}
function matrix3(value:unknown):VolumeMatrix3|null{if(!Array.isArray(value)||value.length!==3)return null;const rows=value.map(vector3);return rows.every(Boolean)?Object.freeze(rows as [VolumeVector3,VolumeVector3,VolumeVector3]):null;}
function determinant(matrix:VolumeMatrix3){const[a,b,c]=matrix;return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);}
function wellConditioned(matrix:VolumeMatrix3){const scale=Math.max(...matrix.flat().map(Math.abs));const det=Math.abs(determinant(matrix));return Number.isFinite(det)&&det>1e-12*Math.max(scale**3,1);}
function canonicalSecurity(value:unknown){return record(value)&&value.contains_javascript===false&&value.contains_html===false&&value.contains_css===false&&value.contains_shader===false&&value.contains_executable===false&&value.external_urls_allowed===false&&value.renderer_included===false;}
function scanInert(value:unknown,depth=0):void{if(depth>32)throw new Error("depth");if(Array.isArray(value)){if(value.length>16_777_216)throw new Error("size");value.forEach((item)=>scanInert(item,depth+1));return;}if(record(value)){for(const[key,item]of Object.entries(value)){if(FORBIDDEN_KEYS.has(key.toLowerCase()))throw new Error("key");scanInert(item,depth+1);}return;}if(typeof value==="string"&&FORBIDDEN_MARKERS.some((item)=>value.toLowerCase().includes(item)))throw new Error("marker");}
