# Scientific Result Bundle 1.0

The bundle contains typed result items, facts, figures, tables, evidence,
methods, limitations, warnings, and provenance. Cross references are checked
at validation time. A quantitative fact must point to a committed artifact
locator, tool call, or exact scientific object reference. The projection layer
does not infer numbers from filenames, prose, or images.

Partial execution is represented as `execution_status = PARTIAL` while
preserving successful outputs and recording failed or unavailable outputs as
warnings/limitations. Execution status and relevance status are independent.
