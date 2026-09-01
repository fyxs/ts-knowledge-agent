# TS Knowledge Agent

本项目是 TS 团队共享知识库的本地知识处理应用，后续可包含 CLI、本地搜索服务和 Web 界面。

## 当前阶段

第一期只实现知识搜集、转换、沉淀和搜索闭环，不实现外部 Agent 子 Agent/MCP/HTTP 接入，不实现 Claude Code 或 Hermes 的任务执行能力。

## 依赖的知识仓库

固定远程仓库：`git@github.com:fyxs/ts-knowledge-base.git`

本项目与知识仓库分离：本项目存应用代码；知识仓库存团队共享知识。

## 文档

- `docs/design-v1.md`：V1 产品和技术设计
- `docs/logging-v1.md`：日志系统设计
- `docs/roadmap.md`：后续迭代边界
