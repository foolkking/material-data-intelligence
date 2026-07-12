# Phase 10F-15 Browser Compatibility

The production runner used live formal-tool artifacts in:

- Chromium 149: WebGL 2 rendered; interactions and all boundary cases passed.
- Firefox 128: WebGL 2 rendered; rotate, zoom, reset, lifecycle, console, and network audits passed.
- WebKit 18: WebGL 2 rendered; rotate, zoom, reset, lifecycle, console, and network audits passed.

Browser binaries are test tooling only and are not application dependencies. No renderer runtime request reached an external host.
