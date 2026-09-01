# TS Knowledge Agent 路线图

## V1：本地知识闭环

1. CLI 初始化：固定 Git 仓、`member_id`、个人知识空间和本地源目录。
2. 每小时扫描：识别新增、修改、路径变化和源文件缺失。
3. MarkItDown 转换：保留源文件，生成带来源元数据的 Markdown。
4. Agent/模型提炼：生成候选知识并写入当前成员空间。
5. SQLite：保存本地任务状态、哈希和全文索引。
6. 每小时批次 Git 同步：pull、检查、commit、push、远程 SHA 回读。
