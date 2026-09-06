# 全站产品现实审计（2026-09-03）

## 范围与证据

本轮使用当前工作树、真实运行中的 API/前端与已登录 Chromium 会话，
检查了桌面 `1280×720` 和移动 `390×844` 的 Console、Projects、Project
Overview、Data、Research、Reports、Report detail、Tasks、Notifications、
Trash、Account、Admin、Model Settings 路由。浏览器运行时保持：

```text
PostgreSQL = ready
Redis       = ready
MinIO       = ready
API         = 127.0.0.1:8005
Frontend    = 127.0.0.1:3000
Workers     = 6
```

本轮机器证据：

- 桌面/移动路由均返回 HTTP 200；
- 受保护路由真实会话无 5xx、fatal console error 或 unhandled rejection；
- 所有已测页面 `body.scrollWidth === body.clientWidth`；
- Data 表格在移动端的真实表宽约 `759px`、可视容器约 `375px`，保持了完整列
  数据，但必须通过区域滚动查看；
- Research 移动端工作台计算高度 `744px`，视口高度 `844px`，提交按钮底部
  可落到视口下方；页面根容器同时使用 `overflow: hidden`，存在触达风险；
- Reports detail 移动端高度约 `4225px`，章节导航仍是横向内容，未向用户明确
  展示“还可横向滚动”的提示；
- Tasks/Notifications 移动端分别约 `6636px/6507px`，大量历史记录以单一长
  列呈现，缺少分页/折叠；
- `/admin` 对 researcher 返回“无平台管理权限”，属于正确的 fail-closed
  授权结果，不是服务故障；
- 13/13 个验收 ScientificObjectVersion payload 与 241/241 个验收 Artifact
  payload 已通过精确 size/SHA 可用性核验。无法恢复的历史占位数据继续保持
  fail-closed，不以其他版本替代。

## 十项以上具体观察

| 编号 | 观察 | 证据 | 优先级 | 归类 |
|---|---|---|---|---|
| UI-01 | Research 移动端提交按钮可能被工作台底部裁切 | `textarea` bottom 815，`开始分析` bottom 867，视口 844；根容器 `overflow:hidden` | P1 | Scroll Ownership |
| UI-02 | Data 移动端完整表格超出可视宽度 | 表格 `759px`、区域 `375px`，当前只露出前几列 | P1 | Tables / Mobile |
| UI-03 | Data 表的横向可见性依赖用户发现滚动 | 虽有提示文案，但无渐变/滚动位置反馈 | P2 | Tables / Feedback |
| UI-04 | Reports detail 移动端章节链接超出屏幕 | 章节链接最大 x 487，视口 390 | P1 | Navigation / Mobile |
| UI-05 | Reports detail 首屏操作分成两行但缺少主次解释 | “返回报告/打开来源研究/导出…”在首屏并列 | P2 | Page Header |
| UI-06 | Reports 列表与 Tasks/Notifications 是超长单列 | 报告约 3–5k px，Tasks/Notifications >6.5k px | P1 | Lists / Organization |
| UI-07 | Tasks/Notifications 首屏依赖异步加载，状态信息延迟出现 | 现有同栈审计记录约 6s 才显示有用计数；需继续保留 skeleton/缓存 | P1 | Loading / Recovery |
| UI-08 | Project Data 同时展示 Dataset 与 Scientific Object，关系解释不足 | 桌面 Data 左侧与主区同时出现两类来源/对象 | P1 | IA / Labels |
| UI-09 | Dataset detail 保留诊断/执行术语，和 Research 工作台心智模型并存 | `Profile/Plan/queue` 等技术词与产品研究入口同页 | P1 | IA / Legacy |
| UI-10 | Global Search 默认空状态若无条件展示大量结果，会把检索变成库存浏览 | 既有审计记录曾观察到 140+ 条结果与 `ScientificResult <id>` | P1 | Search / Organization |
| UI-11 | Trash 是生命周期关键入口，但主要位于账户菜单 | `/trash` 可用，常规导航不直接展示 | P1 | Navigation / Lifecycle |
| UI-12 | Account 页面移动端内容很长，安全操作与会话列表距离较远 | 页面约 3250px，需依赖长滚动 | P2 | Account / Scroll |
| UI-13 | Admin 对普通 researcher 正确拒绝，但缺少“申请平台权限”的下一步 | `/admin` 只有无权限说明与返回账户中心 | P2 | Admin / Recovery |
| UI-14 | 结果/报告的技术身份信息仍有进入主阅读流的风险 | Report 中显示版本 UUID、Artifact 引用行 | P2 | Typography / Provenance |
| UI-15 | 图表预览是确定性有限点投影，不等于完整交互式图形 | `ScientificReportArtifactPreview` 只显示最多 96 点 SVG | P1 | Figure / Viewer |
| UI-16 | Source missing 页面必须明确区分“缺 bytes”与“服务故障” | 当前已恢复多数 payload，但无法恢复项仍需保持专业 fail-closed | P0 | Error / Trust |

