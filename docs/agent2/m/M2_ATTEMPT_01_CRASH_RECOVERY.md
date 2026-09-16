# MDI V0 — M2

# CRASH RECOVERY AND IDEMPOTENT SCIENTIFIC PUBLICATION

# attempt-01

# M1 EXTERNALLY ACCEPTED

# STOP BEFORE M3

Authoritative current program state:

```text
R0      = ACCEPTED

Pre-M0  = ACCEPTED
Pre-M1  = ACCEPTED
Pre-M2  = ACCEPTED
Pre-M3  = ACCEPTED
Pre-M4  = ACCEPTED
Pre-M5  = ACCEPTED
Pre-M6  = ACCEPTED

M0      = ACCEPTED
M1      = ACCEPTED
```

Canonical repository:

```text
E:\1project\mdi-b0-5a1
```

Accepted M1:

```text
E:\mdi-v0-review\M1_attempt-01.zip

ZIP SHA256 =
fa719e8ff85db3e86bd1c84d7c5dfa0801f4c59a9abdf9d223ad9597bba22c5d

phase_return SHA256 =
9e9c98b5131687ca894753b9903cbaf0677cc6c59f9e18b9b80df61f4207bd79
```

Start:

```text
PHASE = M2
ATTEMPT = attempt-01
```

Expected bundle:

```text
E:\mdi-v0-review\M2_attempt-01.zip
```

Do NOT start M3.

## 0. M2 PURPOSE

M1 established:

```text
single PostgreSQL durable ownership authority
execution_attempt fencing
server-controlled leases
expiry/reclaim
stale-worker rejection
cancellation precedence
```

M2 now answers a different question:

```text
After a real crash or publication gap,
what is the LATEST VALID DURABLE BOUNDARY,
and how does the system recover from there
WITHOUT repeating already committed scientific effects?
```

M2 is specifically about:

```text
crash recovery
publication seams
duplicate delivery
queue acknowledgement gaps
object-store/database reconciliation
idempotent authoritative publication
fresh-process recovery
orphan detection
```

M2 is NOT:

```text
another lease redesign
new workflow engine
generic retry platform
Kafka/Celery migration
provider retry policy
load/fairness optimization
M3/M4/M5 work
```

## 1. AUTHORITATIVE M2 REQUIREMENTS

Close exactly:

```text
M2-001
M2-002
M2-003
M2-004
M2-005
M2-006
M2-007
M2-008
```

### M2-001

Map durable boundaries:

```text
Turn decision
→ Plan
→ Job
→ ToolCall attempt
→ raw/staged Artifact
→ verified Artifact
→ ScientificResult
→ Interpretation
→ Report
→ next child scheduling
```

For every seam declare the minimum safe retry/reconciliation boundary.

### M2-002

After queue publication failure:

```text
recover the EXISTING Job / child Turn
```

Do not create replacement scientific entities merely because enqueue
acknowledgement was lost.

Reuse existing:

```text
idempotency
reconciliation
outbox-like state
```

or add only the narrowest durable equivalent.

### M2-003

Separate:

```text
object bytes stored
object verified
Artifact authoritative
Result authoritative
```

Reconcile:

```text
object upload success + DB failure

DB success + queue failure
```

Partial objects must never masquerade as completed science.

### M2-004

Deduplicate authoritative effects by stable operation/input/attempt identity.

Do NOT claim:

```text
globally exactly-once physical execution
```

The correct guarantee is:

```text
possibly repeated execution
+
idempotent authoritative publication
```

for interrupted indivisible scientific calls.

### M2-005

If:

```text
ScientificResult is complete
Interpretation fails
```

retry ONLY Interpretation.

Do not recompute completed science.

Preserve:

```text
Result
source ObjectVersion
Report/Context identity
```

during reopen/recovery.

### M2-006

Execute REAL isolated interruption/recovery tests including:

```text
owned worker process termination
API restart
Redis interruption
PostgreSQL transient interruption
MinIO write/read interruption
client disconnect
```

No mock-only claim.

### M2-007

For every executed fault record:

```text
observed failure
exact interruption seam
expected recovery
actual recovery
effect counts
elapsed recovery
```

### M2-008

Detect:

```text
orphan RUNNING Job
stale lease
duplicate publication
recoverable/retryable state
```

Do not delete user science or clear shared queues to make counts look clean.

