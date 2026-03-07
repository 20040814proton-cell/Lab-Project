# Lab Ecosystem 维护手册

## ⚠️ 数据安全红线（最高优先级）

- 严禁执行：`docker compose down -v`
- 严禁执行：`docker volume rm ...`
- 严禁执行：`docker system prune --volumes`

MongoDB 依赖 Docker Volume 持久化。误删 Volume 会导致数据库不可逆清空。

---

## 1. 架构与发布边界

- Frontend: Vue + Vite
- Backend: FastAPI + Beanie + MongoDB
- Gateway: Caddy
- Orchestration: Docker Compose

固定发布规则：

1. 服务器禁止前端构建（禁止 `pnpm build` / `npm run build`）。
2. 后端与部署配置走 Git（`git pull` + Docker 重建 backend）。
3. 前端必须本地构建，再通过 SFTP/WinSCP 上传 `dist/`。

---

## 2. 本地启动（开发）

## 2.1 依赖

- Node.js 20+
- pnpm 9+
- Python 3.10+
- Docker Desktop（用于本地 Mongo）

## 2.2 启动 MongoDB

PowerShell：

```powershell
if (docker ps -a --format '{{.Names}}' | Select-String '^lab-mongo$') {
  docker start lab-mongo
}
else {
  docker run -d --name lab-mongo -p 27017:27017 mongo:7
}
```

说明：如果你看到 `Conflict. The container name "/lab-mongo" is already in use`，直接执行 `docker start lab-mongo`。

## 2.3 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:LAB_MONGO_URI='mongodb://127.0.0.1:27017'
$env:LAB_MONGO_DB='lab_ecosystem'
$env:LAB_JWT_SECRET='dev_secret_change_me'
$env:LAB_CORS_ORIGINS='http://localhost:3333,http://127.0.0.1:3333'

uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

- <http://127.0.0.1:8000/healthz>
- <http://127.0.0.1:8000/readyz>

## 2.4 启动前端

新开终端，在项目根目录执行：

```powershell
pnpm install
pnpm dev
```

访问：<http://localhost:3333>

说明：开发环境前端默认请求 `http://127.0.0.1:8000`（见 `src/logics/api.ts`）。

## 2.5 本地常见问题

1. `Failed to resolve import "/images/..."`
- 原因：仓库已瘦身，大静态资源不在 Git。
- 处理：把 `public/images`、`photos`、`demo` 同步回本地再开发。

2. 登录报 404 或 HTML 被当 JSON
- 原因：后端没启动，或接口请求被打到静态服务。
- 处理：确认 `uvicorn` 在 `127.0.0.1:8000` 正常监听。

---

## 3. 服务器发布（生产）

## 3.1 后端发布（Git + Docker）

```bash
cd /opt/lab-ecosystem
git pull
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build backend
```

如果改了 Caddy 配置，再执行：

```bash
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build caddy
```

## 3.2 前端发布（本地构建 + SFTP）

本地机器：

```powershell
pnpm install
pnpm build
```

上传本地 `dist/` 到服务器：

- `/opt/lab-ecosystem/dist`

必要时重载 Caddy：

```bash
cd /opt/lab-ecosystem
docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod restart caddy
```

## 3.3 大静态资源（不走 Git）

- `public/images` -> `/srv/lab-static/images`
- `photos` -> `/srv/lab-static/photos`
- `demo` -> `/srv/lab-static/demo`

可用脚本：

- `deploy/linux/sftp-upload-static.sh`
- `deploy/linux/sftp-upload-dist.sh`

---

## 4. 一键后端更新脚本（update.sh）

服务器 `/opt/lab-ecosystem/update.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /opt/lab-ecosystem

git fetch --all
git checkout main
git reset --hard origin/main
git pull origin main

docker compose -f deploy/docker/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build backend
```

赋权与执行：

```bash
chmod +x /opt/lab-ecosystem/update.sh
/opt/lab-ecosystem/update.sh
```

---

## 5. 超级管理员初始化

```bash
cd /opt/lab-ecosystem
bash deploy/linux/init-superadmin.sh
```

默认账号：

- 用户名：`superadmin`
- 密码：`123456`

重置示例：

```bash
bash deploy/linux/init-superadmin.sh superadmin "123456" "System Administrator" --reset-if-exists
```

---

## 6. 常用运维命令

```bash
cd /opt/lab-ecosystem
bash deploy/linux/check-prod.sh
bash deploy/linux/deploy-prod.sh
bash deploy/linux/rollback.sh
bash deploy/linux/backup.sh 7
```

---

## 7. 关键文件

- `deploy/docker/docker-compose.prod.yml`
- `deploy/docker/Caddyfile.prod`
- `deploy/docker/Dockerfile.backend`
- `deploy/.env.prod`
- `src/logics/api.ts`
- `deploy/linux/*.sh`