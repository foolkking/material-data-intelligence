# State Matrix

## Research states

| State | User-facing headline | Required underlying fact | Result surface | Primary action | Reality |
| --- | --- | --- | --- | --- | --- |
| IDLE | 从一个科学问题开始 | Project/data available | Project/data orientation | ask a question / inspect data | SMALL_ADAPTATION |
| PLANNING | 分析方案 | validated/persisted plan before enqueue | scientific steps + limitations | confirm/revise | EXISTS_IN_CODE |
| RUNNING_NO_RESULT | 正在执行科学分析 | Job/tool currently active, no persisted artifact | named current step only | inspect data / wait | EXISTS_IN_CODE |
| RUNNING_WITH_INCREMENTAL_RESULT | 相关性分析已可读取 | one artifact persisted while later work is active | available Figure + active next step | inspect artifact | EXISTS_IN_CODE |
| PARTIAL_SUCCESS | 部分分析未完成 | completed artifact + failed/incomplete later operation | preserved partial result + limitation | retry scoped work / read result | SMALL_ADAPTATION |
| COMPLETE | 科学结果 | terminal result and available interpretation | Figure-led document with collapsed process summary | inspect evidence / open report | EXISTS_IN_CODE |
| UNSUPPORTED | 无法进行…分析 | eligibility/data-requirement failure | missing requirement + available properties | choose supported question | EXISTS_IN_CODE |
| NEEDS_CLARIFICATION | 先确定数据范围 | clarification needed before execution | minimal scope question | choose scope | PARTIAL |
| FAILED | 统计摘要没有完成 | failed work plus preserved completed outputs | retained artifacts + scoped recovery | retry failed step | SMALL_ADAPTATION |

## Language transformation

| Raw system fact | Default user expression | Never primary copy |
| --- | --- | --- |
| AnalysisIntent | 已理解问题 / 需要澄清 | Intent ID, provider payload |
| Eligibility missing field | 当前数据没有…列 | capability code / validation dump |
| AnalysisPlan | 分析方案 | Plan ID, registry version |
| Job queued/running | 正在进行…科学操作 | queue/worker/provider status |
| ToolCall completed | 已完成… | raw Tool ID/call log |
| Artifact available | Figure/表格已可读取 | artifact storage identity |
| interpretation terminal | 解释结果 / limitation | synthetic streaming explanation |

## Loading, empty, and recovery

- Loading reserves stable geometry and labels the object being resolved; it does not show an indefinite generic spinner as the only state.
- Empty Project tells the user what data/research has not been created and gives a direct next action.
- Unsupported names the scientific absence and lists meaningful alternatives.
- Partial/failed retains confirmed artifacts and inputs. It does not erase work or imply that an unavailable result exists.
