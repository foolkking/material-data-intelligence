# Phase 12-5 Preview, Finalization, and History

Draft state is session-only and protected against accidental unload. Preview
persists neither Report nor Recipe and creates no execution record. Finalize
requires an explicit confirmation that the persisted pair is immutable and
non-executing. History opens exact report IDs and retains legacy read-only
records without upgrading them.
