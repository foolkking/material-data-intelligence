# Product Maturity — Payload Recovery Entry UX Batch

Date: 2026-09-01

## Finding

The same-stack runtime is healthy (`PostgreSQL`, `Redis`, `MinIO`, and Redis
workers all report `ok`). Some historical synthetic records still have no
recoverable payload bytes. Those records must remain fail-closed rather than
being replaced with another source version or fabricated content.

The existing UI correctly distinguishes a transient storage read failure from
a confirmed missing payload, but the confirmed-missing state did not provide a
direct recovery action and repeated fallback instances could reuse a generic
DOM id.

## Bounded repair

`ScientificDataView` now:

- offers a project-scoped `重新导入源文件` link when the server confirms the
  exact normalized payload is unavailable;
- retains the existing metadata/source inspection and retry actions;
- gives each fallback heading a dataset/kind-scoped id and matching
  `aria-labelledby` relationship.

`ScientificResultViewer` now also offers a project-scoped `返回数据源` link
when a result Artifact is missing or temporarily unreadable, so users can
inspect the preserved Dataset/source metadata without constructing a URL or
silently switching to a different Result.

This is a presentation and recovery bridge only. It does not create, mutate,
or substitute any `ScientificObject`, `ScientificObjectVersion`,
`ScientificResult`, `Artifact`, or `Report`.

## Verification

- ProductPages, ProductShell, ProjectHome and DatasetWorkbench focused tests:
  `61 passed`.
- ScientificViewerAdapter effect tests: `8 passed`.
- TypeScript typecheck: PASS.
- Production Next build: PASS.
- API compileall: PASS.
- `git diff --check`: PASS (existing LF/CRLF normalization warnings only).
- `/health/runtime`: PostgreSQL/Redis/MinIO/Redis worker/DeepSeek `ok`.
- Existing authenticated browser tab and all services remain running.
