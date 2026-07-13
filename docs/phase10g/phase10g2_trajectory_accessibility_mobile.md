# Trajectory Accessibility and Mobile

The named trajectory region exposes current/total frame, paused/playing state, speed, loop, wrapping, and lattice mode. Buttons, slider, speed, loop, selection modes, supercell, cell, clipping, and fit action are keyboard operable. Arrow/Home/End/Space shortcuts are scoped to the focused region and never intercept inputs.

Live announcements are bounded and automatic playback does not announce every frame. Application-owned viewport detection switches mobile controls to 44 px minimum targets, single-column layout, a 15 fps cap, three-frame / 4 MiB cache, touch picking, and `pan-y` canvas behavior without scroll lock. Resize listeners are removed on unmount.
