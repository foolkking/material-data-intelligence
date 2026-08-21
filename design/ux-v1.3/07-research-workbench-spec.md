# Research Workbench Specification

## Layout

```text
+ Conversation (36%, resizable 30-45%) + Dynamic Workbench (64%) +
| question and continuity              | header: current research            |
|                                      | Activity (224px) | result surface |
|                                      | real steps       | plan/run/result|
| composer                             |                  | inspector opt. |
+--------------------------------------+-------------------------------------+
```

On desktop, both the question and current work are visible. On mobile, conversation is first and workbench follows; mobile does not falsely preserve the desktop simultaneous split.

## Human-readable plan

The user sees **分析方案** before running and **分析方法** after result. It contains:

- selected data meaning and scope;
- scientific steps;
- expected figures/outputs;
- applicable limitations.

It hides Plan ID, input references, registry version, schema version, hashes and raw tool contracts. The backend validated/persisted AnalysisPlan remains mandatory.

## Raw process to research-process mapping

| User research stage | Minimum backend fact | Current reality | UI rule |
| --- | --- | --- | --- |
| 理解问题 | accepted/clarified AnalysisIntent | EXISTS_IN_CODE | show only outcome/question wording |
| 确定数据 | resolved Dataset/Profile/resource selection | PARTIAL | show only proven scope; cross-Dataset target needs backend work |
| 制定分析 | persisted validated AnalysisPlan | EXISTS_IN_CODE | render human plan, not raw contract |
| 执行计算 | Job/ToolCall running state | EXISTS_IN_CODE | named current operation, no percentage |
| 生成结果 | persisted Artifact | EXISTS_IN_CODE | show artifact incrementally when available |
| 解释结果 | terminal interpretation lifecycle | EXISTS_IN_CODE | show only after it exists; do not fake a streaming phase |

## Current scope boundary

`Project default all data -> agent selects related resources` is a valid target interaction but **REQUIRES_NEW_BACKEND_CAPABILITY** across Datasets. Today a single valid Dataset/DataProfile remains the execution root. The prototype represents target Project vocabulary and marks the backend implication in the reality matrix.

## State requirements

The prototype includes IDLE, PLANNING, RUNNING_NO_RESULT, RUNNING_WITH_INCREMENTAL_RESULT, PARTIAL_SUCCESS, COMPLETE, UNSUPPORTED, NEEDS_CLARIFICATION, and FAILED. See `09-state-matrix.md` for source truth and copy.

## Completion hierarchy

`RUNNING` retains the Activity rail beside live scientific output: the focal point is both the actual active operation and the artifact emerging from a completed tool. `COMPLETE` collapses this rail into `分析完成 · 4 个步骤 / 查看分析过程`; the Figure receives the recovered width and becomes the focal point. `PARTIAL_SUCCESS` and `FAILED` retain the fuller process context because the user must distinguish preserved output from incomplete or failed work.
