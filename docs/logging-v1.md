# 日志系统设计 V1

## 结论

需要日志，但第一期不需要独立的日志平台。采用“本地结构化运行日志 + SQLite 任务记录 + Git 变更历史”的轻量方案。

## 三种记录分工

- **运行日志**：记录扫描、转换、提炼、索引和搜索过程中的事件、耗时、错误和诊断信息。
- **SQLite 任务记录**：记录任务状态、输入输出、哈希、重试次数和最后错误，支持应用重启后恢复。
- **Git 历史**：记录进入团队知识仓的内容变更、来源登记和知识演进，不承担运行日志。

## 第一期开启的事件

每次任务至少记录：`event_id`、`run_id`、`event_type`、`timestamp`、`member_id`、`source_path`（必要时脱敏）、`source_hash`、`status`、`duration_ms`、`error_code`、`message`。

事件类型：`scan_started`、`file_discovered`、`conversion_started`、`conversion_succeeded`、`conversion_failed`、`extraction_started`、`extraction_succeeded`、`extraction_failed`、`index_updated`、`git_sync`、`search`。

## 安全与隐私

日志不得记录文件正文、模型密钥、Token、密码、Cookie 或完整模型请求。错误信息需要脱敏；源路径是否完整记录由本地配置决定。默认保留最近 30 天运行日志，SQLite 任务记录按知识生命周期保留必要摘要。

## 为什么需要日志

- 判断扫描是否真的执行；
- 区分未发现、未转换、转换失败和索引未更新；
- 支持失败重试和断点恢复；
- 诊断模型调用、MarkItDown 和 Git 同步问题；
- 为后续质量统计和团队维护提供事实。

## 第一版不做

- 不接入 ELK、Loki、云日志平台；
- 不建立复杂监控大盘；
- 不把日志提交到共享知识仓；
- 不用日志替代知识来源、验证记录或 Git 历史。

## 最小实现

```text
logs/app.jsonl       本地结构化日志
SQLite runs/events   本地任务状态和可查询事件
Git commits          共享知识变更历史
```

发生错误时，CLI 和 Web 只展示 `run_id`、错误摘要和下一步建议，详细日志留在本机。
