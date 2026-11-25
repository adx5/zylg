# 部署说明（阿里云 · nginx 同源反代方案）

## 架构

```
浏览器 ──► http://47.94.96.227/           nginx 托管 frontend/dist
                │
                └─ /api/ ──► 127.0.0.1:8000  FastAPI（gunicorn/uvicorn）
```

前端只请求相对路径 `/api`，由 nginx 转发。**不涉及 CORS**，以后上 HTTPS 也不会出现混合内容拦截。

---

## 一、服务器目录

```bash
mkdir -p /var/www/linggong/dist
mkdir -p /opt/linggong/backend
```

## 二、部署后端

1. 上传 `backend/` 到 `/opt/linggong/backend`，建虚拟环境并装依赖：

```bash
cd /opt/linggong/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. 配置 `.env`（至少确认这几项）：

```ini
ENV=production
SECRET_KEY=<强随机串，≥32 位>
DATABASE_URL=<Neon/自建 PG 连接串>
REDIS_URL=<Redis 连接串>
```

> 注意：`ENV=production` 时若 `SECRET_KEY` 未配置，服务会**拒绝启动**（fail-closed）。
> 另外当前 `.env` 里 `DATABASE_URL / REDIS_URL / SECRET_KEY` 各有重复定义，建议清理只留一份。

3. 跑数据库迁移：

```bash
. .venv/bin/activate
alembic upgrade head
```

4. systemd 托管（`/etc/systemd/system/linggong-api.service`）：

```ini
[Unit]
Description=linggong API
After=network.target

[Service]
WorkingDirectory=/opt/linggong/backend
Environment="PYTHONIOENCODING=utf-8"
ExecStart=/opt/linggong/backend/.venv/bin/gunicorn main:app \
  -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 \
  --timeout 120 --access-logfile -
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now linggong-api
curl -s http://127.0.0.1:8000/health
```

> 只监听 `127.0.0.1:8000`，不对外暴露端口，全部流量走 nginx。

## 三、部署前端

1. 本地构建（会读取 `frontend/.env.production` 的 `VITE_API_BASE_URL=/api`）：

```bash
cd frontend
npm run build
```

2. 上传 `frontend/dist/*` 到 `/var/www/linggong/dist/`。

> **换 IP / 换域名 / 换端口都不用改前端代码**，因为走的是相对路径。

## 四、配置 nginx

```bash
cp deploy/nginx-linggong.conf /etc/nginx/conf.d/linggong.conf
nginx -t && systemctl reload nginx
```

## 五、阿里云安全组

| 端口 | 用途 | 建议来源 |
|---|---|---|
| 80 | 前端 | 0.0.0.0/0 |
| 443 | 前端 HTTPS（后续） | 0.0.0.0/0 |
| 8000 | **不要对外开放**（nginx 内部转发） | 关闭 |

## 六、验收清单

```bash
curl -I http://47.94.96.227/                       # 200，返回 index.html
curl -s http://47.94.96.227/healthz                # {"status":"ok",...}
curl -s -X POST http://47.94.96.227/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"phone":"13900010001","target_role":"worker"}'   # 返回 token
```

浏览器打开 `http://47.94.96.227/#/login` → 用 `13900010001` 登录。

## 七、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 登录报「网络连接失败」 | nginx 未代理 `/api`，或后端没起 | `nginx -t` + `systemctl status linggong-api` |
| 502 Bad Gateway | 后端进程挂了 | 看 `journalctl -u linggong-api -n 100` |
| 页面白屏 | dist 路径配错 | 确认 `root` 指向 dist 且 `index.html` 存在 |
| 管理端 403 | `ENFORCE_ADMIN_IP` 开启但 IP 不在白名单 | 加 IP 或先关闭该开关 |
| 证书上传失败 | 体积超限 | 已设 `client_max_body_size 10m`；后端另有压缩校验 |

## 八、后续上 HTTPS

用 certbot 申请证书后，把 80 的 server 块改成 443，并加 80→443 跳转即可。
因为 API 走同源 `/api`，**不需要再改任何前端配置**。
