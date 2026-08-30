# 枢衡 API 契约(OpenAPI)

> 本文回答什么问题:OpenAPI 契约由什么生成、如何更新、如何检查漂移。
> 状态:定稿 v2。

`openapi.json` 是供前端和集成方消费的**生成契约**,由 FastAPI 路由 + Pydantic schema 自动产出。作者真源是后端路由和 schema,不得手工修改 JSON 来掩盖漂移。

## 重新生成

后端路由/DTO 有改动后,重跑导出并提交更新后的 `openapi.json`:

```bash
uv run python -m fulcrum.openapi            # 写入 docs/api/openapi.json
uv run python -m fulcrum.openapi --out 其它路径.json
uv run python -m fulcrum.openapi --check    # 只比较,漂移时退出码为 1
```

导出构建完整 app(含鉴权/管理/网关路由),鉴权/网关/审计库指向临时目录、用完即弃,
不在 `data/runtime` 留任何副本。

## 覆盖范围

核心安全(`/v1/chat/completions`、`/tools/call`、`/audit/{session_id}`)、前置网关
(`/gateway/chat`、`/admin/gateway-config`)、登录鉴权(`/auth/*`)、管理后台(`/admin/*`)、
健康检查(`/healthz`)。

## 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1 | 2026-06-16 | 建立 OpenAPI 导出与消费约定 |
| v2 | 2026-07-31 | 区分作者真源与生成契约,增加只读漂移检查 |