## 2. REQUIRED DESIGN REFERENCES

Read before changing code:

```text
governance/EXECUTION_CONTRACT.md
governance/CONFLICTS_AND_CLARIFICATIONS.md
review/RETURN_PROTOCOL.md

phases/M2.md

specs/S10_History_Lifecycle.md
specs/S13_No_Authority_Feedback.md

cases/fault_matrix.json
```

Also inspect current exact implementation for:

```text
Turn admission
Plan persistence
Job creation
enqueue
worker entrypoint
ToolCall persistence
Artifact staging/publication
Result projection
Interpretation scheduling
Report scheduling
next autonomous child scheduling
reopen/read paths
```

M1 implementation is now baseline, not something to redesign.

## 3. M1 NONBLOCKING EVIDENCE HYGIENE

Do NOT modify or reseal M1.

Create inside M2:

```text
M1_evidence_errata.json
```

Record that the accepted final detailed F10 evidence is:

```text
job_id =
job_agent2_e113844308d04fa6975cd5c1f0bfd86f
```

and that the old row still present in M1:

```text
fault_campaign_summary.json
```

contained a superseded earlier F10 job/reference.

Canonical M1 truth for continuity comes from:

```text
F10_user_cancellation.json
cancellation_race_results.json
scientific_effect_counts.json
lifecycle_projection_results.json
phase_return.json
```

Do not change the M1 acceptance decision.

Also record the exact canonical source path + SHA256 for:

```text
0035_job_execution_leases
```

so M2's schema baseline is explicitly traceable.

This is evidence hygiene only.

## 4. CREATE A NEW M2 ISOLATED ENVIRONMENT

Do NOT destructively reuse M1 namespace.

Create new qualification-owned:

```text
PostgreSQL DB/schema
Redis namespace/DB
MinIO bucket/prefix
qualification API
qualification workers
qualification Project/data
```

using actually free values.

Never assume a port/Redis DB is free.

Record:

```text
qualification_environment.json
owned_resource_manifest.json
qualification_process_registry.json
```

Shared:

```text
canonical PostgreSQL service
canonical Redis service
canonical MinIO service
```

must NOT be stopped for fault injection.

## 5. DURABLE BOUNDARY MATRIX

Before implementation create:

```text
recovery_boundary_matrix.json
```

Rows must include at least:

```text
Turn decision persisted
Plan persisted
Job persisted
enqueue requested
enqueue acknowledgement
Job claimed
ToolCall created
Tool locally finished
raw object bytes written
object checksum verified
Artifact row committed
Result projected
Interpretation requested
Interpretation committed
Report requested
Report committed
next child Turn/Job persisted
next child enqueue acknowledged
```

For every row record:

```text
durable authority
idempotency key
owner/fence involved
what can be retried
what MUST NOT be recomputed
what can be reconciled
what represents authoritative user-visible science
```

## 6. GAP ANALYSIS BEFORE CODE

Create:

```text
M2_gap_analysis.md
```

For each boundary classify:

```text
ALREADY_SAFE
MISSING_RECONCILIATION
MISSING_IDEMPOTENCY
INCORRECT
NOT_APPLICABLE
```

Do NOT write code merely because M2 has begun.

Only fix demonstrated gaps.

## 7. AUTHORITATIVE EFFECT IDENTITY

Document current stable identities for:

```text
Turn
Plan
Job
ToolCall
Artifact
ScientificResult
Interpretation
Report
child Turn/Job
```

Define which identity makes retry idempotent.

Important distinction:

```text
execution_attempt
```

may change after crash/reclaim.

But a logically identical completed scientific effect must not produce
multiple current authoritative Results merely because attempt changed.

Create:

```text
authoritative_effect_identity.json
```

## 8. OBJECT STORE STAGING MODEL

Map current behavior:

```text
Tool computes
→ bytes created
→ object written
→ checksum/size verified
→ Artifact metadata committed
→ Result sees Artifact
```

If M1 already added attempt-scoped storage such as:

```text
attempts/<execution_attempt>/...
```

reuse it.

Do NOT invent another storage hierarchy unless M2 evidence proves one is
needed.

Create:

```text
artifact_publication_model.md
```

Explicitly distinguish:

```text
TEMPORARY/STAGED
VERIFIED
AUTHORITATIVE
```

