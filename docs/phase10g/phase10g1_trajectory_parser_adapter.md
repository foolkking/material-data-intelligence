# Phase 10G-1 Trajectory Parser / Adapter

Phase 10G-1 implements real bounded ingestion for multi-frame Extended XYZ and canonical `phase10g.trajectory.v1` JSON. The parser normalizes to the existing contract, validates before persistence, and creates one `Trajectory` normalized object. The planner-hidden `structure.trajectory_import` adapter then emits inert trajectory, summary, parse report, and manifest JSON through validated Plan/QueueWorkerRuntime execution.

Single-frame EXTXYZ retains the existing static Structure behavior. Plain XYZ trajectory import is deferred because v1 has no absent-lattice mode; no synthetic cell is created. Viewer, playback, dynamic bonds, analysis, remote sources, archives, and formal product registration remain out of scope.
