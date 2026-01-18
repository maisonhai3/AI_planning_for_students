# 📋 Implementation Plan: Lập Kế Hoạch Học Tập Cho Sinh Viên

## Tổng quan dự án

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Student Study Planner |
| **Thời gian** | 4 tuần |
| **Tech Stack** | Next.js (pnpm) + Django REST + LangChain + Firestore |
| **Architecture** | Monorepo với shared configs |
| **Team size đề xuất** | 1-2 developers |

---

## 🏗️ Kiến trúc Monorepo

```
planing_for_students/
├── apps/
│   ├── web/                         # Next.js Frontend (pnpm)
│   │   ├── src/
│   │   │   ├── app/                 # App Router (Next.js 14+)
│   │   │   │   ├── page.tsx         # Home - Input form
│   │   │   │   ├── plan/[id]/       # View saved plan
│   │   │   │   └── layout.tsx
│   │   │   ├── components/
│   │   │   │   ├── InputForm.tsx    # Syllabus/Todo input
│   │   │   │   ├── PlanViewer.tsx   # Iframe renderer
│   │   │   │   ├── LoadingState.tsx
│   │   │   │   └── ActionButtons.tsx
│   │   │   ├── lib/
│   │   │   │   ├── firebase.ts      # Firestore client
│   │   │   │   └── api.ts           # API helpers
│   │   │   └── types/
│   │   │       └── plan.ts          # TypeScript interfaces
│   │   ├── public/
│   │   ├── next.config.js           # CSP headers config
│   │   ├── tailwind.config.js
│   │   └── package.json
│   │
│   └── api/                         # Django REST Backend (uv)
│       ├── manage.py
│       ├── pyproject.toml           # uv project config
│       ├── uv.lock
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings/
│       │   │   ├── base.py
│       │   │   ├── development.py
│       │   │   └── production.py
│       │   ├── urls.py
│       │   └── wsgi.py
│       ├── apps/
│       │   ├── planner/             # Main planner app
│       │   │   ├── views.py         # API views
│       │   │   ├── serializers.py   # DRF serializers
│       │   │   ├── urls.py
│       │   │   └── services/
│       │   │       ├── router.py    # LangChain Router
│       │   │       ├── planner.py   # Plan generator
│       │   │       └── coder.py     # HTML generator
│       │   └── feedback/            # Tracking app
│       │       ├── views.py
│       │       ├── models.py
│       │       └── serializers.py
│       ├── core/
│       │   ├── langchain/
│       │   │   ├── chains.py        # Chain definitions
│       │   │   └── prompts.py       # Prompt hub integration
│       │   ├── langsmith/
│       │   │   ├── client.py        # LangSmith client
│       │   │   └── versioning.py    # Prompt versioning
│       │   └── firebase/
│       │       └── client.py        # Firestore client
│       ├── tests/
│       └── Dockerfile
│
├── packages/                        # Shared packages
│   └── shared-types/                # Shared TypeScript types
│       ├── package.json
│       └── src/
│           └── plan.ts
│
├── docs/
│   ├── IMPLEMENTATION_PLAN.md       # This file
│   ├── PROMPTS.md                   # Prompt templates (synced to LangSmith)
│   ├── API_SPEC.md                  # API documentation
│   └── EVALUATION.md                # F1 Score methodology
│
├── scripts/
│   ├── setup.sh                     # Dev environment setup
│   └── deploy.sh                    # Deployment script
│
├── pnpm-workspace.yaml              # pnpm workspace config
├── turbo.json                       # Turborepo config (optional)
├── docker-compose.yml               # Local development
├── .gitignore
└── README.md
```

---

## 🔧 Công cụ & Package Manager

### Frontend (pnpm)
```bash
# pnpm - Fast, disk-efficient package manager
pnpm create next-app apps/web --typescript --tailwind --app

# Workspace setup
pnpm-workspace.yaml:
  packages:
    - 'apps/*'
    - 'packages/*'
```

### Backend (uv)
```bash
# uv - Extremely fast Python package manager (by Astral)
cd apps/api
uv init
uv add django djangorestframework
uv add langchain langchain-google-genai langchain-openai
uv add langsmith firebase-admin
uv add python-dotenv httpx

# Run with uv
uv run python manage.py runserver
```

---

## 📅 Timeline Chi Tiết

### **TUẦN 1: MVP - Static Generation** 
> Mục tiêu: Input → AI → HTML hiển thị trong Iframe

#### Ngày 1-2: Project Setup
- [ ] Khởi tạo Monorepo với pnpm workspace
- [ ] Khởi tạo Next.js (apps/web) với TypeScript + Tailwind
- [ ] Khởi tạo Django project (apps/api) với uv
- [ ] Setup Django REST Framework
- [ ] Cấu hình Docker Compose cho local dev
- [ ] Setup `.env` files với API keys
- [ ] **Setup LangSmith Hub cho Prompt Versioning**

