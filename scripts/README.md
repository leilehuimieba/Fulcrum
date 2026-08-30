# scripts

可复现脚本目录。

本目录用于放置运行、部署、评测、数据处理等可重复执行的脚本。

约定:

- 脚本应有清晰命名、参数说明和失败提示。
- 不提交一次性调试脚本;确需保留时说明用途和生命周期。
- 脚本不得内置密钥、账号、真实路径或个人机器配置。
- 重要脚本应在 README 或相关文档中说明运行方式。

仓库治理检查:

```powershell
uv run python scripts/check_markdown_links.py
uv run python -m fulcrum.openapi --check
```

第一条检查根目录 `*.md` 与 `docs/**/*.md` 的本地链接;第二条只读比较运行时 OpenAPI 与入库生成契约。两条命令失败时均返回非零退出码。
