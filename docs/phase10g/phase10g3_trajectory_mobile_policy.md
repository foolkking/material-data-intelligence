# Phase 10G-3 Trajectory Mobile Policy

Mobile uses independent application-owned budgets: 15 fps maximum, 3/4 MiB interactive cache, 2/2 MiB degraded cache, 192 interactive instances, and 384 hard displayed-instance limit. Prefetch remains zero and bonds remain off.

Mobile identity is detected conservatively from a narrow viewport, a short landscape dimension, or touch capability. The Next root layout declares device-width viewport metadata, so 390 x 844 and 844 x 390 evidence use real CSS viewport dimensions. Orientation does not promote the viewer to desktop budgets.

Chromium and WebKit evidence covers product entry, next-frame touch, speed, loop, touch distance selection, 2 x 2 x 2 display, orientation resize, one canvas/context, no local control overflow, and a 400-atom mobile refusal before WebGL. `touch-action: pan-y` preserves page scrolling.

Physical-device thermal behavior and broad hardware GPU coverage remain outside automated evidence.
