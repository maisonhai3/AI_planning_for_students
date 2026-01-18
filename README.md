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

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI    │────▶│  Gemini/    │
│  Frontend   │◀────│  + LangChain │◀────│   GPT-4o    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌──────────────┐
│   Iframe    │     │  Firestore   │
│   Render    │     │  + LangSmith │
└─────────────┘     └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- Docker (optional)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd planing_for_students

# Run setup script
./scripts/setup.sh

# Fill in API keys
# - backend/.env
# - frontend/.env.local
```

### Development

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Open http://localhost:3000
```

### With Docker

```bash
docker-compose up
```

## 📁 Project Structure

```
planing_for_students/
├── frontend/          # Next.js + Tailwind
│   ├── src/app/       # App Router
│   └── src/components/
├── backend/           # FastAPI + LangChain
│   ├── app/chains/    # Router, Planner, Coder
│   └── app/prompts/   # Prompt templates
├── docs/              # Documentation
│   ├── IMPLEMENTATION_PLAN.md
│   ├── PROMPTS.md
│   ├── API_SPEC.md
│   └── EVALUATION.md
└── scripts/           # Setup & deploy scripts
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) | Timeline và chi tiết kỹ thuật |
| [Prompts](docs/PROMPTS.md) | Tất cả prompt templates |
| [API Spec](docs/API_SPEC.md) | REST API documentation |
| [Evaluation](docs/EVALUATION.md) | F1 Score methodology |

## 🔑 Environment Variables

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Gemini API key |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `LANGSMITH_API_KEY` | ⚪ | LangSmith tracing |
| `FIREBASE_PROJECT_ID` | ✅ | Firebase project |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend URL |
| `NEXT_PUBLIC_FIREBASE_*` | ✅ | Firebase config |

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, React, Tailwind CSS, TypeScript
- **Backend**: FastAPI, LangChain, Python 3.10+
- **AI Models**: Gemini 1.5 Flash, GPT-4o
- **Database**: Firebase Firestore
- **Observability**: LangSmith
- **Hosting**: Vercel (Frontend), Cloud Run (Backend)

## 📊 Metrics

Target metrics sau 4 tuần:

| Metric | Target |
|--------|--------|
| F1 Score | > 0.7 |
| Response Time (P95) | < 10s |
| Cost per request | < $0.05 |

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