## 9. F01 — WORKER DIES BEFORE TOOL STARTS

Execute fault-matrix:

```text
F01
Worker dies before Tool starts
```

Owner phase = M2.

Required sequence:

```text
durable Job admitted

owned worker claims Job

BEFORE registered Tool begins:
terminate only that verified owned worker

lease expires/recovery activates

fresh worker with no warm upload state
recovers SAME Job

Tool executes
Result publishes
```

Require:

```text
same Job ID
same source ObjectVersions
same Plan
no duplicate Tool authoritative effect
one authoritative Result
```

Do not manually create replacement Job.

## 10. F02 — WORKER DIES MID INDIVISIBLE TOOL

Execute:

```text
F02
Worker dies mid indivisible Tool
```

Use an actual current Tool classified by M1 as:

```text
RESTARTABLE_IDEMPOTENT_ATTEMPT
```

Prefer a deterministic scientific operation with an independently checkable
oracle.

Required:

```text
attempt A enters actual Tool execution

owned process is terminated DURING computation

attempt A never publishes completed science

fresh worker reclaims

attempt B starts from declared durable boundary
```

Since current Toolset has:

```text
checkpointable = 0
```

this MUST be a truthful:

```text
RESTART
```

not fake partial resume.

Final authoritative scientific output must pass its oracle.

## 11. DO NOT CALL REEXECUTION "RESUME"

For F02, record:

```text
old local execution = interrupted
new attempt = restarted from durable boundary
```

Do NOT report:

```text
resumed at 63%
```

unless the current Toolset changes and a valid M1 checkpoint contract exists.

## 12. F04 — ARTIFACT EXISTS BEFORE RESULT PUBLICATION

Execute:

```text
F04
Artifact stored before Result publication crash
```

Use a real scientific Tool with meaningful Artifact(s).

Inject a controlled owned-process crash at the exact seam AFTER:

```text
required object bytes exist
checksum/size verification succeeded
Artifact is sufficiently durable according to current contract
```

but BEFORE:

```text
ScientificResult publication completes
```

Then start a fresh process.

Required:

```text
existing verified Artifact reconciled

ScientificResult published at most once

scientific algorithm NOT rerun
if existing verified durable evidence is sufficient

Artifact hash unchanged
```

This is a critical M2 case.

## 13. F04 MUST PROVE NO ALGORITHM RERUN

Record a deterministic execution counter or equivalent owner-layer evidence.

Before crash:

```text
scientific computation count = 1
```

After reconciliation:

```text
scientific computation count must remain 1
```

if durable verified Artifact was already sufficient.

Do not infer this merely from equal output hashes.

## 14. UPLOAD-SUCCESS / DB-FAILURE RECONCILIATION

Separately exercise the storage seam where:

```text
object bytes successfully written
DB authoritative reference fails before commit
```

After recovery:

```text
either exact staged bytes are reconciled and promoted safely
or safely classified/cleaned as orphan staging
```

Never expose them as completed Artifact before authoritative metadata exists.

Record:

```text
artifact_publication_reconciliation.json
```

## 15. F05 — QUEUE ACKNOWLEDGEMENT LOST

Execute:

```text
F05
Queue publication acknowledgement lost
```

Inject failure AFTER the relevant durable scientific entity exists but around
the enqueue/ack seam.

Required:

```text
same Turn/Job/child entity recovered

no replacement scientific entity

duplicate delivery safe

eventual one authoritative downstream effect
```

If current outbox/reconciliation already solves this:

```text
prove it with real failure injection
```

Do not create a second async platform.

## 16. QUEUE DELIVERY SEMANTICS

State explicitly:

```text
delivery may be at-least-once
```

if that is current truth.

Do NOT claim transport exactly-once.

The guarantee should be:

```text
stable durable identity
+
idempotent authoritative publication
```

## 17. DUPLICATE MESSAGE TEST

Deliver the same eligible Job/message more than once through the actual
qualification queue path.

Required:

```text
physical handler invocations may be > 1

authoritative ToolCall/Result publication remains singular as required

no duplicate downstream child work
```

Record:

```text
duplicate_delivery_results.json
```

## 18. RESULT MUST SURVIVE INTERPRETATION FAILURE

Execute an M2-owned controlled Interpretation failure AFTER a completed
ScientificResult exists.

This is NOT F09/provider-429 qualification.

Do not steal M3 ownership.

