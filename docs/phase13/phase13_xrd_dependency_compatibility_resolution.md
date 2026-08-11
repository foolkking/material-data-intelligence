# Phase 13 XRD Dependency Compatibility Resolution

Decision: `Branch B1`. The current `structure.xrd@0.1.0` Tool contract accepts the allowlisted `CuKa` radiation configuration and does not accept an arbitrary wavelength parameter. Its approved backend reports `1.54184 angstrom`. The Demo 3 experimental fixture now carries that exact existing configuration, with source identity and checksum sealed in the current fixture registry.

The comparison Adapter remains strict: any theoretical/experimental wavelength mismatch is rejected. No conversion, reprojection, tolerance change, peak-policy change or LLM wavelength authority was introduced.