## 已确认关闭的历史问题

- 移动端项目身份已通过 `.product-project-mobile-identity` 显示；
- 全站当前验收路径无 global horizontal overflow；
- ScientificObject/Artifact 真实 payload 可用性已完成精确恢复与核验；
- Artifact 缺失不会被其他版本或最新版本静默替代；
- `/admin` 的未授权状态为正确的服务器授权结果；
- 报告、Viewer、表格链接均使用单一 `/api` 前缀的当前客户端实现。

## 共享根因与本轮修复顺序

1. **Scroll Ownership（P1）**：移动 Research 工作台不能让主提交动作落在不可
   滚动的裁切区；移动端允许页面自然滚动，同时保留桌面双栏内部滚动。
2. **Table discoverability（P1/P2）**：移动科学表格保留语义横向滚动，并增强
   滚动区域可见性/键盘焦点，不把列数据删掉或改成不稳定的卡片索引。
3. **Long-list organization（P1）**：报告、任务、通知的分页/折叠属于后续
   共享列表根因；当前先记录为未关闭，不用截图冒充已解决。
4. **Legacy/technical disclosure（P1/P2）**：Dataset detail 与 Report 技术
   信息需要共享的“技术详情”折叠/上下文说明，不能改变科学 authority。

## 结论

当前服务不是停止状态；“Internal Server Error/无法打开”的主要历史根因已从
运行时切换为 payload 可用性与 UI 可达性。当前 P1 修复先处理移动 Research
滚动裁切，并在修复后重新截图、重新测量 DOM 与浏览器错误。未在本文件中把
未验证项写成 PASS。

## 修复后复核（2026-09-03）

- UI-01 已关闭：在当前 3000 前端构建上，移动 Research 的
  `.conversation-history` 有界为 `268px`，`开始分析` 的真实矩形为
  `top=777.8 / bottom=821.8`，完整落在 `390×844` 视口内；
- 页面保持 `body.scrollWidth=390 / clientWidth=390`，无横向溢出；
- 复核期间 `console errors=0`、HTTP 5xx=0；
- 其余 UI-02–UI-16 仍按上表记录为待后续共享根因批次，不能因单点修复
  自动标记为完成。

## 数据源与路由复核（2026-09-03）

