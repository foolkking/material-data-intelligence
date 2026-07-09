# Phase 10F-10 Test Transcript

## Targeted Frontend Test

Command:

```text
npm --prefix apps/web test -- PlannerWorkbench.test.tsx
```

Result:

```text
PASS
1 test file passed
11 tests passed
```

Covered:

- existing PlannerWorkbench behavior;
- Phase 10D static viewer scene preview regression;
- Phase 10F-10 `viewer_scene.v1` JSON-only preview;
- Phase 10F-10 manifest JSON-only preview;
- warning/caps display;
- invalid fixture validation errors;
- renderer-free and external-resource-free fixture sample scan.
