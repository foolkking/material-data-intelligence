# Phase 10F-27 structure.viewer_3d Capabilities

| Capability | Status |
| --- | --- |
| canonical periodic scene v2 | supported |
| atoms, lattice, bounded periodic bonds | supported |
| cross-boundary and self-periodic topology | supported, non-authoritative |
| picking and periodic inspector | supported |
| distance, angle, signed dihedral | supported |
| renderer-local bounded supercell | supported |
| clipping and deterministic camera controls | supported |
| local PNG/JSON/Markdown scientific export | supported |
| accessibility/mobile/JSON fallback | supported |
| trajectory/animation | unsupported |
| phonon/Brillouin/volumetric | unsupported |
| structure editing | unsupported |
| authoritative chemistry, valence, bond order | unsupported |

Distance-cutoff topology is a visual neighbor graph and remains explicitly
non-authoritative. Renderer-local view state never mutates the source structure
or canonical artifact.