- 同栈服务保持运行：API `127.0.0.1:8005`、PostgreSQL `127.0.0.1:55434`、Redis DB 13、MinIO `127.0.0.1:9000`、6 个 worker。
- Dataset `dataset_0002_cb403e1b78f54d32` 在 PostgreSQL 中保留了 `si.cif` 的权威引用（441 字节，SHA-256 `4aeaf0107a36ef4bf587da1e52d20ca2739063dd5a548dcb3dac29efc0331198`）及规范化导出元数据。
- 活动 MinIO 缺少的原始源文件和规范化 `metadata.json` 已从保留 MinIO `127.0.0.1:9102` 按原 key 恢复并完成大小/SHA 校验；`structure.json` 原已存在且保持不变（832 字节，SHA-256 `067bc07a01eb9d27021cfcb9406a6358b7b0c81910ca4beb2531dfbfc35217a6`）。
- `DurableObjectStoreResolver` 现在能从活动 MinIO 成功解析该 Dataset（1 个结构）；认证浏览器在 `1280×720` 和 `390×844` 打开真实结构查看器均无 `SOURCE_MISSING`、Internal Server Error、console/page/network 错误，横向溢出为 0。
- 科学 Viewer API 客户端仅对“完整后端 URL 且已包含 `/api`”做去重；浏览器代理仍保留仓库要求的 `/api/api/...` 到 FastAPI `/api/...` 路由映射，避免错误地改成 404。
- 当前项目活动列表中的 13 个 ScientificObject 均通过认证 API 返回 `200`，其当前版本 Viewer 均为 `READY`、`PROFESSIONAL`、`source_resource_refs=1`；未发现新的 SOURCE_MISSING 或跨版本替代。
- 进一步遍历当前账号可见的 16 个项目及其活动 ScientificObject：所有拥有当前版本的对象均返回 Viewer `200/READY`，问题对象数为 `0`；没有因项目切换产生新的授权或资源错误。
- PostgreSQL 一致性快照显示 `scientific_object_versions` 共 262 条且全部为 `AVAILABLE`，`scientific_objects` 共 225 条且当前均为 `ACTIVE`；本轮未发现因版本状态导致的 Viewer 不可用。

## 本轮最终缺口边界

- 本轮确认的服务/资源/路由故障已关闭：Dataset 原始源可读取、规范化解析资源可读取、活动对象 Viewer 全部可用、认证桌面/移动路径无运行时错误。
- 全站此前记录的长列表组织、报告章节移动端提示、Data/Dataset 心智模型、技术详情折叠等 P1/P2 产品改进仍未在本批次展开；这些是后续产品成熟度工作，不应伪装成已经完成。
- 因此本轮不创建提交或发布封板结论；保留当前服务和浏览器会话，等待下一批次集中处理剩余 UI/IA 缺口。

## 共享 UI 改进复核（2026-09-03）

- UI-04（报告章节移动端可发现性）已部分关闭：章节导航保留单一横向滚动
  owner，并增加“左右滑动查看章节”提示；移动页无横向溢出。
- UI-11（回收站入口过深）已部分关闭：全局顶栏新增直接入口，账户菜单入口
  继续保留；移动端使用紧凑可访问控件避免顶栏拥挤。
- 其他长列表分页/折叠、Dataset detail 技术术语分层等问题仍按未关闭处理，
  本轮没有将其误报为完成。

## 共享列表与报告操作层批次（2026-09-03）

- Tasks/Notifications 默认仍保持最近 30 项的 bounded rendering，并新增“显示更早任务 /
  显示更早通知”渐进加载；筛选切换会重置窗口，避免在不同语义筛选之间泄漏滚动状态。
- 报告首屏操作按“来源研究”主行动与“返回/导出”次级行动分组；移动端按两组纵向排列，
  保持单一页面滚动与章节横向滚动 owner。
- Admin 无平台权限状态增加“返回控制台”恢复路径，保留账户中心入口；不改变服务端授权。
- 真实认证 Chromium 复核：Tasks `390×844`、Notifications `1280×720` 均显示渐进加载入口，
  `scrollWidth - clientWidth = 0`，console errors=0。
- Data 科学属性表增加移动端“左右滑动查看完整列”提示，保持可聚焦表格区域与
  稳定行选择；未删除列或改变数据 authority。
- Dataset 工作台增加“数据资产工作台”上下文说明与术语折叠，明确 Dataset、
  ScientificObject/Version、Profile、规范化资源和结果之间的边界；真实对象路由
  仍按 Data Platform 的权威对象/版本路径渲染，不创建第二套数据入口。
- 认证浏览器从 Data → Research 的产品导航点击过程中，文档请求增量为 `0`，
  说明当前 App Router 导航没有退化为整页重载；目标页正常到达“研究时间线”。
- 复查报告索引代码确认已存在“加载更多已验证报告 / 加载更多历史运行”边界，
  因此 UI-06 的 Reports 长列表已有共享分页入口；本批次新增的 Tasks/Notifications
  渐进入口与其保持一致。