The failure seam should prove:

```text
Result remains CURRENT and usable

scientific Tool is NOT rerun

Interpretation becomes retryable/recoverable

retry Interpretation only

same Result/source identities retained
```

Create:

```text
result_interpretation_recovery.json
```

## 19. REPORT / CONTEXT / REOPEN IDENTITY

After recovery:

```text
reopen the Research state
```

Verify exact:

```text
source ObjectVersions
Result IDs
Interpretation ID where successfully retried
Report ID
Context refs
```

No fuzzy rebound to a new source version.

No new scientific Result just from reopening.

## 20. F06 — REDIS TEMPORARILY UNAVAILABLE

Execute:

```text
F06
Redis temporary unavailable
```

CRITICAL SAFETY:

```text
DO NOT stop shared Redis.
```

Use a qualification-only interruption mechanism such as:

```text
qualification-only TCP proxy
qualification-only endpoint
scoped network/test seam
```

so only M2 API/workers lose Redis connectivity.

Required:

```text
typed/bounded failure or retry

no scientific payload truth lost

PostgreSQL/object-store committed data preserved

after endpoint recovery:
existing durable work resumes/reconciles
```

No:

```text
FLUSHALL
FLUSHDB on shared DB
```

## 21. F07 — POSTGRESQL TEMPORARILY UNAVAILABLE

Execute:

```text
F07
PostgreSQL temporary unavailable
```

DO NOT stop shared PostgreSQL.

Interrupt only M2 qualification connectivity using:

```text
qualification-only proxy/test endpoint
```

or another actually isolated mechanism.

Required:

```text
no partial scientific commit

no blind authoritative publication while DB authority unavailable

safe retry/recovery after connectivity returns

no idle-in-transaction leak attributable to fault
```

## 22. F08 — MINIO WRITE/READ FAILURE

Execute:

```text
F08
MinIO partial write/read failure
```

Do NOT stop shared MinIO.

Interrupt only qualification-owned object traffic.

Test at least one real write/read seam.

Required:

```text
incomplete bytes not published as complete Artifact

checksum/size/manifest remain coherent

safe retry/reconciliation

no unrelated bucket/object damage
```

## 23. API RESTART RECOVERY SMOKE

M2-006 requires actual API restart recovery.

Restart ONLY the qualification API.

Do NOT call this F11 closure; F11 belongs to M4.

Use an active/persisted qualification workflow.

Verify:

```text
API memory loss does not lose durable state

reopen returns exact persisted Job/Result state

no read-triggered reexecution

workers remain scientifically coherent
```

Create:

```text
api_restart_recovery.json
```

## 24. CLIENT DISCONNECT RECOVERY SMOKE

M2-006 also requires client interruption.

Use a qualification-owned client and current supported endpoint.

Abort a request/download/upload where scientifically appropriate.

Do NOT claim F13 closure; F13 belongs to M4.

Verify:

```text
server durability remains coherent

no leaked authoritative partial object

client may retry safely where contract allows

completed scientific state remains usable
```

## 25. FRESH PROCESS REQUIREMENT

All crash-recovery acceptance cases must recover using:

```text
a genuinely fresh process
```

not the same Python process with an exception caught.

Record:

```text
PID
start time
command
cwd
parent
qualification namespace
```

for killed process and recovering process.

## 26. PROCESS OWNERSHIP REVALIDATION

Immediately before ANY:

```text
terminate
pause
resume
restart
network-cut action
```

revalidate:

```text
PID
start time
command
cwd
PPID
qualification namespace
```

If mismatch:

```text
ABORT FAULT INJECTION
```

Old M0/M1 PIDs are not current ownership proof.

## 27. FAILURE TIMELINE CONTRACT

Every real M2 fault artifact must include:

```text
case ID

expected pre-state

exact fault seam

pre-injection ownership proof

injection timestamp

observed failure

durable state immediately after failure

recovery trigger

fresh recovery process

recovery completion timestamp

elapsed recovery

expected effect counts

actual effect counts

scientific oracle

cleanup/shared-service state
```

No exception-only evidence.

## 28. BEFORE/AFTER EFFECT COUNTS

Create:

```text
before_after_effect_counts.json
```

For every case count where applicable:

```text
Turn
Plan
Job
Tool execution attempts
ToolCall authoritative rows
staged objects
verified Artifacts
ScientificResults
Interpretations
Reports
child Turns
child Jobs
queue deliveries
```

