# API Transcript

## Service Mode
- Planner provider: mock
- Queue runtime: local in-memory repository bundle with QueueWorkerRuntime
- LLM mode: no real LLM
- Network: local process only

## Cases
| Case | Input Type | Selected Tool | Job Status | Artifacts | Result |
|---|---|---|---|---:|---|
| simple_cubic_cif | small CIF | structure.coordination_hist | completed | 4 | PASS |
| nacl_poscar | small POSCAR | structure.coordination_hist | completed | 4 | PASS |
| generated_structure_json | pymatgen Structure JSON | structure.coordination_hist | completed | 4 | PASS |

## Captures
Redacted JSON captures are stored under `api_redacted/<case_id>/`.
