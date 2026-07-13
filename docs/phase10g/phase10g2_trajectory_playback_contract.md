# Trajectory Playback Contract

Forward display playback supports 0.25x, 0.5x, 1x, 2x, and 4x. Interactive desktop is capped at 30 fps; degraded/mobile is capped at 15 fps. Display speed is not physical-time scale and never skips a scientific frame silently.

Loop off pauses on the final frame; loop on returns to frame zero. At most one timer exists. Pause, hidden tab, unmount, artifact switch, context loss, refusal, and error cancel it. Returning to a visible tab remains paused. Reduced-motion never auto-plays and uses no interpolation.