Separate:

```text
attempt count
```

from:

```text
authoritative effect count
```

## 29. EXACTLY-ONCE CLAIMS ARE FORBIDDEN

Do NOT write:

```text
exactly-once execution
```

unless mathematically/product-authoritatively true.

Prefer:

```text
at-least-once execution is possible

authoritative publication is idempotent

duplicate durable scientific effects are prevented
```

## 30. ORPHAN DETECTION

Implement/verify detection for:

```text
RUNNING Job with no valid owner
expired/stale lease
staged object with no authoritative Artifact
duplicate publication candidate
failed enqueue needing reconciliation
retryable Interpretation
```

Create:

```text
recovery_scan_results.json
```

The scanner/reconciliation path must not delete legitimate user science.

## 31. ACTIONABLE RECOVERY STATE

Where current API/read model exposes lifecycle state, add only the narrowest
read-only recovery projection needed for M2, such as:

```text
RECOVERING
RETRYABLE
STALE_LEASE
AWAITING_RECONCILIATION
FAILED_RECOVERABLE
```

Only if supported by durable facts.

Do not make frontend/UI the recovery owner.

## 32. BROWSER RECOVERY EVIDENCE

M2 authoritative required artifacts call for current browser evidence.

Capture real current browser screenshots for applicable states such as:

```text
recovering
partial/retryable
failure
reopened completed output
```

Screenshots must correspond to actual durable state.

Do not fake states with frontend-only edits.

The known browser 125/150/200% zoom limitation is irrelevant here and remains
nonblocking.

## 33. F01 ACCEPTANCE

Require:

```text
same Job recovered
fresh worker
Tool executes once authoritatively
one final Result
```

## 34. F02 ACCEPTANCE

Require:

```text
worker actually terminated mid Tool

old attempt incomplete

new attempt explicitly RESTARTS

no false checkpoint/resume claim

one authoritative final science result
```

## 35. F04 ACCEPTANCE

Require:

```text
verified Artifact already exists

process dies before Result publication

fresh recovery sees same verified Artifact

science algorithm is not rerun

Result publishes once
```

## 36. F05 ACCEPTANCE

Require:

```text
queue ack uncertainty actually injected

same durable entity recovered

duplicate delivery harmless

no replacement Job/child Turn

one authoritative downstream effect
```

## 37. F06 ACCEPTANCE

Require:

```text
real qualification Redis connectivity interruption

shared Redis untouched

durable DB/storage truth preserved

recovery completes after connectivity restore
```

## 38. F07 ACCEPTANCE

Require:

```text
real qualification PostgreSQL connectivity interruption

shared PostgreSQL process untouched

no partial scientific commit

recovery succeeds
```

## 39. F08 ACCEPTANCE

Require:

```text
real qualification object-store interruption

no incomplete object published as complete

hash/size/manifest coherent after recovery
```

## 40. INTERPRETATION RECOVERY ACCEPTANCE

Require:

```text
completed Result exists before failure

Interpretation failure does NOT change Result

Tool execution count unchanged during retry

Interpretation eventually succeeds or returns truthful bounded recoverable
state

same Result ID retained
```

## 41. NO RECOMPUTE ON READ

After any recovery/reopen:

```text
GET/read/browser reopen
```

must not silently trigger science recomputation.

Measure ToolCall/Result counts before and after reopen.

## 42. SCIENTIFIC ORACLES

Use deterministic accepted scientific operations for recovery cases wherever
possible.

After crash/recovery validate final scientific result independently.

Infrastructure recovery PASS with scientifically corrupted output is FAIL.

## 43. DO NOT OVERWRITE COMMITTED SCIENCE

If attempt A already authoritatively committed a Result:

```text
later attempt B cannot replace it merely because B is newer
```

unless the product contract explicitly represents B as a new Result/version.

Test this invariant.

## 44. HISTORY / SOURCE LIFECYCLE

Respect S10:

```text
ARCHIVED
TRASHED
INVALIDATED
MISSING
temporarily unavailable
new source version
```

Recovery must preserve exact historical refs.

Do not fuzzy-bind a missing old source to a newer version.

Do not rewrite old Result provenance during recovery.

## 45. NO AUTHORITY FEEDBACK

Respect S13.

