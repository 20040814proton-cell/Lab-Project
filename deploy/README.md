# 维护操作执行手册 V2

## ⚠️ 最高级安全红线（全局强制）

- 绝对禁止执行 `docker compose down -v`。
- 绝对禁止执行 `docker volume rm ...` 或 `docker system prune --volumes`。
- MongoDB 生产数据依赖 Docker Volume 持久化，误删卷会导致数据库不可逆清空。
- 所有容器启停命令只允许 `up/down/restart`，且不带 `-v`。

## Summary

本项目生产环境采用以下固定策略：

- 前后端分离的混合部署流：服务器只构建后端，前端只在本地构建后上传 `dist`。
- Web 层统一使用 Caddy：静态文件服务 + `/api` 反代。
- 数据安全优先：所有维护动作必须保护 Mongo Volume。

## 架构边界

- 对外入口：`http(s)://<domain>`（由 Caddy 提供）。
- Caddy 静态根目录：容器内 `/srv`（宿主机挂载 `/opt/lab-ecosystem/dist`）。
- 后端服务：`backend:8000` 仅容器网络可见。
- 健康检查：`/healthz`、`/readyz`。

## 1. 服务器准备与安全确认

```bash
cd /opt/lab-ecosystem
docker volume ls
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod config
```

说明：

- 任何时候都不要执行带 `-v` 的下线命令。
- `deploy/.env.prod` 必填：`CADDY_SITE_HOST`、`LAB_MONGO_URI`、`LAB_MONGO_DB`、`LAB_JWT_SECRET`、`LAB_CORS_ORIGINS`、`LAB_STATIC_DIR`。

## 2. 后端与环境更新（纯 Git + Docker）

服务器执行：

```bash
cd /opt/lab-ecosystem
git pull
bash deploy/linux/check-prod.sh
bash deploy/linux/deploy-prod.sh
```

仅当 Caddy 配置有变更时：

```bash
bash deploy/linux/deploy-prod.sh --with-caddy
```

注意：

- 服务器端禁止执行任何前端构建命令（`pnpm build` / `npm run build`）。

## 3. 前端更新（本地构建 + 物理上传）

在本地开发机执行：

```bash
pnpm install
pnpm build
```

上传方式（二选一）：

- 用 WinSCP/SFTP 直接覆盖上传本地 `dist/` 到服务器 `/opt/lab-ecosystem/dist`。
- 或使用脚本：

```bash
bash deploy/linux/sftp-upload-dist.sh <user> <host> [identity_file]
```

上传后（可选）重载 Caddy：

```bash
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod restart caddy
```

## 4. 外置大静态资源（非 Git）

本地目录与服务器目录映射：

- `public/images` -> `/srv/lab-static/images`
- `photos` -> `/srv/lab-static/photos`
- `demo` -> `/srv/lab-static/demo`

可用脚本：

```bash
bash deploy/linux/sftp-upload-static.sh <user> <host> [identity_file]
```

## 5. Caddy-only 规则

生产环境不再使用 Nginx，统一由 Caddy 承担：

- 静态站点：`/srv`
- `/api/*` -> `backend:8000`
- `/static/*` -> `backend:8000`
- SPA fallback：`try_files {path} /index.html`

`CADDY_SITE_HOST` 用法：

- 域名模式（自动 HTTPS）：如 `lab.example.com`
- 临时 IP 调试（HTTP）：如 `:80`

## 6. 回滚与备份

后端回滚：

```bash
bash deploy/linux/rollback.sh
```

后端回滚并重载 Caddy：

```bash
bash deploy/linux/rollback.sh --restart-caddy
```

Mongo 备份（默认保留 7 份）：

```bash
bash deploy/linux/backup.sh 7
```

## 7. 验收清单

- 安全：操作日志中没有 `-v` 参数命令。
- 发布合规：服务器未执行前端构建；前端通过本地 build + 上传发布。
- 网关正确：`/api/*`、`/static/*` 正常反代；深层路由刷新不 404。
- 可用性：`/healthz`、`/readyz` 返回 200。
- 业务回归：`/forum`、`/forum/{id}`、`/news/{id}` 正常；动态详情返回按钮与上一篇/下一篇正常。
