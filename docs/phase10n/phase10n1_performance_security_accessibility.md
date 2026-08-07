# Phase 10N-1 Performance, Security And Accessibility

Caps are 32 structures, 5,000 sites per request, 1,000 neighbors per site, 50,000
retained rows, 16 MiB artifact payload and 120 seconds runtime. Over-cap input is a
typed rejection. Development measurements do not claim production capacity.

Adapters use existing validated storage only. They have no shell, subprocess,
filesystem-path, network, notebook, dynamic-module or user-code authority. Artifact
content is inert and checksum/scope validation is mandatory. Secrets, storage keys,
private paths and stack traces are redacted.

The coordination UI exposes named algorithm controls, keyboard-selectable tables,
visible focus, live status, algorithm-qualified non-color labels, mobile reflow and a
text table alternative for the Structure Viewer. A WebGL surface is never the only
way to obtain a coordination value.
