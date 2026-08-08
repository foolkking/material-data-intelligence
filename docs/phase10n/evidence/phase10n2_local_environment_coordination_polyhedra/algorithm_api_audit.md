# Locked Algorithm API Audit

The implementation uses locked `pymatgen 2026.5.4` structure inputs and locked
`numpy 2.4.6` numeric operations. The bounded face backend uses locked
`scipy 1.17.1` `scipy.spatial.ConvexHull`. No ChemEnv extra, package upgrade,
remote service or runtime install is used. Geometry classification is repository
owned and consumes the N1 relation vectors without neighbor discovery.
