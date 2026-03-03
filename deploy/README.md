# Deployment Commands

## Linux Production (CentOS/RHEL)

### 1. Edit production env

Update `deploy/.env.prod`:

- `CADDY_SITE_HOST=<your-domain>`
- `LAB_CORS_ORIGINS=https://<your-domain>`
- `LAB_JWT_SECRET=<strong-random-secret>`
- Keep `LAB_MONGO_URI=mongodb://mongo:27017`

### Static files are external to Git

Upload static folders to server path `/srv/lab-static` (via SFTP):

- `public/images` -> `/srv/lab-static/images`
- `photos` -> `/srv/lab-static/photos`
- `demo` -> `/srv/lab-static/demo`

You can use:

```bash
bash ./deploy/linux/sftp-upload-static.sh <user> <host> [identity_file]
```

### 2. Run checks

```bash
bash ./deploy/linux/check-prod.sh
```

### 3. Deploy

```bash
bash ./deploy/linux/deploy-prod.sh
```

### 4. Rollback

```bash
bash ./deploy/linux/rollback.sh
```

### 5. Mongo backup

```bash
bash ./deploy/linux/backup.sh 7
```

## Expected production entrypoint

`https://<your-domain>`

## Legacy Windows scripts

Windows scripts are kept under `deploy/windows/` as a fallback path, but Linux production is the primary deployment route now.

## One-time Git history cleanup (optional, destructive)

Only run this if you want to remove large static files from repository history.

```bash
git tag before-history-cleanup
git clone --mirror <repo-url> repo-backup.git
git clone --mirror <repo-url> repo-cleanup.git
cd repo-cleanup.git
git filter-repo --path public/images --path photos --path demo --invert-paths --force
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git remote set-url origin https://github.com/godcplus/-.git
git push --force --all origin
git push --force --tags origin
```
