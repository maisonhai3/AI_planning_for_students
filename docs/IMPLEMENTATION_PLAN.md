# 📋 Implementation Plan: Lập Kế Hoạch Học Tập Cho Sinh Viên

## Tổng quan dự án

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Student Study Planner |
| **Thời gian** | 4 tuần |
| **Tech Stack** | Next.js + Python (LangChain) + Firestore |
| **Team size đề xuất** | 1-2 developers |

---

## 🏗️ Kiến trúc thư mục

```
planing_for_students/
├── frontend/                    # Next.js Application
│   ├── src/
│   │   ├── app/                 # App Router (Next.js 14+)
│   │   │   ├── page.tsx         # Home - Input form
│   │   │   ├── plan/[id]/       # View saved plan
│   │   │   ├── api/             # API Routes (proxy to Python)
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── InputForm.tsx    # Syllabus/Todo input
│   │   │   ├── PlanViewer.tsx   # Iframe renderer
│   │   │   ├── LoadingState.tsx
│   │   │   └── ActionButtons.tsx # Save/Regenerate
│   │   ├── lib/
│   │   │   ├── firebase.ts      # Firestore client
│   │   │   └── api.ts           # API helpers
│   │   └── types/
│   │       └── plan.ts          # TypeScript interfaces
│   ├── public/
│   ├── next.config.js           # CSP headers config
│   ├── tailwind.config.js
│   └── package.json
│
├── backend/                     # Python LangChain Service
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routers/
│   │   │   └── planner.py       # /generate endpoint
│   │   ├── chains/
│   │   │   ├── router_chain.py  # Easy/Hard classifier
│   │   │   ├── planner_chain.py # Study plan generator
│   │   │   └── coder_chain.py   # HTML/Tailwind generator
│   │   ├── prompts/
│   │   │   ├── router.py
│   │   │   ├── planner.py
│   │   │   └── coder.py
│   │   ├── schemas/
│   │   │   └── plan.py          # Pydantic models
│   │   └── utils/
│   │       ├── langsmith.py     # Tracing setup
│   │       └── cache.py         # Context caching
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docs/
│   ├── IMPLEMENTATION_PLAN.md   # This file
│   ├── PROMPTS.md               # All prompt templates
│   ├── API_SPEC.md              # API documentation
│   └── EVALUATION.md            # F1 Score methodology
│
├── scripts/
│   ├── setup.sh                 # Dev environment setup
│   └── deploy.sh                # Deployment script
│
├── docker-compose.yml           # Local development
├── .gitignore
└── README.md
```

---

## 📅 Timeline Chi Tiết

### **TUẦN 1: MVP - Static Generation** 
> Mục tiêu: Input → AI → HTML hiển thị trong Iframe

#### Ngày 1-2: Project Setup
- [ ] Khởi tạo Next.js với TypeScript + Tailwind
- [ ] Khởi tạo Python project với FastAPI + LangChain
- [ ] Cấu hình Docker Compose cho local dev
- [ ] Setup `.env` files với API keys

#### Ngày 3-4: Core AI Logic
- [ ] Viết Planner Prompt (Gemini Flash)
- [ ] Viết Coder Prompt (HTML generator)
- [ ] Implement `/generate` API endpoint
- [ ] Test với hardcoded input

#### Ngày 5-7: Frontend Integration
- [ ] Tạo InputForm component
- [ ] Tạo PlanViewer (Iframe với srcDoc)
- [ ] Cấu hình CSP headers
- [ ] End-to-end test: Form → API → Iframe

**Deliverable Tuần 1:**
```
✅ Sinh viên nhập syllabus → Nhận được HTML calendar/plan
✅ Chưa lưu database, chưa có Router
```

---

### **TUẦN 2: Dynamic Storage**
> Mục tiêu: Lưu và xem lại plans

#### Ngày 1-2: Database Setup
- [ ] Tạo Firebase project
- [ ] Thiết kế Firestore schema
- [ ] Implement CRUD operations (Python)