- Account 移动端目录改为吸顶导航（`top: 56px`），长页面滚动时仍能快速回到
  个人资料、会话、密码和停用账户四个安全区段；认证浏览器实测吸顶位置稳定，
  页面高度 `3250px`、横向溢出 `0`、console errors=0。
- 报告 Figure 预览由单一柱状投影改为有界多序列 SVG 线图：保留正负值基线、
  序列边界、坐标语义和只读声明；真实报告点开后渲染 `2` 条序列、`2` 个有限点，
  无 5xx、console errors 或横向溢出。

## 移动横向内容的共享可见性微调（2026-09-03）

- 通用 `.table-scroll`、Workspace 验证数据表与报告章节导航均保留单一横向
  scroll owner；移动端增加右侧内阴影、稳定滚动条颜色与可见焦点轮廓。
- 认证 Chromium 复核：Data 验证表区域宽度 `390px`、内容宽度 `759px`；
  报告章节区域宽度 `358px`、内容宽度 `573px`；两条路径页面级
  `scrollWidth === clientWidth`，console errors=0、HTTP 5xx=0。
- 这只改善内容可发现性与键盘可达性；没有删除科学列、改变样本身份、
  修改 Result/Artifact authority 或引入第二套渲染框架。

## 当前构建报告/路由复核（2026-09-04）

- 当前生产构建运行于 `127.0.0.1:3021`，代理 API 为 `127.0.0.1:8005`；
  PostgreSQL、Redis、MinIO 与 6 个 workers 保持运行。
- 核心路由 desktop/mobile 共 `24` 个组合：`22` 个有效用户路径无
  `Internal Server Error`、`Application error`、critical 5xx、横向溢出或
  浏览器 error/warn；`/admin` 的两次 `role=alert` 均为 researcher 的预期
  `无平台管理权限` fail-closed 授权状态，不计为运行时故障。
- Report `agent2_report_401cfb421fcab8a9366e06fedb3acb6d` 桌面与
  `390x844` 均可见“查看科学依据”折叠入口；移动 document/body
  `375/375`，overflow `0`，console error/warn `0`。

## 稀疏 Figure 预览可解释性微调（2026-09-03）

- 真实报告中的持久化 Figure 预览增加序列图例和每条序列的有限点数；
  `All sites` 与 `Si` 均可辨识为各含 `1 个点`，避免少量数据被误判为
  空白或读取失败。
- 该变化仍是 Artifact 的确定性只读呈现；完整数值和可交互查看路径继续
  保留在权威 Artifact/Viewer 中，不会创建 Job、Artifact 或 ScientificResult。
- Chromium 桌面复核页面 `scrollWidth === clientWidth`，console errors=0、
  HTTP 5xx=0。

## 回收站空状态可达性微调（2026-09-03）

- 回收站在当前筛选为空时增加“查看项目”和“返回控制台”两个产品级出口，
  避免用户只能依赖全局顶栏才能离开空状态。
- 移动端两个出口在窄屏下均分可用宽度，保持主要/次要操作层级和键盘焦点可见。
- 定向测试 `TrashCenterPage.test.tsx` 为 `4 passed`；认证 Chromium 在
  `390×844` 与 `1280×720` 均显示两个出口，页面级无横向溢出、console errors=0、
  HTTP 5xx=0。
- 构建后首次复核曾出现旧 chunk 的 400 加载失败；仅重启前端 `next start`
  刷新构建产物后复核通过。PostgreSQL、Redis、MinIO、API、workers 与现有
  Chrome 标签页未关闭。

## 前端构建刷新后的全路由复核（2026-09-03）

- 前端重启后重新检查 Console、Projects、Project Overview、Data、Research、
  Reports、Tasks、Notifications、Trash、Account、Admin、Model Settings，
  共 `24` 个路由/视口组合（`390×844` 与 `1280×720`）。
- `24/24` 返回 HTTP 200；所有组合页面级横向溢出为 `0`；console errors、
  page errors 和 HTTP 5xx 均为 `0`。这确认旧 chunk 刷新没有造成跨路由回归。

## 授权科学语义搜索批次（2026-09-03）