#### Ngày 3-4: Core AI Logic
- [ ] Push Planner Prompt lên LangSmith Hub
- [ ] Push Coder Prompt lên LangSmith Hub
- [ ] Implement Django `/api/generate` endpoint
- [ ] Test với hardcoded input

#### Ngày 5-7: Frontend Integration
- [ ] Tạo InputForm component
- [ ] Tạo PlanViewer (Iframe với srcDoc)
- [ ] Cấu hình CSP headers
- [ ] End-to-end test: Form → API → Iframe

**Deliverable Tuần 1:**
```
✅ Sinh viên nhập syllabus → Nhận được HTML calendar/plan
✅ Prompts được version control trên LangSmith Hub
✅ Chưa lưu database, chưa có Router
```

---

### **TUẦN 2: Dynamic Storage**
> Mục tiêu: Lưu và xem lại plans

#### Ngày 1-2: Database Setup
- [ ] Tạo Firebase project
- [ ] Thiết kế Firestore schema
- [ ] Implement Django service layer cho Firestore

#### Ngày 3-4: Save/Load Features
- [ ] Nút "Save Plan" → Lưu Firestore
- [ ] Trang `/plan/[id]` → Xem plan đã lưu
- [ ] Django Channels cho Realtime (optional)

#### Ngày 5-7: User Experience
- [ ] Loading states & animations
- [ ] Error handling & retry
- [ ] "Regenerate" button
- [ ] Share link functionality

**Deliverable Tuần 2:**
```
✅ Plans được lưu trữ persistent
✅ Có thể share link cho bạn bè
✅ Regenerate nếu không hài lòng
```

---

### **TUẦN 3: Intelligence Layer**
> Mục tiêu: Router phân loại + Multi-model

#### Ngày 1-2: Router Chain
- [ ] Push Router Prompt lên LangSmith Hub
- [ ] Implement RunnableBranch logic
- [ ] Test cases: Easy vs Hard inputs

#### Ngày 3-4: Multi-Model Integration
- [ ] Integrate Gemini 2.5 Pro cho Hard tasks
- [ ] Fallback mechanism nếu một model fail
- [ ] Cost tracking per request

#### Ngày 5-7: Optimization
- [ ] Context caching (Gemini)
- [ ] Django async views cho streaming
- [ ] Rate limiting với Django middleware

**Deliverable Tuần 3:**
```
✅ Requests đơn giản → Gemini 2.5 Flash (rẻ, nhanh)
✅ Requests phức tạp → Gemini 2.5 Pro (chính xác)
✅ Streaming response cho UX tốt hơn
```

---

### **TUẦN 4: Quality & Observability**
> Mục tiêu: Logging, Evaluation, Production-ready

#### Ngày 1-2: LangSmith Integration
- [ ] Full tracing cho tất cả chains
- [ ] Prompt A/B testing với LangSmith Hub
- [ ] Dashboard visualization

#### Ngày 3-4: Evaluation Framework
- [ ] Implement "Save" tracking (positive signal)
- [ ] Implement "Regenerate" tracking (negative signal)
- [ ] F1 Score calculator
- [ ] LLM-as-a-Judge setup (5% sampling)

#### Ngày 5-7: Production Prep
- [ ] Vercel deployment (Frontend)
- [ ] Cloud Run/Railway deployment (Django)
- [ ] Environment variables setup
- [ ] Monitoring & alerts

**Deliverable Tuần 4:**
```
✅ Full observability với LangSmith
✅ Prompt versioning & A/B testing
✅ Tự động đánh giá chất lượng
✅ Production deployment
```

---

## 🔧 Chi Tiết Kỹ Thuật

### Django Project Structure

```python
# apps/api/config/settings/base.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'corsheaders',
    'apps.planner',
    'apps.feedback',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
```

### API Endpoints (Django REST)

| Method | Endpoint | View | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/generate/` | `GeneratePlanView` | Generate study plan |
| GET | `/api/v1/plans/{id}/` | `PlanDetailView` | Get saved plan |
| POST | `/api/v1/plans/` | `PlanCreateView` | Save new plan |
| PUT | `/api/v1/plans/{id}/` | `PlanUpdateView` | Update plan |
| POST | `/api/v1/feedback/` | `FeedbackView` | Log user action |

### LangSmith Prompt Versioning

```python
# core/langsmith/versioning.py
from langsmith import Client
from langchain import hub

client = Client()

