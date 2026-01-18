# Student Study Planner 📚

> AI-powered study planning system for Vietnamese university students

## 🎯 Overview

Hệ thống giúp sinh viên tự động tạo kế hoạch học tập từ syllabus và to-do list, sử dụng AI (Gemini Flash + GPT-4o) với Router thông minh để tối ưu chi phí và chất lượng.

## ✨ Features

- 📝 **Input linh hoạt**: Nhập syllabus, to-do list, hoặc mô tả tự do
- 🤖 **AI Router**: Tự động chọn model phù hợp (Flash cho đơn giản, GPT-4o cho phức tạp)
- 🎨 **Generative UI**: AI tự tạo giao diện HTML/Tailwind đẹp mắt
- 💾 **Lưu & Chia sẻ**: Lưu kế hoạch và chia sẻ với bạn bè
- 📊 **Tự đánh giá**: Hệ thống tự tính F1 Score để cải thiện liên tục
- 🔄 **Prompt Versioning**: Quản lý prompts trên LangSmith Hub

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MONOREPO                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐          ┌──────────────┐                  │
│  │  apps/web   │ ──────▶  │  apps/api    │                  │
│  │  (Next.js)  │ ◀──────  │  (Django)    │                  │
│  │   [pnpm]    │          │    [uv]      │                  │
│  └─────────────┘          └──────────────┘                  │
│        │                         │                           │
│        ▼                         ▼                           │
│  ┌─────────────┐          ┌──────────────┐                  │
│  │   Iframe    │          │  LangChain   │                  │
│  │   Render    │          │  + LangSmith │                  │
│  └─────────────┘          └──────────────┘                  │
│                                  │                           │
│                    ┌─────────────┼─────────────┐            │
│                    ▼             ▼             ▼            │
│              ┌─────────┐  ┌──────────┐  ┌─────────┐        │
│              │ Gemini  │  │  GPT-4o  │  │Firestore│        │
│              │  Flash  │  │          │  │         │        │
│              └─────────┘  └──────────┘  └─────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18
- pnpm >= 8
- Python >= 3.11
- uv (Astral)
- Docker (optional)

### Setup

```bash
# Clone the repository
git clone https://github.com/maisonhai3/AI_planning_for_students.git
cd AI_planning_for_students

# Run setup script
./scripts/setup.sh

# Fill in API keys
# - apps/api/.env
# - apps/web/.env.local
```

### Development

```bash
# Terminal 1 - Backend (Django)
cd apps/api
uv run python manage.py runserver

# Terminal 2 - Frontend (Next.js)
cd apps/web
pnpm dev

# Or start both with:
pnpm dev

# Open http://localhost:3000
```

### With Docker

```bash
docker-compose up
```

## 📁 Project Structure

```
planing_for_students/
├── apps/
│   ├── web/                 # Next.js + Tailwind (pnpm)
│   │   ├── src/app/         # App Router
│   │   └── src/components/
│   └── api/                 # Django REST + LangChain (uv)
│       ├── apps/planner/    # Main planner app
│       ├── apps/feedback/   # Feedback tracking
│       └── core/langsmith/  # Prompt versioning
├── packages/                # Shared packages
├── docs/                    # Documentation
│   ├── IMPLEMENTATION_PLAN.md
│   ├── PROMPTS.md
│   ├── API_SPEC.md
│   └── EVALUATION.md
└── scripts/                 # Setup & deploy scripts
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) | Timeline và chi tiết kỹ thuật |
| [Prompts](docs/PROMPTS.md) | Prompt templates + LangSmith Hub integration |
| [API Spec](docs/API_SPEC.md) | Django REST API documentation |
| [Evaluation](docs/EVALUATION.md) | F1 Score methodology |

## 🔑 Environment Variables

### Backend (apps/api/.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Gemini API key |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `LANGSMITH_API_KEY` | ⚪ | LangSmith tracing + Hub |
| `FIREBASE_PROJECT_ID` | ✅ | Firebase project |
| `DJANGO_SECRET_KEY` | ✅ | Django secret |

### Frontend (apps/web/.env.local)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend URL |
| `NEXT_PUBLIC_FIREBASE_*` | ✅ | Firebase config |

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Package Manager**: pnpm
- **Styling**: Tailwind CSS
- **Language**: TypeScript

### Backend
- **Framework**: Django 5 + Django REST Framework
- **Package Manager**: uv (Astral)
- **AI Orchestration**: LangChain
- **Models**: Gemini 1.5 Flash, GPT-4o
- **Observability**: LangSmith (Tracing + Prompt Hub)

### Infrastructure
- **Database**: Firebase Firestore
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Cloud Run / Railway
- **Prompt Management**: LangSmith Hub

## 📊 Metrics

Target metrics sau 4 tuần:

| Metric | Target |
|--------|--------|
| F1 Score | > 0.7 |
| Response Time (P95) | < 10s |
| Cost per request | < $0.05 |
| Prompt iteration cycle | < 5 min |

## 🔄 Prompt Versioning Workflow

```
1. Edit prompt locally (docs/PROMPTS.md)
           ↓
2. Test locally với sample inputs
           ↓
3. Push to LangSmith Hub (versioned)
           ↓
4. A/B test in production (5% traffic)
           ↓
5. Monitor metrics (F1 Score per version)
           ↓
6. Promote winning version to 100%
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Made with ❤️ for Vietnamese students

**Tech Stack**: Monorepo • pnpm • uv • Django REST • LangChain • LangSmith Hub
