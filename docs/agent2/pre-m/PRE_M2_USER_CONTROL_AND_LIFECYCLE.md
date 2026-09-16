# Pre-M2 User Scientific Control & Lifecycle

Status: `PASS_WITH_CURRENT_CONTRACTS`  
Date: 2026-09-11

## Parameter authority

The existing contracts already distinguish effective values by origin:

```text
USER_EXPLICIT
CONTEXT_RESOLVED
AGENT_DERIVED
```

Together with strict Tool schemas, exact source/version binding and immutable
AnalysisPlan/Result persistence, these implement the required product meaning:

| Product meaning | Current authority |
|---|---|
| `SOURCE_LOCKED` | exact ScientificObjectVersion / Result dependency |
| `AUTO_DERIVED` | validated Result-grounded dependency value |
| `USER_EDITABLE` | explicit validated plan parameter |
| `ADVANCED_EDITABLE` | explicit validated bounded method parameter |
| `SYSTEM_ONLY` | registry/policy-controlled execution value |

Changing a scientific parameter creates a new validated AnalysisPlan and a new
Result. It never overwrites an existing Result. Presentation-only changes do
not recompute science; reinterpretation creates a new Interpretation; source
changes require an exact new source version.

## Preferences

Interface and presentation preferences remain frontend/user presentation state.
Any preference or preset capable of changing a ScientificResult must resolve
into the AnalysisPlan with its effective value and origin. There is no hidden
scientific preference authority and no unified AI “Expert Mode”.

## History, partial ingestion and search

- Historical objects use explicit active/archive/trash/invalidation/missing
  states and retain exact versions. No silent current-version rebinding occurs.
- Transport integrity and scientific parse/admission are distinct. Independent
  resources may be partially ready; an unavailable dependency blocks only the
  affected Capability.
- Search obeys `Found != Added != Used`. Opening a result is navigation.
  Selecting “ask with this” creates a Context candidate; only the submitted
  Turn's persisted ContextSnapshot records actual use.

## Explicit limit

Pre-M2 did not add a large generic parameter/preferences system. The existing
authority contracts satisfy V0 semantics; richer method controls may be added
only capability-by-capability without changing these boundaries.
