# Phase 10L-1 Bounded Clarification Contract

Clarification is restricted to one round and at most three questions. Supported
question forms are `SELECT_ONE`, `SELECT_MANY`, and `CONFIRM`; the implemented
deterministic path uses exact Profile/resource choices rather than free text.

Each question has a stable ID/code, inert prompt, type, exact options,
required flag, and one allowlisted binding target. Options must match current
Profile resource identity or target semantic identity. An answer binds the
parent intent ID, question ID, exact selected value, and expected Profile
semantic hash.

Successful answers create a new immutable intent with a parent link, a new
semantic hash, answer provenance, and round `1`. They never edit an
`AnalysisPlan`, choose a tool, create a job, or enqueue work. Unknown options,
duplicate/missing answers, stale Profile/resource identity, unsupported bind
targets, and second-round attempts are typed failures. If blocking ambiguity
remains after the single round, the request terminates as unsupported.
