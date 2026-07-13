# Phase 10G-2 Trajectory Viewer

Validated `phase10g.trajectory.v1` artifacts now drive a real Three.js trajectory surface through PlannerWorkbench. The surface initializes one shared renderer engine, commits frame zero paused, and updates existing instanced atom matrices and line buffers without rebuilding renderer, mesh, geometry, material, controls, or camera on each frame.

The planner-hidden `structure.trajectory_import` remains the producer. `structure.viewer_3d` remains static, and no formal trajectory viewer tool is registered. Static reference bonds are PARTIAL_READY and off by default; dynamic bond inference is prohibited.
