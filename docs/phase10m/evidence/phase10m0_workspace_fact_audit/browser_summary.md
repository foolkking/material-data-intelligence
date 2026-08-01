# Current Browser Fact Summary

| Replay | Browser matrix | Cases | Live API | Live LLM | Console/page errors | External requests | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| L5 natural-language capture | Chromium, Firefox, WebKit; Chromium 390x844 | 5 ready + clarification + unsupported + capability mismatch | 0 | 0 | 0 | 0 | PASS for current UI replay |
| L4 interpretation capture | Chromium, Firefox, WebKit; Chromium 390x844 | ready/strict-provider/partial/no-evidence/validation/integrity | 0 | 0 | 0 | 0 | PASS for current UI replay |
| L3 dependency runner | not used as current PASS | interpretation GET interception missing | n/a | n/a | known fixture-only 404 | n/a | LIMITATION |

## Scenario mapping

- Empty/new analysis: L5 intercepted `GET /datasets` returned an empty list
  before demo dataset creation; current UI displayed the existing entry state.
- Dataset, ML, structure, phonon, and volumetric: L5 `case_1` through `case_5`.
- Clarification, unsupported, capability mismatch: L5 non-ready states.
- Multi-tool dependency and partial/blocked branch: L4/L3 persisted captures;
  L4 browser replay validates the partial interpretation disclosure and no
  execution authority.
- Grounded interpretation and evidence drill-down: L4 deterministic and
  strict-provider cases.
- Historical reload: `UNAVAILABLE` as a current product surface because no
  history or Workspace route exists; exact historical source records are
  inventory evidence only.
- Keyboard/accessibility: runner accessibility and focus snapshots; proposed
  Workspace keyboard behavior remains acceptance target, not current behavior.

## Current-code limitation

The existing L3 dependency browser runner predates the current interpretation
GET route interception and returns a fixture-only 404 in the current UI flow.
The runner was not edited; the result is retained as an honest limitation and
not elevated to current Workspace support.
