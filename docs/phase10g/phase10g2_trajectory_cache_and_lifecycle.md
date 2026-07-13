# Trajectory Cache and Lifecycle

Mapped display frames use deterministic LRU eviction: seven desktop interactive frames / 16 MiB, four degraded frames / 8 MiB, or three mobile frames / 4 MiB. The cache stores no renderer objects and never preloads all frames. Generation tokens discard stale seek results.

Artifact switch, unmount, refusal, and context loss cancel playback, clear cache/selection/measurement, remove listeners, dispose renderer resources, and prevent stale commits. Context recovery is user-triggered and remains paused.
