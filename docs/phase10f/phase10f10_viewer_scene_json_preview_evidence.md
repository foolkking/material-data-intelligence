# Phase 10F-10 Viewer Scene JSON Preview Evidence

## 1. Evidence Scope

- Frontend evidence: implemented through `apps/web/app/components/PlannerWorkbench.test.tsx`.
- API evidence: fixture-backed mock planner/job artifact responses are replayed through the existing workbench fetch flow.
- Browser evidence: jsdom-based frontend evidence is complete; real browser screenshot evidence remains optional and was not required to add a renderer.
- Renderer evidence: deferred.

## 2. Fixture-backed Samples

The frontend evidence covers these Phase 10F-9 contract samples:

| Fixture | Preview Result |
|---|---|
| `valid_minimal_crystal.viewer_scene.v1.json` | JSON-only summary renders |
| `valid_multi_species_crystal.viewer_scene.v1.json` | Included in renderer-free fixture sample scan |
| `valid_optional_bonds.viewer_scene.v1.json` | Included in renderer-free fixture sample scan |
| `valid_warning_caps.viewer_scene.v1.json` | warnings and caps render |
| `invalid_nan_coordinate.viewer_scene.v1.json` | included in invalid fixture inertness scan |
| `invalid_external_resource_reference.viewer_scene.v1.json` | validation errors render |
| `invalid_executable_field.viewer_scene.v1.json` | included in invalid fixture inertness scan |
| `invalid_schema_version.viewer_scene.v1.json` | included in invalid fixture inertness scan |

## 3. Frontend Test Evidence

Targeted command:

```text
npm --prefix apps/web test -- PlannerWorkbench.test.tsx
```

Observed result:

```text
1 test file passed
11 tests passed
```

The added tests verify:

- valid `viewer_scene.v1` fixture renders kind, version, schema version, validation state, scene summary, and manifest metadata;
- warning/caps fixture renders warning codes and cap values;
- invalid external-resource placeholder fixture renders validation errors without executing payload content;
- fixture samples contain no real external URL, script marker, WebGL marker, or Three.js marker;
- no canvas, script, or iframe element is created by the preview.

## 4. API Evidence Boundary

The evidence uses the existing PlannerWorkbench fetch mock and existing `/planner/jobs/job_1/artifacts` and `/planner/jobs/job_1/result` response shape. It does not add a production runtime API route.

## 5. Browser Evidence Boundary

The implemented preview runs in the existing React artifact preview surface under jsdom tests. No real browser screenshot was added in this phase. Future real-browser evidence can reuse the Phase 10E screenshot workflow after a reviewer asks for screenshot capture.

## 6. Conclusion

PASS for JSON-only preview evidence. Renderer and real-browser screenshot evidence remain deferred and are not prerequisites for this non-renderer phase.
