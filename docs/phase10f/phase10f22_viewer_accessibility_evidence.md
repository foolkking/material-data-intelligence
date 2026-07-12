# Viewer Accessibility Evidence

The Phase 10F-22 runner extends the real production Playwright matrix. It
asserts keyboard camera changes, focusable region and shortcuts, bounded scene
summary, polite live region, reduced-motion context, mobile touch action, 44px
targets, orientation resize, one canvas, console safety, and zero external
requests in Chromium, Firefox, and WebKit.

The matrix applies 200% document zoom and verifies the viewer region and reset
control remain operable. Forced-colors is requested per browser and the actual
support state is captured; unsupported CI emulation remains a documented limit.
