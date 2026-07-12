# Phase 10F-15 Mobile and Resize

Chrome evidence covers 390x844 portrait and 844x390 landscape with touch enabled and DPR 2.

- no horizontal overflow;
- one canvas before and after resize;
- drawing buffer remains finite and bounded by DPR cap 2;
- controls wrap into touch-sized 44 px minimum targets;
- renderer canvas uses local `touch-action: none`, without locking page scroll globally;
- JSON fallback and tabs remain available.

This is a mobile baseline, not a full device/GPU matrix.
