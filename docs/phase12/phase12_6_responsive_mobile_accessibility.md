# Phase 12-6 Responsive, Mobile, and Accessibility Closure

Phase 12-6 closes responsive and accessibility engineering across the existing
Planner and one-Workspace-per-Job product. The sealed viewports are `1440x900`,
`1280x720`, `390x844`, and a 200% zoom/reflow proxy. Mobile retains one active
Workspace panel, a context drawer, panel switcher, and Inspector bottom sheet.

The implementation adds skip navigation, keyboard-operable resizing, explicit
expanded state, bounded scientific-table scrolling, long-identity wrapping,
forced-colors focus treatment, reduced-motion handling, and shared 44px touch
targets. It does not change routes, scientific payloads, Workspace identity,
selection semantics, Report/Recipe authority, backend behavior, or scientific
claims. `UX-006` and `UX-009` are the only owned problems closed here.

Screen-reader closure is reported as `PASS_BY_DOM_ARIA_AND_BROWSER_EVIDENCE`.
No claim of NVDA, JAWS, VoiceOver, WCAG certification, or formal accessibility
certification is made.
