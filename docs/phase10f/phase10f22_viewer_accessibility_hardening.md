# Phase 10F-22 Viewer Accessibility Hardening

The renderer now exposes a focusable region, bounded keyboard camera controls,
a synchronized semantic scene summary, polite selection announcements, and a
capped semantic periodic-neighbor table. Mobile controls have 44px targets and
the canvas preserves vertical page scrolling with `touch-action: pan-y`.

Reduced-motion and forced-colors policies are application-owned. No artifact
field controls roles, focus, shortcuts, events, or accessibility text structure.
