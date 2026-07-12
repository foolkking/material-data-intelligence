# Periodic Bond Identity

Endpoint identity is `(site_index, image_offset)`. Canonicalization compares the forward tuple `(A,B,dx,dy,dz)` with reversed `(B,A,-dx,-dy,-dz)` and chooses the lexicographic minimum. The stable id is derived from that tuple.

Zero-offset self edges are invalid. Nonzero self-periodic edges are valid. Reverse and translation-equivalent candidates deduplicate to one topology edge. Ordering is the sorted canonical key and is independent of neighbor enumeration timing or renderer object ids.
