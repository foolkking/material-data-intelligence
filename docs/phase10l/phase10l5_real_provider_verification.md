# Phase 10L-5 Real Provider Verification

Run the live gate only from a controlled local process:

```powershell
$env:DEEPSEEK_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_KEY', 'User')
uv run python scripts/verify_deepseek_phase10l5.py
```

The runner never prints or persists the key. It executes each of the five
frozen cases with a fresh `DeepSeekProvider`; each case has an independent
maximum of twelve calls. A case failure is retained as sanitized diagnostic
evidence and does not stop the remaining cases. `--case-index N` reruns one
case, and `--finalize-only` builds the suite from the five already-passed case
records without making a new network call.

The verified current-product suite in the current evidence directory is:

```text
provider: deepseek
model: deepseek-v4-flash
case count: 5
per-case calls: 3, 3, 3, 4, 3
total real calls: 16
other real providers: 0
verdict: PASS
```

## Historical browser/Mock replay closure

The five current-product cases are not treated as coverage of every earlier
browser flow. `scripts/verify_deepseek_historical_browser_flows.py` replays the
additional historical planner cases through the current canonical
Intent -> Eligibility -> Plan -> Runtime path with real DeepSeek. The retained
suite is:

```text
historical suite: historical_deepseek_suite_dde5218a3d2121fc038bb90d6daa044a
additional historical cases: 40
total cases including the five current cases: 45
passed: 45
failed: 0
real DeepSeek calls in supplemental replay: 92
models: deepseek-v4-flash, deepseek-v4-pro
other real providers: 0
verdict: PASS
```

The supplemental matrix covers the useful planner/browser semantics retained
from Phase 9, 10A, 10B, 10C, 10E, 10F, 10G, 10H, 10I, 10J, 10K, 10L-1, and
10L-2. It includes current canonical replacements for historical tools that
were renamed or superseded, exact target-binding cases, and typed non-ready
cases. A historical prompt is not claimed as verbatim when the original file
was damaged or absent; those records are marked as semantic reconstruction or
superseded coverage in the evidence.

The following are intentionally not real-provider replay cases: pure browser
interaction/renderer checks, deterministic security and failure injection,
provider-parser negative fixtures, and historical tools with no current
registered executable capability. They remain covered by deterministic tests
or are recorded as excluded with a reason; they are not counted as live LLM
coverage. Phase 1-8 infrastructure flows and Phase 10D static-preview-only
flows have no distinct current planner semantic to replay and are covered by
their existing regression evidence or current replacement cases.

The first failed attempts remain under `deepseek_live_failures/` as sanitized
regression provenance. They document real contract failures that were fixed;
they are not relabeled as successful output.
