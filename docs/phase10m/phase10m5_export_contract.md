# Phase 10M-5 Export Contract

Mandatory exports are canonical JSON and UTF-8 LF-normalized Markdown. Both are
generated from the persisted immutable Report/Recipe pair, never recomposed
from current Workspace “latest” state.

Canonical JSON contains the Report snapshot, Recipe manifest, export manifest,
exact source refs, warnings/limitations, hashes, and no-execution flags with
sorted keys. Markdown uses deterministic templates, no raw HTML or remote
assets, and retains identifiers, all disclosures, provenance, and Recipe ref.

`ReportExportManifest 1.0` records pair IDs/hashes, format, renderer contract,
source refs, content checksum/size, generated timestamp outside semantic hash,
authorization scope, omitted payload reasons, coverage, and
`executionAuthorized=false`. Server-generated filenames prevent traversal and
Content-Disposition injection. Exports are capped at 2,097,152 bytes.

PDF, DOCX, LaTeX, PPTX, HTML/WYSIWYG, video, and remote publication are outside
M5 and cannot substitute for JSON/Markdown.
