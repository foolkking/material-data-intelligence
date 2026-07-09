# Phase 10F-8 Viewer Scene Validation Contract

## 1. Purpose

The validation contract converts Phase 10F-7 input and size caps into a contract draft for inert viewer-scene JSON. It is planning-only and does not add validator code.

## 2. Draft Caps

| Cap | Draft Value | Contract Behavior |
|---|---:|---|
| `max_sites` | 256 | Reject or deterministically truncate with warning before artifact write. |
| `max_bonds` | 2048 | Reject or deterministically truncate with warning before artifact write. |
| `max_unit_cell_edges` | 12 | Unit-cell edge records must stay bounded. |
| `max_species` | 32 | Reject scenes that exceed species cap unless a reviewed truncation policy exists. |
| `max_cell_expansion` | `[1, 1, 1]` | v1 must not auto-expand supercells beyond the input cell. |
| `max_scene_json_bytes` | 1000000 | Reject artifact payloads above the cap. |

## 3. Numeric Validation

- Coordinates, lattice vectors, lattice parameters, radii, bond distances, and camera numeric hints must be finite JSON numbers.
- `NaN`, `Infinity`, `-Infinity`, stringified numeric sentinels, and null numeric placeholders are invalid where numeric fields are required.
- Coordinate arrays must have exactly three finite numbers.
- Lattice vectors must be a 3x3 matrix of finite numbers when present.
- Occupancies must be finite and non-negative when present.
- Bond distances must be finite and positive when present.

## 4. Structure Validation

| Area | Requirement |
|---|---|
| sites | Stable integer `index`, element label, and position required. |
| species | Must match site elements after normalization. |
| lattice | Required for periodic scenes; optional for non-periodic scenes only if future policy approves non-periodic inputs. |
| bonds | Optional; if present, endpoints must reference valid site indices. |
| cell expansion | Metadata only; renderer must not expand beyond cap. |
| style | Optional advisory data only. |
| warnings | Stable warning code/message objects or stable strings. |

## 5. Security Validation

The validation contract rejects:

- external URL references;
- absolute local file paths intended for renderer loading;
- script-like fields such as `script`, `javascript`, `onload`, `onclick`, `eval`, `callback`, `function`, `html`, `src`, `href`, or `dynamic_import`;
- renderer bundle references;
- compressed executable payload markers;
- artifact-provided shader code or executable material definitions.

## 6. Reject vs Warning Policy

| Condition | Policy |
|---|---|
| Missing required top-level field | reject |
| Invalid `kind`, `version`, or `schema_version` | reject |
| Non-finite required numeric value | reject |
| External resource reference | reject |
| Script-like or executable field | reject |
| Payload exceeds `max_scene_json_bytes` | reject |
| Site or bond count exceeds caps | reject unless deterministic truncation is explicitly recorded |
| Optional bonds omitted | warning or no warning, depending on producer policy |
| Style hints omitted or ignored | no warning required |
| Unknown forward-compatible optional field | warning only if it affects renderer/security behavior |

## 7. Validation Object

The artifact should include a validation summary:

```json
{
  "validation": {
    "status": "passed",
    "validated_in_phase": "contract_planning",
    "finite_numbers": true,
    "caps_enforced": true,
    "external_resources_detected": false,
    "scriptable_fields_detected": false,
    "truncated": false
  }
}
```

Implementation phases must replace `contract_planning` with the actual validation phase/tool.