#### Ngày 3-4: Save/Load Features
- [ ] Nút "Save Plan" → Lưu Firestore
- [ ] Trang `/plan/[id]` → Xem plan đã lưu
- [ ] Realtime update khi AI đang generate

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
- [ ] Viết Router Prompt (classifier)
- [ ] Implement RunnableBranch logic
- [ ] Test cases: Easy vs Hard inputs

#### Ngày 3-4: Multi-Model Integration
- [ ] Integrate GPT-4o cho Hard tasks
- [ ] Fallback mechanism nếu một model fail
- [ ] Cost tracking per request

#### Ngày 5-7: Optimization
- [ ] Context caching (Gemini)
- [ ] Response streaming
- [ ] Rate limiting

**Deliverable Tuần 3:**
```
✅ Requests đơn giản → Gemini Flash (rẻ, nhanh)
✅ Requests phức tạp → GPT-4o (chính xác)
✅ Streaming response cho UX tốt hơn
```

---

### **TUẦN 4: Quality & Observability**
> Mục tiêu: Logging, Evaluation, Production-ready

#### Ngày 1-2: LangSmith Integration
- [ ] Setup LangSmith tracing
- [ ] Log tất cả chain executions
- [ ] Dashboard visualization

#### Ngày 3-4: Evaluation Framework
- [ ] Implement "Save" tracking (positive signal)
- [ ] Implement "Regenerate" tracking (negative signal)
- [ ] F1 Score calculator
- [ ] LLM-as-a-Judge setup (5% sampling)

#### Ngày 5-7: Production Prep
- [ ] Vercel deployment (Frontend)
- [ ] Cloud Run/Railway deployment (Backend)
- [ ] Environment variables setup
- [ ] Monitoring & alerts

**Deliverable Tuần 4:**
```
✅ Full observability với LangSmith
✅ Tự động đánh giá chất lượng
✅ Production deployment
```

---

## 🔧 Chi Tiết Kỹ Thuật

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Generate study plan |
| GET | `/api/plans/{id}` | Get saved plan |
| POST | `/api/plans` | Save new plan |
| PUT | `/api/plans/{id}` | Update plan |
| POST | `/api/feedback` | Log user action (save/regenerate) |

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
    model_used: "gemini-flash" | "gpt-4o"
  },
  metadata: {
    created_at: Timestamp,
    updated_at: Timestamp,
    regenerate_count: 0,
    is_saved: false,
    router_decision: "easy" | "hard"
  }
}

// Collection: feedback
{
  plan_id: "reference",
  action: "save" | "regenerate" | "share",
  timestamp: Timestamp
}
```

### Environment Variables

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_CONFIG={}

# Backend (.env)
GOOGLE_API_KEY=           # Gemini
OPENAI_API_KEY=           # GPT-4o
LANGSMITH_API_KEY=        # Tracing
LANGSMITH_PROJECT=student-planner
FIREBASE_CREDENTIALS=     # Service account JSON
REDIS_URL=                # Optional: caching
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
| Gemini API downtime | Medium | Fallback to GPT-4o |
| Slow response time | Medium | Streaming + loading UX |

---

## 📝 Checklist Trước Khi Bắt Đầu

### Cần từ Product Owner
- [ ] Sample syllabus/input examples (3-5 cases)
- [ ] Định nghĩa "kế hoạch tốt" để training Judge
- [ ] Budget limit cho API calls

### Cần từ DevOps/Infra
- [ ] Firebase project created
- [ ] Vercel team/project setup
- [ ] Domain name (nếu cần)

### Cần từ Developer
- [ ] Gemini API key (Google AI Studio)
- [ ] OpenAI API key
- [ ] LangSmith account

---

## 🚀 Bắt Đầu Ngay

Sau khi có đủ API keys, chạy:

```bash
# Clone và setup
cd /home/maihai/Projects/planing_for_students
./scripts/setup.sh

# Start development
docker-compose up -d
```

---

*Document version: 1.0*  
*Last updated: 2026-01-18*
