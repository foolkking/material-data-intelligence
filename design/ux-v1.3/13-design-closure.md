# UX_V1_3_1_DESIGN_CLOSURE

## 1. Closure scope

UX-V1.3.1 closed language consistency, Complete-state hierarchy, Data toolbar duplication, GlobalBar ownership, Landing authentication states, prototype reviewer annotation leakage, table density, and keyboard behavior. It did not alter product code, backend capability, CI, workflows, or the frozen Scientific Research Workbench direction.

**Closure revision:** `UX-V1.3.1-final-2026-08-18`.

## 2. Language policy

`PRODUCT_CHROME_LANGUAGE = zh-CN`. Navigation, state names, dialogs, controls, Inspector and Report labels are Simplified Chinese. Material formulas, user-created names, filenames, units, source properties and established abbreviations remain canonical where scientifically useful. Raw contract language is limited to progressive technical disclosure.

## 3. Research state hierarchy

| State | Final layout rule |
| --- | --- |
| Running | Activity rail plus live result. Current named scientific work and an already persisted artifact may coexist. |
| Complete | Full-width compact `分析完成 · 4 个步骤` summary; process history is closed by default; Figure/result owns recovered width. |
| Partial | Retain fuller activity context with preserved output and limitation. |
| Failed | Retain fuller activity context with preserved output, failed step and scoped recovery. |

Chrome final geometry confirmed the correction: Running used a `224px` Activity rail; Complete used a `44.7px` full-width summary and a `1222.8px` result surface.

## 4. Global and Data action cleanup

GlobalBar now contains brand, current context, search and account identity only. Context commands live beside their objects: Console has `查看相关数据`, Data has `研究此数据`, and Research owns `查看数据`. The formal Data Viewer has no duplicate `预览` or permanent `详情` action; scientific selection opens Inspector.

## 5. Landing authentication states

Logged-out Landing exposes `登录` and `开始使用`; the latter opens the same modal. The modal contains only email, password and login action geometry, without claiming an implemented authentication method. Logged-in prototype state changes the entry to `进入控制台` with an account avatar.

## 6. Prototype annotation cleanup

Reviewer/backend/prototype explanations were removed from user-visible Data and Research surfaces. The sole revision note is confined to `原型审阅控件`, which is explicitly review-only and outside product UI. Chrome state scans found no reviewer annotation wording inside Research.

## 7. Table density

The final default is `40px` for table rows and headers (`39.98px` actual Chrome layout), with 13px data and 12px units. This passed the Data/Table geometry check without losing selection clarity, sticky headers or Inspector space. A 42px mode remains an optional comfortable density, not the default.

## 8. Accessibility closure

| Check | Result |
| --- | --- |
| Login focus entry, Tab/Shift+Tab trap, Escape and restoration | PASS in Chrome |
| Inspector Escape/restoration | PASS in Chrome |
| Quick Preview Escape/restoration | PASS in Chrome |
| Structure selection keyboard | PASS in Chrome |
| Splitter ArrowLeft/ArrowRight | implemented and source-reviewed; final visual evidence not captured |
| Reduced motion | CSS contract present; OS preference toggle NOT VERIFIED |
| 200% browser zoom | NOT VERIFIED: Ctrl-plus did not change browser metrics |

## 9. Final evidence revision

The final source identity is `UX-V1.3.1-final-2026-08-18`. Chrome saved and visually reviewed final `1920x1200` Landing logged-out and Login Modal screenshots; requested viewport overrides did not apply, and later capture calls were intermittent. `evidence/closure/` deliberately contains no stale or relabelled screenshot.

## 10. Final Chrome validation

Chrome opened the final prototype at actual `1920x1200`, exercised Landing login, Console Quick Preview, Data table/structure/Inspector, Research all nine states, and keyboard/Escape flows. It confirmed the discrete Activity-versus-Complete result hierarchy and the final table/Inspector geometry. Final screenshots exist for Landing logged-out and Login Modal only; it could not provide the full required screenshot set at `1920x1080`, `1440x900`, `1280x800`, or `390x844`.

## 11. Design review and deslop

**Design review:** PASS for the repaired Complete focal point, running-state truthfulness, action ownership, density and Chinese product chrome in the final DOM/geometry pass.

**Design deslop:** PASS for no generic AI gradient/glass/purple palette, no card-per-section composition, no raw IDs or workspace term in default product flow, no fake progress/streaming, no permanent infrastructure state, and no reviewer notes in product UI.

Final screenshot-dependent visual review remains **NOT VERIFIED**, rather than being folded into either review result.

## 12. Remaining open decisions

1. Product and backend owners must choose the actual authentication method.
2. A Chrome environment with working final screenshot capture and viewport override must repeat the final evidence matrix before production implementation acceptance.
3. Production implementation must validate font loading, OS reduced motion, true 200% zoom, screen-reader behavior, mobile hardware and real data payloads.

## 13. Production design readiness

The design rules, page/state specifications and isolated prototype are frozen. However, the explicit UX-V1.3.1 final-evidence gate is not met: `FINAL_SCREENSHOT_EVIDENCE = NOT_VERIFIED`. Therefore:

```text
DESIGN_READY_FOR_PRODUCTION_IMPLEMENTATION = NO
```

This is a design QA/evidence blocker, not a request to modify production UI or backend.
