# Product Maturity — Same-stack runtime reload and browser recheck

日期：2026-09-01

本批次发现并修复了两个运行时问题，而不是科学数据服务停止：

- API 重载时曾误用 MinIO 凭据；恢复仓库运行手册中的 `mdi-local` /
  `mdi-local-dev` 后，真实 MinIO 读写和 `/health/runtime` 恢复正常。
- 3013 端口上的旧 Next 进程使用默认 `.next`，在 `/trash` 与 `/account`
  加载旧 chunk 时产生 `ChunkLoadError`。仅替换 3013 前端进程为当前完整
  构建 `.next-prod-maturity-20260902`，没有停止 API、PostgreSQL、Redis、
  MinIO、workers 或关闭浏览器标签页。

## Runtime

```text
API = http://127.0.0.1:8005
frontend = http://127.0.0.1:3013
compatibility alias = http://127.0.0.1:3000
database = PostgreSQL 127.0.0.1:55434 / mdi
queue = Redis 127.0.0.1:6379/13
artifact storage = MinIO 127.0.0.1:9000 / mdi-artifacts
worker = Redis-backed
```

当前 `/health/runtime`：

```text
database = ok / postgresql
redis = ok / redis
artifactStorage = ok / minio
worker = ok / redis
llmProvider = ok / deepseek
```

## Browser

新认证标签页等待异步加载后复核：

```text
/trash = 正常回收站空状态，无应用错误
/account = 正常账户中心，无应用错误
项目数据对象详情 = 正常导航和数据列表
科学报告详情 = 正常报告阅读器
fresh tab console errors = 0
Internal Server Error = 0
Application error = 0
```

Acceptance Dataset 仍显示真实可交互内容：

```text
Dataset = dataset_0001_a0b09e3324e44ca4
row = Si / 1
objectId = obj_dataframe_60c91184df02
sampleRef = dataset_0001_a0b09e3324e44ca4@2:60c91184df022d34:0
```

旧标签页未关闭；新标签页已停留在 Acceptance Dataset 页面并标记为可继续核验。

补充：`scripts/phase14r_frontend_start.mjs` 现以 `apps/web` 为工作目录，
使用原生 `next start` 启动指定生产构建；新增
`apps/web/test/phase14r-runtime-static-assets.mjs`，当前通过静态资源完整性
检查，避免再次从仓库根目录误读过期 `.next`。
