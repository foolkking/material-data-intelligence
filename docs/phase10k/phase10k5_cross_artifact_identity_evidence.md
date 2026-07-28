# Phase 10K-5 Cross-Artifact Identity Evidence

## Authority Chain

```text
normalized resources
  -> Material Data Profile 2.0
  -> exact dataset/Profile/resource binding
  -> independent K2/K3/K4 products
  -> application-owned frontend binding gate
```

The Profile is the only semantic authority. K2/K3/K4 do not rediscover formula,
property, task, uncertainty, class, or sample-ID roles.

## Dataset and Revision Identity

Products must agree exactly on dataset ID/version, Profile ID/contract/hash,
the canonical resource list, every normalized object hash, and the derived
dataset content hash. A stale semantic hash, content hash, object hash, object
set, Profile ID, or dataset version disables linking. No fallback to “latest”
Profile is permitted during persisted job execution.

## Sample Identity

The canonical cross-product key is:

```text
sampleKey = objectId + ":" + sampleRef
```

The evidence records one source material in Dataset Explorer, Materials ML,
and Composition Space and verifies equality. Duplicate `sampleRef` values in
different objects remain distinct. Missing/inconsistent keys and duplicate K2
keys are rejected before product rendering.

## Dependent ML Artifacts

Composition Space only consumes exact allowlisted K3 regression/uncertainty v1
artifacts. The artifact binding must match the active Profile and all sample
rows must carry a valid object-qualified key and non-negative row index.
Displayed ML coverage includes total, matched, and missing sample counts; units
come from the K3 artifact and are not inferred in the browser.

Evidence:

* `integration/cross_artifact_sample_identity.json`
* `integration/exact_version_binding.json`
* `integration/profile_authority.json`
* `integration/partial_failure_isolation.json`
