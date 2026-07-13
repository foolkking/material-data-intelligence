# Measurement Evidence

`node apps/web/test/viewer-scene-advanced-picking-browser-evidence.mjs` runs a
real adapter-generated v2 flow in Chromium, Firefox, and WebKit. It performs
atom and visible-bond canvas picking, explicit and cross-boundary measurements,
keyboard distance/angle/dihedral/undo, local JSON download, mobile bond tap,
tab lifecycle, and synthetic context loss. Console and external network counts
must remain zero.
