# 枢衡文档地图与单一真源

> 本文回答什么问题:某类事实应在哪里修改、哪些文件是作者真源、哪些文件是生成产物、提交前如何校验。
> 状态:定稿 v1。

---

## 1. 使用原则

1. 同一事实只在一个作者真源中维护,其它文档使用相对链接引用。
2. 生成产物由确定性命令重建,不得手工修改来掩盖上游漂移。
3. 当前进度先更新进度看板;架构、指标或样例契约变化再同步各自真源。
4. 历史报告记录当时证据,不替代当前代码、运行时和进度看板。

## 2. 真源矩阵

| 事实类型 | 单一真源 | 类型 | 修改规则 |
|---|---|---|---|
| 项目定位、范围与目标 | [plan/00-项目大方向.md](plan/00-项目大方向.md) | 作者真源 | 方向变化先评审,再同步 README 导航 |
| 当前实现进度 | [plan/03-进度看板.md](plan/03-进度看板.md) | 作者真源 | 模块状态变化优先更新此处 |
| 总体架构与边界 | [arch/00-技术架构总览.md](arch/00-技术架构总览.md) | 作者真源 | 重大架构变化记录取舍、失败模式和修订 |
| 评测指标定义 | [eval/00-评测指标体系.md](eval/00-评测指标体系.md) | 作者真源 | 先定义公式、方向、数据与复现方式,再报告效果 |
| 评测语料 schema 与金标 | [../samples/eval/corpus/SPEC.md](../samples/eval/corpus/SPEC.md) | 作者真源 | 冻结语料变更遵循 SPEC 的版本和标注规则 |
| API 消费契约 | [api/openapi.json](api/openapi.json) | 生成产物 | 修改后端路由/schema 后重新生成,禁止手改 JSON |
| 仓库协作与安全规则 | [../AGENTS.md](../AGENTS.md) | 作者真源 | 只维护长期稳定约定,不写短期计划 |

根目录 [README.md](../README.md) 是项目门面和导航,不是上述事实的第二份副本。

## 3. 生成产物

### OpenAPI

作者真源是 `src/fulcrum` 中实际注册的 FastAPI 路由与 Pydantic schema;`api/openapi.json` 是供前端和集成方消费的生成快照。

```powershell
uv run python -m fulcrum.openapi
uv run python -m fulcrum.openapi --check
```

第一条更新生成物;第二条只读比较,漂移或文件缺失时返回退出码 `1`。

### 评测结果

`docs/eval/results/` 是运行产物目录并被忽略,不作为指标定义或稳定效果结论的真源。需要入库的实验结论应记录数据、环境、命令和绝对日期,放入 `docs/eval/` 的正式文档。

## 4. 提交前校验

```powershell
uv run python scripts/check_markdown_links.py
uv run python -m fulcrum.openapi --check
```

Markdown 检查覆盖根目录 `*.md` 和 `docs/**/*.md` 的本地文件/目录链接,忽略 HTTP(S)、`mailto`、纯页内锚点和代码围栏。当前不验证远程站点可达性,也不验证目标文档中的锚点名称。

CI 对每个 PR 运行这两条门禁。pre-commit 在相关文件变化时执行同一命令;CI 是最终兜底,不会因本地未安装 hook 而跳过。

---

## 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1 | 2026-07-31 | 建立文档真源矩阵、生成产物边界和仓库校验入口 |
