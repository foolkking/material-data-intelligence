# Phase 10M-3 Selection Inspector

The M2 Inspector now displays canonical selection kind, origin panel (or
URL/Pin provenance), Project, source-scope hash, all non-null exact identity
fields, and every panel's compatibility reason. Compatible entries provide a
bounded Open panel command.

Clear is explicit and keyboard-operable. Copy produces a canonical deep link.
Pin uses the existing Workspace PATCH with `If-Match`; conflicts remain typed
and no implicit save occurs. Read-only historical Workspaces may use transient
selection but cannot Pin.

The Inspector never renders Artifact payloads, provider prompts, executable
links, HTML, scripts, private paths, credentials, or unpersisted scientific
inference.
