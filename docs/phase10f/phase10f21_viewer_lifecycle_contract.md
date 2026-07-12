# Viewer Lifecycle Contract

Each engine initialization receives a monotonically increasing React-local
generation. Cleanup invalidates that generation. A late engine is disposed
immediately and cannot publish state. Disposal disconnects ResizeObserver,
removes window/control/pointer/context listeners, disposes all geometries and
materials, forces context loss, removes the canvas, and clears evidence state.

Rendering occurs only on initialization, controls change, resize, visibility,
selection, reset, or export. There is no continuous RAF loop.
