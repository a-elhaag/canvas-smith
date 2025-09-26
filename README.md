<div align="center">

# Canvas Smith

Single-container full‑stack application combining a FastAPI backend and a Vue 3 (Vite + Tailwind) frontend.

Backend serves the compiled frontend (Vite build) from the same container for a simple deployment footprint (ideal for Azure Container Apps).

</div>

---

## ✨ Features

- FastAPI backend (health/status/info endpoints, CORS, static serving)
- Vue 3 + Vite + Tailwind CSS frontend
- Single Docker image (multi-stage build) – backend + built frontend
- Optional local dev with virtual environment
- Healthcheck endpoint (`/health`) & status endpoint (`/api/status`)
- Ready for Azure Container Apps deployment via `deploy-azure.sh`

---

## 🗂 Project Structure

```
backend/
	main.py               # FastAPI app (serves API + built frontend if present)
	requirements.txt
	static/               # (runtime) Copied Vite build output (index.html + assets/)
frontend/
	src/                  # Vue application source
	package.json
Dockerfile              # Multi-stage: build frontend then assemble Python image
docker-compose.yml      # Single service container for local run
deploy-azure.sh         # Script to deploy to Azure Container Apps
.env.azure              # (optional) Azure environment variables (ignored by git)
README.md               # This file
```

---

## ✅ Prerequisites

| Tool                 | Needed For                                   | Notes                          |
| -------------------- | -------------------------------------------- | ------------------------------ |
| Python 3.11+         | Local backend dev                            | Docker image uses 3.11-slim    |
| Node 20+ / pnpm      | Frontend dev (optional if using only Docker) | `corepack enable` enables pnpm |
| Docker               | Containerized dev/prod                       | Required for production build  |
| Azure CLI (optional) | Deployment                                   | `az login` before deploy       |

---

## 🔧 Local Development (without Docker)

Backend (create virtual environment):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py  # or: uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

Access:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🐳 Run Everything via Docker (recommended)

Build + start container:

```bash
docker-compose build
docker-compose up -d
```

Endpoints:

- App / Frontend: http://localhost:8000 (served from built `frontend/dist` copied into backend `static/`)
- API root (same): http://localhost:8000/
- Health: http://localhost:8000/health
- Status JSON: http://localhost:8000/api/status
- Info JSON: http://localhost:8000/api/info
- Swagger UI: http://localhost:8000/docs

Logs & lifecycle:

```bash
docker-compose logs -f
docker-compose ps
docker-compose restart
docker-compose down
```

Rebuild after code changes that affect dependencies or frontend build:

```bash
docker-compose build --no-cache && docker-compose up -d
```

---

## 🏗 Build Production Image Manually

```bash
docker build -t canvas-smith:latest .
docker run -p 8000:8000 canvas-smith:latest
```

---

## ☁️ Azure Container Apps Deployment

Prerequisites:

```bash
az login
az extension add --name containerapp --upgrade
```

Deploy:

```bash
./deploy-azure.sh
```

Script does:

1. Create resource group
2. Create Azure Container Registry (ACR)
3. Build & push image in ACR
4. Create Container Apps Environment
5. Deploy container with external ingress
6. Output public FQDN

If updating code later:

```bash
az acr build --registry <ACR_NAME> --image canvas-smith:latest .
az containerapp update --name canvas-smith --resource-group <RG> --image <ACR_LOGIN_SERVER>/canvas-smith:latest
```

---

## ⚙️ Environment Variables

| Variable       | Purpose                             | Default     |
| -------------- | ----------------------------------- | ----------- |
| PORT           | Backend listening port              | 8000        |
| SERVE_FRONTEND | Serve built frontend from `static/` | true        |
| STATIC_DIR     | Directory containing built frontend | static      |
| ENVIRONMENT    | Environment label                   | development |

Frontend build should output to `frontend/dist/`. Dockerfile copies that to `/app/static/`.

---

## 🧪 Health & Diagnostics

| Endpoint      | Description       | Example                   |
| ------------- | ----------------- | ------------------------- |
| `/health`     | Basic healthcheck | 200 OK JSON               |
| `/api/status` | Connection status | backend_status + message  |
| `/api/info`   | Metadata / mode   | includes `serve_frontend` |
| `/docs`       | Swagger UI        | interactive API           |

Docker healthcheck uses `/health`.

---

## 🛠 Common Tasks

| Task          | Command                                 |
| ------------- | --------------------------------------- |
| Rebuild image | `docker-compose build`                  |
| Tail logs     | `docker-compose logs -f`                |
| Stop all      | `docker-compose down`                   |
| Purge & clean | `docker system prune -f`                |
| Test API      | `curl http://localhost:8000/api/status` |

---

## 🐞 Troubleshooting

| Issue                         | Cause                       | Fix                                                          |
| ----------------------------- | --------------------------- | ------------------------------------------------------------ |
| Import errors in editor       | Wrong Python interpreter    | Select `backend/.venv` in VS Code                            |
| Frontend not showing via 8000 | Build missing               | Run `pnpm build` or rebuild Docker image                     |
| 404 on assets                 | `static/assets` not mounted | Ensure `dist` produced an `assets/` folder                   |
| Docker build slow             | Cold dependency install     | Leverage layer caching; avoid modifying lockfiles needlessly |
| Port in use                   | Another process on 8000     | `lsof -i :8000` then kill or change `PORT`                   |

---

## 🧩 Extending

Ideas:

- Add SPA history fallback for client-side routing
- Add gzip / brotli compression (Starlette middleware)
- Add authentication & JWT
- Set up GitHub Actions CI (build + push to ACR)
- Add OpenAPI tags & more endpoints

---

## 📜 License

Add license info here (MIT, Apache-2.0, etc.) if you intend to open source.

---

## 🙌 Contributing

1. Fork & branch (`feat/your-feature`)
2. Create a backend venv or use Docker
3. Run tests (when added)
4. Submit PR

---

Happy building! If you need automation for CI/CD or history fallback, open an issue or ask.