class PromptManager:
    """
    Quản lý prompt versions trên LangSmith Hub
    """
    
    PROMPT_REPO = "maisonhai3/student-planner"
    
    @classmethod
    def get_prompt(cls, name: str, version: str = "latest"):
        """
        Pull prompt từ LangSmith Hub
        
        Args:
            name: router | planner | coder | judge
            version: specific version hoặc "latest"
        """
        prompt_name = f"{cls.PROMPT_REPO}/{name}"
        if version != "latest":
            prompt_name = f"{prompt_name}:{version}"
        return hub.pull(prompt_name)
    
    @classmethod
    def push_prompt(cls, name: str, prompt, description: str = ""):
        """
        Push prompt mới lên LangSmith Hub
        """
        hub.push(
            f"{cls.PROMPT_REPO}/{name}",
            prompt,
            description=description
        )
    
    @classmethod
    def list_versions(cls, name: str):
        """
        List tất cả versions của một prompt
        """
        return client.list_prompts(
            prompt_name=f"{cls.PROMPT_REPO}/{name}"
        )
```

### Firestore Schema

```javascript
// Collection: plans
{
  id: "auto-generated",
  userId: "anonymous-session-id",
  input: {
    syllabus: "string",
    todos: ["string"],
    preferences: {}
  },
  output: {
    json_plan: {},      // Structured data
    html_content: "",   // Generated HTML
    model_used: "gemini-2.5-flash" | "gemini-2.5-pro"
  },
  metadata: {
    created_at: Timestamp,
    updated_at: Timestamp,
    regenerate_count: 0,
    is_saved: false,
    router_decision: "easy" | "hard",
    prompt_versions: {
      router: "v1.2",
      planner: "v2.0",
      coder: "v1.5"
    }
  }
}

// Collection: feedback
{
  plan_id: "reference",
  action: "save" | "regenerate" | "share",
  timestamp: Timestamp,
  prompt_versions: {}  // Track which prompt version was used
}
```

### Environment Variables

```bash
# apps/web/.env.local (Frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=

# apps/api/.env (Backend)
# Django
DJANGO_SECRET_KEY=
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# AI Models (Gemini only - no OpenAI needed)
GOOGLE_API_KEY=           # Gemini 2.5 Flash & Pro

# LangSmith (Tracing + Prompt Versioning)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=student-planner
LANGSMITH_API_KEY=
LANGSMITH_HUB_REPO=maisonhai3/student-planner

# Firebase
FIREBASE_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=./firebase-credentials.json

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

---

## 📊 Success Metrics

### Tuần 1-2 (Functionality)
- [ ] Response time < 10s cho 90% requests
- [ ] Zero critical bugs trong demo

### Tuần 3-4 (Quality)
- [ ] Router accuracy > 85%
- [ ] F1 Score > 0.7 (dựa trên Save/Regenerate ratio)
- [ ] Cost per request < $0.05
- [ ] Prompt iteration cycle < 5 minutes (thanks to LangSmith Hub)

### Post-Launch
- [ ] User retention (return within 7 days) > 30%
- [ ] NPS Score > 50

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI generates invalid HTML | High | Structured output + validation |
| XSS through Iframe | Critical | Strict CSP + sandbox |
| API costs exceed budget | Medium | Rate limiting + caching |
| Gemini API downtime | Medium | Retry logic + user notification |
| Slow response time | Medium | Django async + streaming |
| Prompt regression | Medium | LangSmith versioning + A/B test |

---

## 📝 Checklist Trước Khi Bắt Đầu

### Cần từ Product Owner
- [ ] Sample syllabus/input examples (3-5 cases)
- [ ] Định nghĩa "kế hoạch tốt" để training Judge
- [ ] Budget limit cho API calls

### Cần từ DevOps/Infra
- [ ] Firebase project created
- [ ] Vercel team/project setup
- [ ] LangSmith organization setup
- [ ] Domain name (nếu cần)

### Cần từ Developer
- [ ] Gemini API key (Google AI Studio) - for 2.5 Flash & Pro
- [ ] LangSmith account + Hub access (Free tier)

---

## 🚀 Bắt Đầu Ngay

Sau khi có đủ API keys, chạy:

```bash
# Clone và setup
cd /home/maihai/Projects/planing_for_students
./scripts/setup.sh

# Start development
docker-compose up -d

# Hoặc chạy riêng
# Terminal 1 - Backend
cd apps/api && uv run python manage.py runserver

# Terminal 2 - Frontend
cd apps/web && pnpm dev
```

---

## 🔄 LangSmith Prompt Workflow

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

---

*Document version: 2.0*  
*Last updated: 2026-01-18*  
*Changes: Migrated to Monorepo, pnpm, uv, Django REST, LangSmith Prompt Versioning*
