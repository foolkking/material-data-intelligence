# UX-V1.3 Design Documentation + High-Fidelity Prototype

This directory is the production-design source of truth for the Material Agent Platform after the Product Architecture Code Audit and UX-V1.1/V1.2 direction/specification work.

It is intentionally separate from `apps/web/`. The prototype uses stable local material-science fixtures and no production API, database, queue, route, or component. It demonstrates target interaction and visual behavior; `00-context-and-frozen-decisions.md` and `12-open-decisions.md` distinguish it from capabilities that exist today.

## Start the prototype

```powershell
cd design/ux-v1.3/prototype
python -m http.server 4173
```

Open `http://127.0.0.1:4173/#landing`. The fixed **原型审阅控件** panel is review-only. It changes pages, scientific viewers, authentication state, and research states without representing a production control.

## Document map

- `00-context-and-frozen-decisions.md`: backend truth, product model, scope boundary.
- `01-reference-research.md`: browser-observed reference research and extraction.
- `02-visual-direction.md` and `03-design-system.md`: art direction and tokens.
- `04-global-shell-and-navigation.md` through `08-result-inspector-report-spec.md`: concrete layouts and interaction contracts.
- `09-state-matrix.md`: state, source-of-truth, and user-facing language.
- `10-responsive-accessibility-motion.md`: geometry and behavioral requirements.
- `11-prototype-validation.md`: Chrome evidence, review results, and implementation corrections.
- `12-open-decisions.md`: only the choices still needing Product Owner judgment.
- `13-design-closure.md`: UX-V1.3.1 closure changes, final evidence revision, and readiness gate.

`../../.interface-design/system.md` is the long-lived visual-system authority for later production UI work.
