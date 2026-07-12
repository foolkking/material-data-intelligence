# Viewer Mobile Interaction Contract

OrbitControls retains its pointer implementation, but the application resets
its inline touch policy to `pan-y`: horizontal/intentional viewer gestures work
while page vertical scrolling remains available. Mobile controls are at least
44px, inspector content scrolls independently, and neighbor tables use bounded
horizontal overflow. Portrait/landscape resize must retain one canvas.