- 搜索后端焦点测试 `tests/test_project_access.py` 为 `32 passed`；覆盖 Dataset
  的 `sample_id/formula`、ScientificObject 规范元数据、ScientificResult
  权威 fact 与 grounded finding 文本，并保持项目授权边界和精确 Result/Turn
  入口。
- 搜索不创建独立 Finding authority：发现文本仍通过授权的 ScientificResult
  投影命中，打开链接保留显式 `researchTurnId`，不依赖 Job 名称猜测。
- 认证内置浏览器在 `390×844` 搜索 `mat-2` 返回 `14` 项；Result、Research、
  Report 均可命中，打开首条 Result 到精确 Turn 路由
  `/projects/project_0002_1a0af866391f412d/research?turn=92fcd73e-3803-4dcf-bc7a-a63fbcf2a70e`
  成功，无 5xx、page/console error 或横向溢出。
- Result 搜索标题现在优先采用权威 `research_question`，其次采用 Result item
  标题，最后才回退到短 ID；副标题保留短 Result ID 与 schema 版本，用户能
  识别科学问题，同时仍可追溯精确对象。
- 搜索弹窗文案明确覆盖“科学结果与结果中的已验证发现”；错误态和已保存检索
  读取失败均提供原地重试，不清空当前关键词、筛选或项目范围。
- API 进程在标题修复后重新启动；健康检查继续为 PostgreSQL/Redis/MinIO/
  Redis worker，前端默认生产构建在 `127.0.0.1:3000`
  返回 `200`。

## 旧浏览器入口恢复（2026-09-03）

- 内置浏览器仍保留两个历史标签页，分别指向 `127.0.0.1:3013` 和
  `127.0.0.1:3016`；此前它们因旧前端进程退出而显示“无法访问此站点”，
  容易被误判为报告或科学数据损坏。
- 未关闭标签页或改变 URL；使用当前默认生产构建在两个端口启动兼容入口，
  并复用 `.env.local` 的 API 代理到 `127.0.0.1:8005`。
- 两个端口现在均返回 HTTP `200`。在 `3013` 历史报告路由
  `/projects/project_0002_1a0af866391f412d/reports/agent2_report_19a0d0c261c28577101de81532464893`
  真实打开后，报告标题、修订版本、章节导航、来源研究入口均可见，浏览器
  控制台错误为 `0`；标签页已保留供用户后续复核。

## 当前生产批次复核（2026-09-03）

- 当前生产前端由工作树重新构建，并在 `3000`、`3013`、`3016` 保持运行；
  三个 `/console` 入口均 HTTP `200`。未关闭已有浏览器标签页。
- Task Center/Notification Center 现在支持有界搜索、稳定排序和无匹配恢复；
  Scientific Report 移动端章节跳转由有序章节模型生成；Dataset workbench
  明确 Dataset、Profile、ScientificObject/Version 与 ScientificResult 的
  来源到结果边界；全局搜索覆盖授权 Dataset/Object/Result 语义内容。
- 验证：focused `44 passed`；full frontend `110 files / 803 tests passed`；
  typecheck、production build、`git diff --check` PASS。
- 认证 Chromium `390x844` 复核 Console、Projects、Tasks、Notifications、
  Trash、历史 Report：全部 HTTP `200`，无 page error、无 5xx、无全局溢出。
- `/health/runtime` 与 operations snapshot：PostgreSQL/Redis/MinIO/Redis
  worker/DeepSeek healthy，queue depth `0`，stale jobs/turns `0`，
  idle-in-transaction `0`，pool checked out `0`。
- 旧的不可恢复 payload 继续保持 fail-closed；不把缺失原始字节伪装成服务
  恢复或补造科学内容。

## 长列表与项目首页连续性补充（2026-09-03）

- Project Home 的数据集、分析历史和最近活动改为渐进式“显示更多”，项目
  历史错误态提供“重新加载”，且保留原有精确项目/研究路由。
- Task/Notification/Report/Dataset 相关 focused coverage 合计 `44 passed`；
  full frontend 已更新为 `110 files / 803 tests passed`。
