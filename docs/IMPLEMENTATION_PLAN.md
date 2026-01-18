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
│       │   │   ├── guards/          # Security guards
│       │   │   │   ├── input_guard.py   # Regex + Safety Settings
│       │   │   │   └── output_guard.py  # Pydantic + AutoFix
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
- [ ] **Implement Input Guard (Regex + Safety Settings)**
- [ ] **Implement Output Guard (Pydantic + AutoFixParser)**
- [ ] Implement Django `/api/generate` endpoint với Guards
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
✅ Input Guard chặn prompt injection + dangerous patterns
✅ Output Guard đảm bảo JSON hợp lệ (auto-fix nếu lỗi)
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

## 🔒 Security Layer (Giải pháp Lai)

> Cân bằng giữa bảo mật và tốc độ phát triển

### Bước 1: Input Guard (Chặn đầu vào)

```python
# apps/planner/guards/input_guard.py
import re
from typing import Tuple, List
from langchain_google_genai import ChatGoogleGenerativeAI

# Google GenAI SDK - Safety Settings
# Docs: https://ai.google.dev/gemini-api/docs/safety-settings
from google.genai import types

class InputGuard:
    """
    Bảo vệ đầu vào với 2 lớp:
    1. Regex/Keyword blacklist (nhanh)
    2. Gemini Safety Settings (sâu)
    
    Reference: https://ai.google.dev/gemini-api/docs/safety-settings
    """
    
    # ============================================
    # Gemini Safety Categories & Thresholds
    # ============================================
    # 
    # Categories:
    #   - HARM_CATEGORY_HARASSMENT: Negative/harmful comments targeting identity
    #   - HARM_CATEGORY_HATE_SPEECH: Rude, disrespectful, or profane content
    #   - HARM_CATEGORY_SEXUALLY_EXPLICIT: Sexual acts or lewd content
    #   - HARM_CATEGORY_DANGEROUS_CONTENT: Promotes harmful acts
    #
    # Thresholds:
    #   - OFF / BLOCK_NONE: Always show (không filter)
    #   - BLOCK_ONLY_HIGH: Block khi xác suất cao
    #   - BLOCK_MEDIUM_AND_ABOVE: Block khi xác suất trung bình trở lên
    #   - BLOCK_LOW_AND_ABOVE: Block khi xác suất thấp trở lên (strict nhất)
    #
    # Note: Default threshold cho Gemini 2.5/3 là OFF
    # ============================================
    
    # Blacklist patterns - Injection attacks
    DANGEROUS_PATTERNS = [
        # SQL Injection
        r"(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\s+",
        r"(?i)(--)|(;)|(\/\*)",
        
        # Prompt Injection
        r"(?i)ignore\s+(previous|all|above)\s+instructions?",
        r"(?i)disregard\s+(previous|all|above)",
        r"(?i)forget\s+(everything|all|previous)",
        r"(?i)you\s+are\s+now\s+a",
        r"(?i)new\s+instructions?:",
        r"(?i)system\s*prompt:",
        r"(?i)act\s+as\s+(if|a)",
        
        # Code injection
        r"(?i)<script[^>]*>",
        r"(?i)javascript:",
        r"(?i)on\w+\s*=",
        
        # Path traversal
        r"\.\./",
        r"(?i)\/etc\/passwd",
    ]
    
    # Suspicious keywords (log but don't block)
    SUSPICIOUS_KEYWORDS = [
        "password", "secret", "api_key", "token",
        "admin", "root", "sudo", "hack",
    ]
    
    @classmethod
    def get_safety_settings(cls) -> List[types.SafetySetting]:
        """
        Tạo Safety Settings cho Gemini API
        
        Sử dụng BLOCK_MEDIUM_AND_ABOVE cho cân bằng giữa:
        - Không quá strict (block false positive)
        - Đủ an toàn cho educational content
        
        Reference: https://ai.google.dev/gemini-api/docs/safety-settings
        """
        return [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
    
    @classmethod
    def check_input(cls, text: str) -> Tuple[bool, str]:
        """
        Kiểm tra input an toàn
        
        Returns:
            (is_safe, reason)
        """
        # 1. Check dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text):
                return False, f"Blocked: Suspicious pattern detected"
        
        # 2. Check length (prevent token bombing)
        if len(text) > 10000:
            return False, "Input too long (max 10000 characters)"
        
        # 3. Log suspicious (but allow)
        for keyword in cls.SUSPICIOUS_KEYWORDS:
            if keyword.lower() in text.lower():
                # Log to monitoring
                print(f"[WARN] Suspicious keyword in input: {keyword}")
        
        return True, "OK"
    
    @classmethod
    def get_safe_llm(cls, model: str = "gemini-2.5-flash"):
        """
        Tạo LangChain LLM instance với Safety Settings
        
        LangChain sẽ tự động convert safety_settings sang format phù hợp
        """
        # Chuyển đổi sang format dictionary cho LangChain
        safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.7,
            safety_settings=safety_settings,
        )
    
    @classmethod
    def get_safe_genai_client(cls, model: str = "gemini-2.5-flash"):
        """
        Tạo Google GenAI Client trực tiếp (không qua LangChain)
        Sử dụng khi cần control nhiều hơn
        
        Reference: https://ai.google.dev/gemini-api/docs/safety-settings
        """
        from google import genai
        
        client = genai.Client()
        
        # Config với safety settings
        config = types.GenerateContentConfig(
            safety_settings=cls.get_safety_settings(),
            temperature=0.7,
        )
        
        return client, model, config


# ============================================
# Example: Direct Google GenAI Usage
# ============================================
def generate_with_safety(prompt: str) -> str:
    """
    Ví dụ sử dụng trực tiếp Google GenAI SDK với Safety Settings
    """
    from google import genai
    
    client = genai.Client()
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
            ]
        )
    )
    
    # Check nếu bị block bởi safety filter
    if response.candidates and response.candidates[0].finish_reason == "SAFETY":
        raise ValueError("Content blocked by Gemini Safety Filter")
    
    return response.text
```

