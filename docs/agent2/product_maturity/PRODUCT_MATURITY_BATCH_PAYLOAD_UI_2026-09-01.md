# Product Maturity — Payload availability UI clarification

日期：2026-09-01

## 结论

本批次再次确认用户报告的“Internal Server Error / 解析资源无法读取”不是
PostgreSQL、Redis、MinIO 或 worker 停止造成的：

- `GET http://127.0.0.1:8005/health/runtime` 返回 `200`；
- database=`postgresql`、redis=`redis`、artifactStorage=`minio`、
  worker=`redis`、LLM provider=`deepseek` 均为 `ok`；
- 3000 兼容入口、3013 前端、8005 API、55434 PostgreSQL、6379 Redis、
  9000 MinIO 均保持监听；
- 认证 acceptance 用户可见的 28 个 Dataset object-store 路由全部返回
  `200`，没有新的 5xx。

## 产品层修复

`ScientificDataView` 现在将来源读取失败分为两个明确状态：

1. `暂时失败，可重试`
   - 适用于网络、服务暂时不可用等非确定性错误；
   - 保留“重新检查存储”动作；
   - 不把暂时故障描述成数据已丢失。
2. `已确认缺失`
   - 对 404 或 `SOURCE_MISSING`/`PAYLOAD_MISSING` 等服务端契约使用；
   - 显示“原始解析 payload 当前不可用”；
   - 明确精确来源、元数据和版本身份仍保留；
   - 明确不会以其他 Dataset、ScientificObjectVersion 或 Artifact 替代；
   - 将重试动作改为“再次确认来源”，并提示重新导入/恢复原始文件。

两种状态均保留“查看来源与属性”和技术详情，避免用户被空白画布或
`Internal Server Error` 误导。不会伪造不可恢复的科学 bytes，也不会修改
ScientificObject、ScientificObjectVersion、ScientificResult、Artifact 或
Report 权威。

## 验证

- `apps/web/app/components/ProductPages.test.tsx`：40 passed；
- TypeScript typecheck：PASS；
- touched Ruff：PASS；
- 28/28 acceptance Dataset object-store API：HTTP 200；
- 服务与浏览器标签页保持运行。

## 剩余数据边界

保留的极少量历史 synthetic/test 引用仍然按 fail-closed 语义显示，不做
跨版本替换或虚构 payload。这些引用不属于 acceptance 用户可见的正常科学
对象范围。真正用户可见的 Dataset、ScientificObjectVersion Viewer、
Report 和 trajectory payload 已完成精确可达核验。
