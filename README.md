# Lab-Project 维护与部署总手册

> 适用目录：`/opt/lab-ecosystem`
>
> 适用架构：Vue + FastAPI + MongoDB + Caddy + Docker Compose

## ⚠️ 最高安全红线（必须遵守）

- 禁止执行：`docker compose down -v`
- 禁止执行：`docker volume rm ...`
- 禁止执行：`docker system prune --volumes`

Mongo 数据依赖 Docker Volume 持久化，误删卷会导致数据库不可逆丢失。

## 1. 项目结构与发布边界

- 前端：本地机器构建（`pnpm build`），上传 `dist/` 到服务器
- 后端：服务器通过 Git 拉代码 + Docker 构建并重启 `backend`
- 网关：只使用 Caddy（不再使用 Nginx）
- 对外：`http(s)://<domain>`
- 反代：`/api/*`、`/static/*` -> `backend:8000`

## 2. 本地开发启动

### 2.1 前端本地启动

```bash
pnpm install
pnpm dev
```

默认前端地址：`http://localhost:3333`

### 2.2 后端本地启动

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

后端健康检查：

- `http://127.0.0.1:8000/healthz`
- `http://127.0.0.1:8000/readyz`

## 3. 服务器首次准备（生产）

1. 准备目录：`/opt/lab-ecosystem`
2. 放置配置：`deploy/.env.prod`（参考 `deploy/.env.example`）
3. 校验 compose：

```bash
cd /opt/lab-ecosystem
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod config
```

4. 首次启动：

```bash
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build
```

## 4. 后端一键更新（推荐）

在服务器创建 `update.sh`：

```bash
cd /opt/lab-ecosystem
nano update.sh
```

写入以下脚本：

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "SAFETY RED LINE:"
echo "  NEVER run docker compose down -v"
echo "  NEVER remove docker volumes"

cd /opt/lab-ecosystem

echo "==> Pull latest backend/deploy code"
git fetch --all
git checkout main
git reset --hard origin/main
git pull origin main

echo "==> Rebuild and restart backend only"
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build backend

echo "==> Done"
```

赋权并执行：

```bash
chmod +x /opt/lab-ecosystem/update.sh
/opt/lab-ecosystem/update.sh
```

说明：

- 这个脚本只更新 Git 跟踪代码（后端/部署文件）
- 不会删除 SFTP 上传的 `dist`、`/srv/lab-static` 大资源
- 不会触碰 Docker Volume（前提是你不执行带 `-v` 的命令）

## 5. 前端发布（强制本地构建）

### 5.1 本地构建

```bash
pnpm install
pnpm build
```

### 5.2 上传 dist 到服务器

上传本地 `dist/` 到服务器：

- 目标目录：`/opt/lab-ecosystem/dist`
- 方式：WinSCP / SFTP / `deploy/linux/sftp-upload-dist.sh`

上传后可重启 Caddy：

```bash
cd /opt/lab-ecosystem
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod restart caddy
```

## 6. 静态大资源发布（不走 Git）

本地目录到服务器目录：

- `public/images` -> `/srv/lab-static/images`
- `photos` -> `/srv/lab-static/photos`
- `demo` -> `/srv/lab-static/demo`

可用脚本：

```bash
bash deploy/linux/sftp-upload-static.sh <user> <host> [identity_file]
```

## 7. 日常运维命令

### 7.1 快速检查

```bash
cd /opt/lab-ecosystem
bash deploy/linux/check-prod.sh
```

### 7.2 标准后端发布

```bash
cd /opt/lab-ecosystem
bash deploy/linux/deploy-prod.sh
```

若改了 Caddyfile：

```bash
bash deploy/linux/deploy-prod.sh --with-caddy
```

### 7.3 回滚后端

```bash
cd /opt/lab-ecosystem
bash deploy/linux/rollback.sh
```

### 7.4 Mongo 备份

```bash
cd /opt/lab-ecosystem
bash deploy/linux/backup.sh 7
```

### 7.5 初始化/重置超级账号

首次创建（在服务器执行）：

```bash
cd /opt/lab-ecosystem
bash deploy/linux/init-superadmin.sh
```

默认账号密码：

- 用户名：`superadmin`
- 密码：`123456`

已存在账号时重置密码：

```bash
cd /opt/lab-ecosystem
bash deploy/linux/init-superadmin.sh superadmin "123456" "System Administrator" --reset-if-exists
```

## 8. 故障排查

### 8.1 检查容器状态

```bash
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod ps
```

### 8.2 查看日志

```bash
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod logs -f backend
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod logs -f caddy
```

### 8.3 健康检查

- `https://<domain>/healthz`
- `https://<domain>/readyz`

### 8.4 前端报错：`Failed to resolve import "/images/..."`

原因通常是仓库已把大静态资源外置，`public/images` 本地不完整。

处理方式：

1. 本地开发需要这批资源时，先把 `images/photos/demo` 同步回本地对应目录。
2. 仅做后端开发时，可不启动前端构建流程。
3. 线上以 `/srv/lab-static` 为准，按手册第 6 节用 SFTP 维护。

## 9. 关键文件索引

- 部署手册（详细）：`deploy/README.md`
- 生产编排：`deploy/docker/docker-compose.prod.yml`
- Caddy 配置：`deploy/docker/Caddyfile.prod`
- 后端 Dockerfile：`deploy/docker/Dockerfile.backend`
- 一键发布脚本：`deploy/linux/deploy-prod.sh`
- 一键回滚脚本：`deploy/linux/rollback.sh`
- 超管初始化脚本：`deploy/linux/init-superadmin.sh`
- dist 上传脚本：`deploy/linux/sftp-upload-dist.sh`
- 静态资源上传脚本：`deploy/linux/sftp-upload-static.sh`

## License

- Code: [MIT](./LICENSE)
- Some words/images: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