### Bước 2: Output Guard (Đảm bảo JSON hợp lệ)

```python
# apps/planner/guards/output_guard.py
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from langchain_google_genai import ChatGoogleGenerativeAI

# ============================================
# Pydantic Models cho Structured Output
# ============================================

class StudySession(BaseModel):
    """Một buổi học trong ngày"""
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    subject: str = Field(..., min_length=1, max_length=100)
    task: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., pattern=r"^(study|review|practice|break)$")
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('end_time')
    def end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class DailySchedule(BaseModel):
    """Lịch học trong một ngày"""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    day_of_week: str
    sessions: List[StudySession]

class Milestone(BaseModel):
    """Mốc quan trọng"""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=500)

class Subject(BaseModel):
    """Môn học"""
    name: str = Field(..., min_length=1, max_length=100)
    priority: str = Field(..., pattern=r"^(high|medium|low)$")
    total_hours: float = Field(..., gt=0, le=100)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")

class StudyPlan(BaseModel):
    """Kế hoạch học tập hoàn chỉnh"""
    title: str = Field(..., min_length=1, max_length=200)
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    subjects: List[Subject]
    schedule: List[DailySchedule]
    milestones: List[Milestone]
    tips: List[str] = Field(..., max_items=10)
    
    @validator('end_date')
    def end_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


# ============================================
# Output Guard với AutoFix
# ============================================

class OutputGuard:
    """
    Đảm bảo output từ LLM là JSON hợp lệ
    Sử dụng LangChain AutoFixParser nếu lỗi
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,  # Deterministic for fixing
        )
        
        # Parser chính
        self.parser = PydanticOutputParser(pydantic_object=StudyPlan)
        
        # Auto-fix parser (gọi LLM lần 2 nếu lỗi)
        self.fixing_parser = OutputFixingParser.from_llm(
            parser=self.parser,
            llm=self.llm,
            max_retries=2,  # Tối đa 2 lần retry
        )
    
    def parse(self, output: str) -> StudyPlan:
        """
        Parse output với auto-fix
        
        Flow:
        1. Thử parse trực tiếp
        2. Nếu lỗi → AutoFixParser gọi LLM sửa
        3. Nếu vẫn lỗi → Raise exception
        """
        try:
            # Thử parse trực tiếp
            return self.parser.parse(output)
        except Exception as first_error:
            print(f"[WARN] First parse failed: {first_error}")
            
            try:
                # Auto-fix: LLM sẽ được gọi với message:
                # "Fix the following JSON to match the schema..."
                return self.fixing_parser.parse(output)
            except Exception as second_error:
                print(f"[ERROR] Auto-fix also failed: {second_error}")
                raise ValueError(
                    f"Cannot parse LLM output after 2 retries. "
                    f"Original error: {first_error}"
                )
    
    def get_format_instructions(self) -> str:
        """
        Trả về format instructions để inject vào prompt
        """
        return self.parser.get_format_instructions()


# ============================================
# Usage trong Chain
# ============================================

def create_safe_planner_chain():
    """
    Tạo chain với Input + Output Guards
    """
    from langchain_core.runnables import RunnableLambda
    
    input_guard = InputGuard()
    output_guard = OutputGuard()
    
    def validate_input(data: dict) -> dict:
        is_safe, reason = input_guard.check_input(data.get("user_input", ""))
        if not is_safe:
            raise ValueError(f"Input blocked: {reason}")
        return data
    
    def parse_output(output: str) -> dict:
        plan = output_guard.parse(output)
        return plan.model_dump()
    
    # Get prompt từ LangSmith Hub
    from core.langsmith.versioning import PromptManager
    planner_prompt = PromptManager.get_prompt("planner")
    
    # Inject format instructions vào prompt
    planner_prompt = planner_prompt.partial(
        format_instructions=output_guard.get_format_instructions()
    )
    
    llm = input_guard.get_safe_llm("gemini-2.5-flash")
    
    chain = (
        RunnableLambda(validate_input)  # Input Guard
        | planner_prompt
        | llm
        | RunnableLambda(parse_output)  # Output Guard
    )
    
    return chain
```

