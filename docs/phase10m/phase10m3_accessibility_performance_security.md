# Phase 10M-3 Accessibility, Performance, and Security

The selection status uses a polite status region. The Inspector is keyboard
operable, receives focus when opened, restores focus when closed, and uses a
mobile bottom sheet. Exact fields and compatibility are textual, not
color-only. Controls meet the 44-pixel mobile target and 390x844 has no
horizontal overflow.

Development acceptance covers 16 secondary refs with rejection of the 17th,
32 subscribers with rejection of the 33rd, 100 rapid updates, semantic replay
suppression, unsubscription cleanup, three desktop engines, and mobile. These
are development/browser acceptance measurements, not a production capacity
claim.

The runtime performs no network request, Artifact payload fetch, dynamic
module load, HTML/JavaScript/iframe execution, scientific computation, LLM
call, or persistence except explicit Pin. No new dependency or migration is
introduced.

All future real LLM calls use DeepSeek only. The sole key source is
`DEEPSEEK_KEY`. Selection runtime itself has no LLM authority and Phase 10M-3
adds zero call sites and performs zero real calls.
