# Phase 10N-3 Registry, Profile and Planner Integration

Registry grows from 56 to 57 with exactly `structure.experimental_xrd_comparison@0.1.0`. `structure.xrd@0.1.0` remains the only theoretical XRD authority and exposes `phase10e4.xrd_pattern.v1` through the existing AnalysisPlan 0.2 dependency port.

DataProfile 2.2 reports one exact experimental XRD resource. Eligibility requires explicit units/wavelength and compatible experimental/theoretical sources. Deterministic and mock Planner paths preserve exact source binding; ambiguous resources are not selected by filename, order or latest. PlanValidator and Runtime retain existing Registry/Adapter authority and reject stale, foreign or checksum-mismatched sources.