Recovery/reopen must not turn:

```text
Interpretation
Report
Memory
```

into new scientific support simply because they were recovered or repeated.

Scientific support must still dereference to:

```text
Result
authorized deterministic facts
LiteratureEvidence
```

## 46. M2-OWNED FAULT CASES

M2 owns and should execute real evidence for:

```text
F01
F02
F04
F05
F06
F07
F08
```

Do NOT claim ownership closure for:

```text
F09 = M3
F11 = M4
F12 = M3
F13 = M4
F14 = M4
F15 = M6
```

M2 may perform API/client recovery smoke required by M2-006, but must not
mark M4 cases completed.

## 47. PRESERVE M1 FENCING

Every M2 recovery path must still obey M1:

```text
current execution_attempt
current owner
valid lease/fence
```

A recovery mechanism is invalid if it bypasses M1 fencing.

Do NOT introduce a reconciler that can authoritatively publish without
current durable authority.

## 48. RETRY BOUNDS

All automatic retries/reconciliation loops must be bounded.

No:

```text
while true
```

retry loops.

Reuse current product limits where possible.

Any new bound needs explicit rationale.

## 49. NO PAYLOAD TRUTH IN REDIS

Redis may contain:

```text
delivery/queue coordination
```

It must not become sole authority for:

```text
scientific payload
Result
source identity
recovery state
```

Recovery after Redis loss must come from durable authority.

## 50. M2 MIGRATION RULE

Do not create a migration merely to store more debugging information.

If M2 correctness requires durable outbox/reconciliation fields:

```text
justify them
test in isolated DB
test historical reads
document rollback/restore
```

Otherwise:

```text
NO_NEW_MIGRATION
```

is preferable.

## 51. OWNER-LAYER CHANGE DISCIPLINE

Expected legitimate M2 owner layers include:

```text
Job/Turn durable reconciliation

queue publication/reconciliation seam

Tool/Artifact publication seam

Result projection idempotency

Interpretation retry scheduling

recovery scanner/read projection
```

Do not touch unrelated:

```text
scientific formulas
viewer rendering
UI styling
public scientific limits
Agent architecture
```

## 52. PUBLIC LIMITS

M2 does not authorize public-limit uplift.

Require:

```text
Public limits changed = NO
```

unless a completely separate measured, science-validated requirement exists.

## 53. REQUIRED ARTIFACTS

At minimum produce:

```text
phase_return.json
change_summary.md

M1_evidence_errata.json

M2_gap_analysis.md

recovery_boundary_matrix.json
authoritative_effect_identity.json
artifact_publication_model.md

fault_results.json
before_after_effect_counts.json
artifact_publication_reconciliation.json
duplicate_delivery_results.json

result_interpretation_recovery.json
recovery_scan_results.json

F01_worker_dies_before_tool.json
F02_worker_dies_mid_tool.json
F04_artifact_before_result_crash.json
F05_queue_ack_lost.json
F06_redis_unavailable.json
F07_postgres_unavailable.json
F08_minio_failure.json

api_restart_recovery.json
client_disconnect_recovery.json

qualification_environment.json
owned_resource_manifest.json
qualification_process_registry.json

browser/
  recovering*.png
  retryable*.png
  failure*.png
  reopen*.png

test_logs/
fault_logs/

service_state.txt
```

If code changed:

```text
changes.patch
focused test logs
```

If a migration is added:

```text
migration source
migration SHA256
migration test result
```

## 54. CONSISTENCY CHECKER

Add an M2 semantic evidence checker.

It must reject at minimum:

```text
F04 PASS
but scientific algorithm executed twice

F05 PASS
but replacement Job/child Turn was created

F06/F07/F08 PASS
without real isolated connectivity/storage interruption

M2-005 CLOSED
but Tool reran during interpretation retry

reopen PASS
but read created new ToolCall/Result

orphan scan COMPLETE
while unresolved orphan RUNNING qualification job exists

authoritative publication PASS
with duplicate current Result

M2 READY
while any owned fault case remains NOT_RUN/FAILED
```

## 55. TESTS

Run focused unit/integration tests for modified owner layers.

But real-process fault execution is mandatory for acceptance.

Unit tests alone do NOT close:

```text
M2-006
M2-007
```

## 56. M2 FINAL ACCEPTANCE GATE

Before:

