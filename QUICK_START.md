# 🚀 Canvas Smith - Quick Start Guide

Convert sketches to Vue.js code with AI - Complete in 5 minutes!

## Prerequisites

- Docker & Docker Compose
- OR Python 3.11+ and Node.js 20+ for local development

---

## 🐳 Option 1: Docker (Recommended)

### 1. Set Up Environment

```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit backend/.env and add your Azure OpenAI credentials:
# AZURE_OPENAI_API_KEY=your_key_here
# AZURE_OPENAI_ENDPOINT=your_endpoint_here
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
```

### 2. Build & Run

```bash
# Build the image (includes frontend build)
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the App

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Stop

```bash
docker-compose down
```

---

## 💻 Option 2: Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Make sure .env is configured
python main.py  # Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev  # Runs on http://localhost:5173
```

---

## 🎨 How to Use

1. **Draw** something on the canvas
2. **Click** "Generate Code" button
3. **Wait** for AI to process (~5-10 seconds)
4. **View** generated Vue.js code
5. **Copy** or **Download** the component

---

## 🧪 Run Tests

### Frontend Tests

```bash
cd frontend
pnpm test          # Watch mode
pnpm test:run      # Single run
pnpm test:ui       # UI mode
```

### Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or change PORT in docker-compose.yml
```

### Frontend Not Showing

```bash
# Rebuild the Docker image
docker-compose build --no-cache
docker-compose up -d
```

### API Connection Failed

Check:
1. Backend is running: `curl http://localhost:8000/health`
2. CORS origins in backend config include your frontend URL
3. API key is valid in `.env`

---

## 📚 Project Structure

```
canvas-smith/
├── frontend/           # Vue 3 + Vite + Tailwind
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── services/     # API client
│   │   └── composables/  # Reusable logic
│   └── dist/           # Built files (after build)
├── backend/            # FastAPI + Azure OpenAI
│   ├── app/           # Application code
│   │   ├── api/       # API routes
│   │   ├── core/      # Config & settings
│   │   └── services/  # AI service
│   └── tests/         # Backend tests
└── Dockerfile         # Single-container build
```

---

## 🌐 Production Deployment

See [README.md](README.md) for Azure Container Apps deployment instructions.

---

## 📝 Environment Variables

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_API_KEY` | ✅ | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | ✅ | Model deployment name |
| `AI_MAX_TOKENS` | ❌ | Max tokens (default: 8000) |
| `CORS_ORIGINS` | ❌ | Allowed origins |

### Frontend (.env.development)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ❌ | Backend URL (default: http://localhost:8000) |

---

## ⚡ Features

- ✅ Draw with pen, shapes, text tools
- ✅ Real-time canvas with rulers
- ✅ AI-powered Vue component generation
- ✅ Copy to clipboard
- ✅ Download as .vue file
- ✅ Toast notifications
- ✅ Loading indicators
- ✅ Responsive design
- ✅ Production-ready Docker image

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

---

## 📄 License

See LICENSE file for details.

---

**Need help?** Open an issue on GitHub!
