# Phase 10F-18 Integrated Plan

Baseline: `bfca00d4c93ab2bd16966b237d850bd33206c20c` on `master`, clean.

The closure order is contract, adapter, frontend mapper/renderer, inspector, evidence, security, regression, then current-HEAD CI. The trust boundary remains inert artifact JSON -> independent frontend validation -> whitelist mapper -> renderer-local geometry. No backend rendering or artifact execution is introduced.

Acceptance requires v1 compatibility, v2 periodic endpoints, orthogonal and triclinic live adapter cases, deterministic deduplication, bounded supercell replication, three-browser evidence, zero external topology requests, and clean CI closure.
