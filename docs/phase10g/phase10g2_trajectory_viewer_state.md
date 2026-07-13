# Trajectory Viewer State

State separates current and requested frame indices and uses a monotonically increasing generation token. Defaults are paused at frame zero, 1x display speed, loop off, 1x1x1 display, bonds off, and no selection. Artifact changes reset frame/camera/cache; display-only supercell changes preserve the committed frame and clear measurement selection.

Typed terminal states cover invalid artifact, budget refusal, frame failure, unsupported renderer, and context loss. Every terminal state retains inert JSON access and allocates no replacement canvas.