### Django View với Guards

```python
# apps/planner/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .guards.input_guard import InputGuard
from .guards.output_guard import OutputGuard, create_safe_planner_chain

class GeneratePlanView(APIView):
    """
    POST /api/v1/generate/
    Generate study plan với security guards
    
    Handles:
    - Input validation (regex + length)
    - Gemini Safety Filter blocks
    - Output JSON parsing errors
    """
    
    def post(self, request):
        user_input = request.data.get("input", "")
        
        # 1. Input Guard (fast fail)
        is_safe, reason = InputGuard.check_input(user_input)
        if not is_safe:
            return Response(
                {"error": reason, "code": "INPUT_BLOCKED"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 2. Run chain với embedded guards
            chain = create_safe_planner_chain()
            result = chain.invoke({"user_input": user_input})
            
            return Response({
                "success": True,
                "plan": result,
            })
            
        except ValueError as e:
            error_msg = str(e)
            
            # Check if blocked by Gemini Safety Filter
            if "safety" in error_msg.lower() or "blocked" in error_msg.lower():
                return Response(
                    {
                        "error": "Nội dung không phù hợp. Vui lòng thử lại với input khác.",
                        "code": "SAFETY_BLOCKED",
                        "detail": "Content blocked by Gemini Safety Filter"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Output parsing failed after retries
            return Response(
                {"error": str(e), "code": "GENERATION_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            # Gemini safety filter triggered hoặc API error
            return Response(
                {"error": "Generation failed. Please try again.",
                 "code": "API_ERROR"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
```

### Security Checklist

| Layer | Giải pháp | Thời điểm |
|-------|-----------|-----------|
| **Input Guard** | Regex blacklist (Prompt Injection, SQL, XSS) | Request nhận được |
| **Gemini Safety** | `BLOCK_MEDIUM_AND_ABOVE` cho 4 categories | LLM call |
| **Output Guard** | Pydantic + AutoFixParser | Sau khi LLM trả về |
| **Frontend CSP** | Strict Content-Security-Policy | Render Iframe |
| **Rate Limiting** | Django middleware | Mọi request |

### Gemini Safety Settings Reference

```python
# Categories được filter (https://ai.google.dev/gemini-api/docs/safety-settings)
# ┌─────────────────────────────────┬─────────────────────────────────────────────┐
# │ Category                        │ Description                                  │
# ├─────────────────────────────────┼─────────────────────────────────────────────┤
# │ HARM_CATEGORY_HARASSMENT        │ Negative/harmful comments targeting identity │
# │ HARM_CATEGORY_HATE_SPEECH       │ Rude, disrespectful, or profane content      │
# │ HARM_CATEGORY_SEXUALLY_EXPLICIT │ Sexual acts or lewd content                  │
# │ HARM_CATEGORY_DANGEROUS_CONTENT │ Promotes harmful acts                        │
# └─────────────────────────────────┴─────────────────────────────────────────────┘

# Thresholds (từ strict nhất đến lỏng nhất)
# ┌────────────────────────┬─────────────────────────────────────────────────────┐
# │ Threshold              │ Blocks when probability is...                       │
# ├────────────────────────┼─────────────────────────────────────────────────────┤
# │ BLOCK_LOW_AND_ABOVE    │ Low, Medium, or High (strict nhất)                 │
# │ BLOCK_MEDIUM_AND_ABOVE │ Medium or High (recommended cho educational apps)  │
# │ BLOCK_ONLY_HIGH        │ High only                                          │
# │ BLOCK_NONE / OFF       │ Never block (default cho Gemini 2.5/3)             │
# └────────────────────────┴─────────────────────────────────────────────────────┘
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
| **Prompt Injection** | **Critical** | **Input Guard + Regex blacklist** |
| **Invalid JSON output** | **High** | **Pydantic + AutoFixParser** |
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
