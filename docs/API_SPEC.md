# 📡 API Specification

> Django REST Framework API documentation cho Student Study Planner Backend

**Base URL:** `http://localhost:8000` (development) | `https://api.studyplanner.com` (production)

**Content-Type:** `application/json`

---

## Authentication

> MVP Phase: Không có authentication  
> Production: Sẽ thêm Firebase Auth token

```
Authorization: Bearer <firebase_id_token>
```

---

## Django URL Configuration

```python
# apps/api/config/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('apps.planner.urls')),
    path('api/v1/', include('apps.feedback.urls')),
]

# apps/api/apps/planner/urls.py
from django.urls import path
from .views import GeneratePlanView, PlanListCreateView, PlanDetailView, RegeneratePlanView

urlpatterns = [
    path('generate/', GeneratePlanView.as_view(), name='generate-plan'),
    path('plans/', PlanListCreateView.as_view(), name='plan-list-create'),
    path('plans/<str:plan_id>/', PlanDetailView.as_view(), name='plan-detail'),
    path('plans/<str:plan_id>/regenerate/', RegeneratePlanView.as_view(), name='regenerate-plan'),
]

# apps/api/apps/feedback/urls.py
from django.urls import path
from .views import FeedbackView

urlpatterns = [
    path('feedback/', FeedbackView.as_view(), name='feedback'),
]
```

---

## Endpoints

### 1. Generate Study Plan

Tạo kế hoạch học tập từ input của sinh viên.

```
POST /api/v1/generate/
```

#### Django View

```python
# apps/planner/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GeneratePlanInputSerializer, PlanOutputSerializer
from .services.planner import PlannerService

class GeneratePlanView(APIView):
    def post(self, request):
        serializer = GeneratePlanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = PlannerService()
        result = service.generate(serializer.validated_data)
        
        output_serializer = PlanOutputSerializer(result)
        return Response({
            'success': True,
            'data': output_serializer.data
        }, status=status.HTTP_200_OK)
```

#### Request Body

```json
{
  "input": {
    "syllabus": "string - Nội dung syllabus hoặc mô tả môn học",
    "todos": ["string - Danh sách các việc cần làm"],
    "deadline": "YYYY-MM-DD (optional)",
    "preferences": {
      "study_hours_per_day": 4,
      "preferred_times": ["morning", "evening"],
      "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
      "theme": "light",
      "layout": "calendar"
    }
  },
  "session_id": "string - Anonymous session ID for tracking"
}
```

#### Serializers

```python
# apps/planner/serializers.py
from rest_framework import serializers

class PreferencesSerializer(serializers.Serializer):
    study_hours_per_day = serializers.IntegerField(default=4, min_value=1, max_value=12)
    preferred_times = serializers.ListField(
        child=serializers.ChoiceField(choices=['morning', 'afternoon', 'evening']),
        required=False
    )
    available_days = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    theme = serializers.ChoiceField(choices=['light', 'dark'], default='light')
    layout = serializers.ChoiceField(choices=['calendar', 'timeline', 'cards'], default='calendar')

class PlanInputSerializer(serializers.Serializer):
    syllabus = serializers.CharField(required=True, min_length=10)
    todos = serializers.ListField(child=serializers.CharField(), required=False, default=[])
    deadline = serializers.DateField(required=False)
    preferences = PreferencesSerializer(required=False)

class GeneratePlanInputSerializer(serializers.Serializer):
    input = PlanInputSerializer()
    session_id = serializers.CharField(required=True)
```

#### Response (Success - 200)

```json
{
  "success": true,
  "data": {
    "plan_id": "uuid",
    "json_plan": {
      "plan_title": "Kế hoạch học tập - Toán Cao Cấp",
      "duration": {
        "start_date": "2026-01-20",
        "end_date": "2026-01-27",
        "total_days": 7
      },
      "subjects": [...],
      "schedule": [...],
      "milestones": [...],
      "tips": [...]
    },
    "html_content": "<!DOCTYPE html>...",
    "metadata": {
      "model_used": "gemini-flash",
      "router_decision": "easy",
      "generation_time_ms": 2340,
      "tokens_used": 1520,
      "prompt_versions": {
        "router": "v1.0",
        "planner": "v1.2",
        "coder": "v1.0"
      }
    }
  }
}
```