```text
AGENT_STATUS = READY_FOR_REVIEW
```

require:

```text
M2-001 CLOSED
M2-002 CLOSED
M2-003 CLOSED
M2-004 CLOSED
M2-005 CLOSED
M2-006 CLOSED
M2-007 CLOSED
M2-008 CLOSED
```

and:

```text
F01 = PASS
F02 = PASS
F04 = PASS
F05 = PASS
F06 = PASS
F07 = PASS
F08 = PASS

duplicate authoritative Result = 0

read-triggered recomputation = 0

completed Result recomputed during interpretation retry = 0

unresolved owned orphan RUNNING jobs = 0

stale attempt publication = 0

shared resource damage = 0
```

## 57. OFFICIAL VALIDATION

Generate:

```powershell
python tools\phase_brief.py M2 `
  --template <M2-attempt-01>\phase_return.json
```

Populate real evidence only.

Then:

```powershell
python tools\validate_return.py `
  <M2-attempt-01>\phase_return.json `
  --seal
```

Require:

```text
FORMAT_AND_EVIDENCE_INTEGRITY_PASS
errors = []
```

Build:

```powershell
python tools\build_review_bundle.py `
  <M2-attempt-01>\phase_return.json `
  --output E:\mdi-v0-review\M2_attempt-01.zip
```

Verify ZIP CRC.

Compute:

```text
ZIP SHA256
phase_return SHA256
```

## 58. STOP GATE

Implementation agent may return:

```text
READY_FOR_REVIEW
PARTIAL
BLOCKED
```

It may NOT self-assign:

```text
ACCEPTED
```

Do NOT start:

```text
M3
M4
M5
M6
FINAL0
```

until external review accepts M2.

## 59. PROTECTED STATE

Preserve:

```text
all accepted Pre-M evidence immutable
M0 immutable
M1 immutable
J frozen unchanged

current uncommitted work preserved

no reset
no clean
no destructive checkout

no commit
no push
no tag
no release
no remote CI

no shared Redis interruption
no shared PostgreSQL stop
no shared MinIO stop
no unknown PID signal

no user-data fault injection
no queue purge to clean counts
no scientific-object deletion to make recovery pass

no fake process death
no mock-only failure presented as real
no fake exactly-once execution claim
no fake checkpoint/resume
```

## 60. FINAL RETURN

Return exactly:

```text
PHASE: M2
ATTEMPT: attempt-01

AGENT_STATUS:
READY_FOR_REVIEW | PARTIAL | BLOCKED

M2-001 =
M2-002 =
M2-003 =
M2-004 =
M2-005 =
M2-006 =
M2-007 =
M2-008 =

Durable boundary map =
<summary>

M1 evidence erratum =
RECORDED_IN_CURRENT_PROVENANCE

F01 =
PASS | FAIL | NOT_RUN

F02 =
PASS | FAIL | NOT_RUN

F04 =
PASS | FAIL | NOT_RUN

F05 =
PASS | FAIL | NOT_RUN

F06 =
PASS | FAIL | NOT_RUN

F07 =
PASS | FAIL | NOT_RUN

F08 =
PASS | FAIL | NOT_RUN

F04 algorithm rerun count after durable artifact =
<count>

F05 replacement Job/Turn count =
<count>

Duplicate delivery authoritative Result count =
<count>

Interpretation retry Tool recomputation count =
<count>

API restart recovery =
PASS | FAIL | NOT_RUN

Client disconnect recovery =
PASS | FAIL | NOT_RUN

Read/reopen triggered Tool recomputation =
<count>

Unresolved owned orphan RUNNING jobs =
<count>

Stale publications =
<count>

Recovery deadlines =
<summary against frozen M0 criteria>

Production behavior changed =
YES | NO
<exact owner-layer changes>

Migration =
NO_NEW_MIGRATION |
MIGRATION_REQUIRED_AND_TESTED

Public limits changed =
NO | <exact justified change>

Shared resources damaged =
NO | YES

Tests/fault campaign =
<commands/counts/results>

Open issues =
<exact M2 IDs>

NEXT PHASE PROPOSED =
M3 | NONE

M3 started =
NO

ZIP =
E:\mdi-v0-review\M2_attempt-01.zip

ZIP SHA256 =
...

phase_return SHA256 =
...

services =
...
```

Execute M2 attempt-01 now and STOP for external review.
