# Viewer Accessibility Security

ARIA names, roles, shortcuts, focus targets, announcements, table structure,
touch policy, and media-query behavior are application-owned. Artifact strings
remain escaped text and cannot become HTML, handlers, roles, IDs, shortcuts, or
live-region payloads. Neighbor DOM rows are capped at 100. No dependency,
telemetry, remote font/icon, network service, or artifact execution was added.
