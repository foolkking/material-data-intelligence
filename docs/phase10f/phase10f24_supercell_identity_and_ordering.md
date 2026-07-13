# Phase 10F-24 Supercell Identity and Ordering

Displayed atoms retain `PeriodicSiteRef {siteIndex,imageOffset}`. Ordering is lexicographic image offset followed by canonical site index. Cartesian translation uses the existing row-vector lattice helper and supports orthogonal and triclinic cells. Apply/reset clears active selection and unfinished measurement state; the canonical site index is never replaced by a display index.
