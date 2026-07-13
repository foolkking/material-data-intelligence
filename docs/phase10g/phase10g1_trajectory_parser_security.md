# Parser Security

Input byte size is checked by stat before parsing. EXTXYZ uses bounded UTF-8 line iteration: 64 MB input, 65,536-byte line, 8192-byte comment, 32 metadata keys, 64 row tokens, and inherited atom/frame/value/output caps. Canonical JSON is byte-capped before decode and then contract/depth validated.

No eval, literal-eval, pickle, dynamic import, plugin, shell, notebook, archive extraction, symlink traversal, URL, remote frame, callback, HTML/JS, telemetry, or arbitrary MIME is used. Errors expose typed codes and safe summaries only. File contexts close on failure/cancellation; partial artifacts are emitted only after complete validation.
