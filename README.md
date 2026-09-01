# TS Knowledge Agent

TS 团队共享知识库的本地 Agent 应用。第一期实现本地知识源扫描、材料转换、知识沉淀、Git 同步和搜索服务；应用代码与 `ts-knowledge-base` 知识仓分离。

## 技术基线

- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: FastAPI + Python
- Local state/index: SQLite + FTS5
- Material conversion: MarkItDown（由应用运行环境管理）
- Model: 沿用当前 Harness 工作模型
- Agent UI protocol: AG-UI；一期先建立协议边界，默认 SSE，WebSocket 仅作后续特殊传输
- Shared knowledge: fixed Git remote `git@github.com:fyxs/ts-knowledge-base.git`

## Repository boundary

本仓库存放 CLI、本地 Web、扫描、转换、索引、Git 同步和服务实现；团队知识内容存放在 `ts-knowledge-base`。

## Current status

当前为可运行的基础工程骨架，核心业务尚未实现。先以接口、目录和测试边界稳定设计，再逐步实现垂直切片。