- 使用用户提供的 Chromium 做认证态路由巡检：`12` 个核心路由、`3` 个前端
  端口、`2` 个视口共 `72` 次加载全部 HTTP `200`；Internal Server Error、
  不可恢复交互提示、page error、console error、5xx、横向溢出均为 `0`。
- `13` 个当前 ScientificObject 的 Data/Version/Viewer 投影在桌面与移动端
  共 `26` 次加载成功，payload 全部 READY，viewer support 全部 PROFESSIONAL。
- 历史缺失原始 payload 的 fail-closed 说明仍保留，不将缺失数据伪装成已恢复。

## 账户与管理员控制面复核（2026-09-03）

- User Center：账户资料读取失败与会话列表读取失败分别提供原地重试，
  已加载的账户内容不会因会话请求失败而消失。
- Admin Center：平台角色、账户启停、成员角色和成员移除均在服务端授权
  之上增加带后果说明的显式确认；用户/项目长列表支持有界继续加载，
  初始读取失败提供恢复入口，邀请凭证复制失败有手动复制反馈。
- Account/Admin focused `13 passed`；后端账户管理员授权 `8 passed`；
  普通用户 `/admin` 仍正确 fail-closed。
- 本地可用认证状态为普通用户，因此管理员真实浏览器变更路径没有被冒充
  为 PASS；管理员后端权限边界和 UI 确认契约已通过测试。
- 当前生产构建后的全前端回归：`110 files / 810 tests passed`；桌面/移动
  核心路由矩阵 `24/24 HTTP 200`，page/console error、5xx、全局溢出均为 0。

## 当前表格、报告与不可用状态复核（2026-09-03）

- 当前生产构建已重新加载到 `3000`、`3013`、`3016`；API、PostgreSQL、
  Redis、MinIO 与 worker 未停止。`8005/health/runtime` 与
  `3000/api/health/runtime` 均返回真实 PostgreSQL/Redis/Redis-worker/MinIO
  状态。
- 认证内置浏览器在 `3000` 报告详情页重新验证成功：报告标题、不可变版本历史、
  章节导航、精确 ScientificObjectVersion、持久化 Figure/Table Artifact 链接
  均可见；图表预览可展开并显示 `All sites / 1 个点`、`Si / 1 个点`；表格预览
  可展开并带 caption、typed headers 与精确版本；console error/warn 为 `0`，
  未出现 `Application error`、Internal Server Error 或空白报告。
- 认证内置浏览器 `390x844` 数据工作台显示已验证数据表、3/3 行、稳定
  `sample_id`（`sample-si`、`sample-fe2o3`、`sample-lifepo4`）、选择按钮与
  “左右滑动查看完整属性”语义区域；页面宽度 `375/375/375`，全局横向溢出 `0`。
- 当前前端全回归为 `110 files / 813 tests passed`；后端关键回归
  `56 passed, 1 historical compatibility skip`；production build、typecheck、
  compileall、`uv lock --check`、`git diff --check` 均通过。
- Operations snapshot（同栈）为 PostgreSQL active `1` / idle `5` /
  idle-in-transaction `0` / pool checkedOut `0`，Redis worker `6` idle、
  queues depth `0`、recentFailed `0`，MinIO bucket `mdi-artifacts` 状态 `ok`。
- 旧的无法恢复原始 payload 仍保持 fail-closed；本批没有把缺失字节伪装成
  恢复成功，也没有删除任何用户文件或临时证据。

## 当前生产路由与对象矩阵（2026-09-03）

- 认证同栈浏览器在 `1280x720` 与 `390x844` 分别巡检
  `/console`、`/projects`、项目概览、Data、Research、Reports、Report 详情、
  Tasks、Notifications、Trash、Account、Admin 共 `24/24` 路由；每次页面均无
  `Application error`、Internal Server Error、console error 或全局溢出。
- 当前项目 `project_0002_1a0af866391f412d` 的 `13/13` 个精确
  ScientificObject/Version 入口在桌面与移动端共 `26/26` 次加载成功，无
  5xx、page error、console error 或溢出。无稳定 sample identity 的旧表格继续
  可读但选择按钮按契约禁用；不会使用视觉行号冒充科学身份。