#### Response (Error - 400/500)

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Input too short. Please provide more details.",
    "details": {}
  }
}
```

#### Error Codes

| Code | Description |
|------|-------------|
| INVALID_INPUT | Input validation failed |
| GENERATION_FAILED | AI failed to generate plan |
| RATE_LIMITED | Too many requests |
| MODEL_UNAVAILABLE | AI model is down |

---

### 2. Save Plan

Lưu kế hoạch vào database.

```
POST /api/v1/plans/
```

#### Django View

```python
class PlanListCreateView(APIView):
    def post(self, request):
        serializer = SavePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from core.firebase.client import FirestoreClient
        db = FirestoreClient()
        result = db.save_plan(serializer.validated_data)
        
        return Response({
            'success': True,
            'data': {
                'plan_id': result['id'],
                'share_url': f"https://studyplanner.com/plan/{result['id']}",
                'created_at': result['created_at']
            }
        }, status=status.HTTP_201_CREATED)
```

#### Request Body

```json
{
  "plan_id": "uuid - từ generate response",
  "session_id": "string",
  "title": "string (optional) - Custom title"
}
```

#### Response (Success - 201)

```json
{
  "success": true,
  "data": {
    "plan_id": "uuid",
    "share_url": "https://studyplanner.com/plan/abc123",
    "created_at": "2026-01-18T10:30:00Z"
  }
}
```

---

### 3. Get Plan

Lấy thông tin kế hoạch đã lưu.

```
GET /api/v1/plans/{plan_id}/
```

#### Django View

```python
class PlanDetailView(APIView):
    def get(self, request, plan_id):
        from core.firebase.client import FirestoreClient
        db = FirestoreClient()
        
        plan = db.get_plan(plan_id)
        if not plan:
            return Response({
                'success': False,
                'error': {
                    'code': 'PLAN_NOT_FOUND',
                    'message': 'Plan with this ID does not exist'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Increment view count
        db.increment_view_count(plan_id)
        
        return Response({
            'success': True,
            'data': plan
        })
```

#### Response (Success - 200)

```json
{
  "success": true,
  "data": {
    "plan_id": "uuid",
    "input": {...},
    "json_plan": {...},
    "html_content": "<!DOCTYPE html>...",
    "metadata": {
      "created_at": "2026-01-18T10:30:00Z",
      "updated_at": "2026-01-18T10:30:00Z",
      "regenerate_count": 0,
      "view_count": 5,
      "prompt_versions": {
        "router": "v1.0",
        "planner": "v1.2",
        "coder": "v1.0"
      }
    }
  }
}
```

---

### 4. Regenerate Plan

Tạo lại kế hoạch (khi user không hài lòng).

```
POST /api/v1/plans/{plan_id}/regenerate/
```

#### Django View

```python
class RegeneratePlanView(APIView):
    def post(self, request, plan_id):
        serializer = RegenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from core.firebase.client import FirestoreClient
        from .services.planner import PlannerService
        
        db = FirestoreClient()
        original_plan = db.get_plan(plan_id)
        
        if not original_plan:
            return Response({
                'success': False,
                'error': {'code': 'PLAN_NOT_FOUND', 'message': 'Plan not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        service = PlannerService()
        new_plan = service.regenerate(
            original_input=original_plan['input'],
            previous_plan=original_plan['json_plan'],
            attempt_number=original_plan['metadata']['regenerate_count'] + 1
        )
        
        return Response({
            'success': True,
            'data': new_plan
        })
```

#### Request Body

```json
{
  "session_id": "string",
  "feedback": "string (optional) - Reason for regeneration"
}
```

---

### 5. Track Feedback

Ghi nhận hành động của user để tính F1 Score.

```
POST /api/v1/feedback/
```

#### Django View

```python
# apps/feedback/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FeedbackSerializer

class FeedbackView(APIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from core.firebase.client import FirestoreClient
        from core.langsmith.client import LangSmithClient
        
        db = FirestoreClient()
        langsmith = LangSmithClient()
        
        # Save to Firestore
        db.save_feedback(serializer.validated_data)
        
        # Log to LangSmith for evaluation
        langsmith.log_feedback(
            plan_id=serializer.validated_data['plan_id'],
            action=serializer.validated_data['action']
        )
        
        return Response({
            'success': True,
            'message': 'Feedback recorded'
        })
```

#### Request Body

```json
{
  "plan_id": "uuid",
  "session_id": "string",
  "action": "save" | "regenerate" | "share" | "abandon",
  "metadata": {
    "time_spent_seconds": 45,
    "scroll_depth": 0.8
  }
}
```

---

### 6. Health Check

Kiểm tra trạng thái service.

```
GET /api/v1/health/
```

#### Django View

```python
# apps/planner/views.py
class HealthCheckView(APIView):
    def get(self, request):
        from core.langsmith.client import LangSmithClient
        
        # Check model availability
        gemini_status = "available"
        gpt4_status = "available"
        
        try:
            # Quick ping to check connectivity
            pass
        except Exception:
            gemini_status = "unavailable"
        
        return Response({
            'status': 'healthy',
            'version': '2.0.0',
            'framework': 'Django REST Framework',
            'models': {
                'gemini_flash': gemini_status,
                'gpt_4o': gpt4_status
            },
            'database': 'connected',
            'langsmith': 'connected'
        })
```

---

## Django REST Settings

```python
# apps/api/config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'generate': '10/minute',
        'regenerate': '5/minute',
    },
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}
```

## Custom Exception Handler

```python
# core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'success': False,
            'error': {
                'code': exc.__class__.__name__.upper(),
                'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
                'details': response.data
            }
        }
        response.data = custom_response
    
    return response
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /api/v1/generate/ | 10 requests | 1 minute |
| POST /api/v1/plans/{id}/regenerate/ | 5 requests | 1 minute |
| GET /api/v1/plans/* | 100 requests | 1 minute |

Custom Throttle:

```python
# core/throttling.py
from rest_framework.throttling import AnonRateThrottle

class GenerateRateThrottle(AnonRateThrottle):
    scope = 'generate'

class RegenerateRateThrottle(AnonRateThrottle):
    scope = 'regenerate'
```

---

## CORS Configuration

```python
# config/settings/base.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://studyplanner.com",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
```

---

## SDK Examples

### JavaScript/TypeScript (Frontend)

```typescript
// apps/web/src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function generatePlan(input: PlanInput): Promise<PlanResponse> {
  const response = await fetch(`${API_URL}/api/v1/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: {
        syllabus: input.syllabus,
        todos: input.todos,
        preferences: {
          study_hours_per_day: 3,
          theme: 'light'
        }
      },
      session_id: crypto.randomUUID()
    })
  });

  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error.message);
  }
  
  return data.data;
}

export async function savePlan(planId: string): Promise<SavedPlan> {
  const response = await fetch(`${API_URL}/api/v1/plans/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      plan_id: planId,
      session_id: getSessionId()
    })
  });
  
  return response.json();
}
```

### Python (Testing)

```python
# tests/test_api.py
import httpx
import pytest

@pytest.mark.asyncio
async def test_generate_plan():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/generate/",
            json={
                "input": {
                    "syllabus": "Môn Toán Cao Cấp - Chương 1: Giới hạn",
                    "todos": ["Ôn tập định nghĩa", "Làm bài tập"],
                    "preferences": {
                        "study_hours_per_day": 2
                    }
                },
                "session_id": "test-session-123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "html_content" in data["data"]
```

---

*API Version: 2.0*  
*Framework: Django REST Framework*  
*Last updated: 2026-01-18*
