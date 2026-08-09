# Phase 10N-4 Artifact Contracts

Three strict families are registered: `phase10n4.trajectory_rdf.v1`, `phase10n4.trajectory_msd.v1`, and `phase10n4.trajectory_diffusion.v1`. Each records exact Tool/Adapter version, project/dataset/job/plan/tool-call scope, trajectory identity, resolved parameters and hash, locked scientific stack, units, coverage, warnings, limitations, runtime diagnostics, and stable content checksum.

RDF stores pair identity, window/frame identities, exact bin IDs/edges/centers, `g(r)`, pair counts, normalization, and cell/PBC policy. MSD stores series/lag identities, unwrapping authority, time/cell policy, atom/species selection, MSD arrays, and origin counts. Diffusion stores exact source MSD Artifact ID/checksum, explicit fit-window identity, OLS diagnostics, regime diagnostic identity/status, and a qualified estimate or explicit unavailability.

Artifacts do not duplicate the trajectory or unwrapped coordinates. Diffusion does not duplicate the full MSD Artifact. Recipe payloads are declarative and non-executable.