- 报告内联 Figure/Table 预览均为只读持久化 Artifact 投影：打开/收起只改变
  展示状态，不创建 Job、ToolCall、Artifact 或 ScientificResult。

## 导航、研究控制与科学表面批量修复（2026-09-03）

- 登录后的品牌入口与显式“控制台”入口统一指向 `/console`；顶层 Projects、
  Console、Account、Admin 增加统一 RouteLoading frame，服务端数据等待时
  保留工作区层级和即时反馈。
- Continue 子 Turn 显式绑定父 Turn 的精确 Result snapshot；PLAN_READY
  自动 dispatch 与 Stop 竞态按持久化终态收敛，避免伪执行失败。
- Electronic/DOS、Phonon Band/DOS、Volumetric 对大合法 payload 使用安全迭代
  和有界绘制；无有限值时呈现可解释空状态，表格补充语义化列。
- 相关前端聚焦 `99 passed`，完整前端回归 `110 files / 818 tests passed`；
  typecheck/build/compileall/lock/diff check 均通过；同栈 operations snapshot
  为 PostgreSQL/Redis/MinIO `ok`，6 workers idle，queue depth `0`，
  idle-in-transaction `0`。

## 当前构建移动导航复核（2026-09-03）

- 通过保留服务并行启动的 `3018` 当前构建完成认证浏览器复核：桌面核心路由
  `11/11`、移动核心路由 `11/11` 均无 `Application error`、Internal Server
  Error、console error 或全局横向溢出。
- `390x844` 项目工作区顶栏的“控制台 / 任务 / 通知 / 回收站 / 搜索 / 账户”
  入口均可见，其中“控制台”保持单行，不影响项目内“概览 / 数据 / 研究 /
  报告”导航层级。
- 当前构建的认证浏览器又遍历了项目内 `13/13` 个真实
  ScientificObject/Version 入口（Electronic DOS、Phonon Band/DOS、Dataset、
  Band、Trajectory、Structure 等），全部无 Internal Server Error、page/console
  error、SOURCE_MISSING 或全局溢出；该批次没有把缺失 payload 伪装成成功。

## 导航、研究控制与科学表面批量修复（2026-09-03）

- 登录后的品牌入口和显式“控制台”入口统一指向 `/console`，深层工作区
  可直接返回主工作台；顶层 Projects/Console/Account/Admin 增加统一
  RouteLoading frame，等待服务端数据时不再出现空白。
- Continue 子 Turn 显式绑定父 Turn 的精确 Result snapshot；PLAN_READY
  自动 dispatch 与 Stop 竞态根据持久化终态收敛，避免伪“研究执行失败”。
- Electronic/DOS、Phonon Band/DOS、Volumetric 的大数组统计使用安全迭代和
  有界绘制；无有限值时展示可解释空状态，表格补充语义化列范围。
- 相关前端聚焦 `99 passed`，typecheck/build/compileall/lock/diff check 均通过；
  同栈 operations snapshot 仍为 PostgreSQL/Redis/MinIO `ok`、6 workers idle、
  queue depth `0`、idle-in-transaction `0`。

## 数据层级与导航感知性能批次复核（2026-09-04）

- Data 页面左侧在筛选控件之后直接呈现“来源数据与科学身份”说明，以两张
  紧凑卡片解释 Dataset 与 Scientific Object/Version 的职责边界；桌面位于
  数据集列表之前，移动端换行正常且无全局溢出。
- `getCachedProjectHistory` 仅返回已成功解析且仍在 30 秒 TTL 内的快照，不会
  启动隐式请求；概览/数据/研究路由命中后直接绘制，未命中仍走原有失败可重试
  路径。Console 的主项目在用户点击前由现有请求去重机制预热。
- 定向 `69 passed`、typecheck、production build、diff check 通过；3020 认证
  浏览器数据页无 page/console error，移动 `scrollWidth === clientWidth === 375`，
  同栈服务健康检查为 PostgreSQL/Redis/MinIO/Redis worker。
- 这批只改善可理解性和感知等待；未改变科学对象、不可变版本、结果或历史
  payload 的权威语义。缺失精确字节仍按 fail-closed 展示，不进行静默替换。
