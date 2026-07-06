# ward_formula_statistics platform result summary

## 1. Verdict
PASS

## 2. Evidence level
Tool Registry + Adapter execution only. No browser screenshots or HTTP API captures are claimed for Phase 10B-1.

## 3. Source benchmark case
- case_id: ward_metallic_glasses_csv_xz
- case_type: direct_uploadable_data
- verification_status: DIRECT_VERIFIED

## 4. Adapter
- toolId: `composition.formula_statistics`
- params: `{"formulaColumn": "composition", "maxExamples": 20, "strict": false}`
- rowCount: 8415

## 5. Artifacts
- table_json: `sample_artifacts/formula_statistics.json`
- summary_md: `sample_artifacts/summary.md`
- recipe_json: `sample_artifacts/recipe.json`

## 6. Boundaries
- uses real LLM: no
- uses browser/API evidence: no
- modifies benchmark pack: no
- unsupported official examples claimed: no
