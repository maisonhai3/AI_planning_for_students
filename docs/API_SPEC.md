# 📡 API Specification

> REST API documentation cho Student Study Planner Backend

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

## Endpoints

### 1. Generate Study Plan

Tạo kế hoạch học tập từ input của sinh viên.

```
POST /api/v1/generate
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
      "tokens_used": 1520
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
POST /api/v1/plans
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
GET /api/v1/plans/{plan_id}
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
      "view_count": 5
    }
  }
}
```

#### Response (Not Found - 404)

```json
{
  "success": false,
  "error": {
    "code": "PLAN_NOT_FOUND",
    "message": "Plan with this ID does not exist"
  }
}
```

---

### 4. Regenerate Plan

Tạo lại kế hoạch (khi user không hài lòng).

```
POST /api/v1/plans/{plan_id}/regenerate
```

#### Request Body

```json
{
  "session_id": "string",
  "feedback": "string (optional) - Reason for regeneration"
}
```

#### Response (Success - 200)

```json
{
  "success": true,
  "data": {
    "plan_id": "new-uuid",
    "json_plan": {...},
    "html_content": "<!DOCTYPE html>...",
    "attempt_number": 2,
    "metadata": {...}
  }
}
```

---

### 5. Track Feedback

Ghi nhận hành động của user để tính F1 Score.

```
POST /api/v1/feedback
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

#### Response (Success - 200)

```json
{
  "success": true,
  "message": "Feedback recorded"
}
```

---

### 6. Health Check

Kiểm tra trạng thái service.

```
GET /api/v1/health
```

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "gemini_flash": "available",
    "gpt_4o": "available"
  },
  "database": "connected",
  "cache": "connected"
}
```

---

## WebSocket (Optional - Streaming)

Cho streaming response khi AI đang generate.

```
WS /api/v1/ws/generate
```

### Client → Server

```json
{
  "type": "start_generation",
  "payload": {
    "input": {...},
    "session_id": "string"
  }
}
```

### Server → Client (Streaming)

```json
// Progress updates
{
  "type": "progress",
  "payload": {
    "stage": "routing" | "planning" | "coding",
    "progress": 0.5,
    "message": "Đang tạo lịch học..."
  }
}

// Partial HTML (for streaming render)
{
  "type": "partial_html",
  "payload": {
    "content": "<div>...</div>",
    "is_complete": false
  }
}

// Final result
{
  "type": "complete",
  "payload": {
    "plan_id": "uuid",
    "json_plan": {...},
    "html_content": "..."
  }
}

// Error
{
  "type": "error",
  "payload": {
    "code": "GENERATION_FAILED",
    "message": "..."
  }
}
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /generate | 10 requests | 1 minute |
| POST /regenerate | 5 requests | 1 minute |
| GET /plans/* | 100 requests | 1 minute |

Response khi bị rate limit:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please wait.",
    "retry_after_seconds": 30
  }
}
```

---

## CORS Configuration

```
Access-Control-Allow-Origin: https://studyplanner.com, http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## SDK Examples

### JavaScript/TypeScript

```typescript
const response = await fetch('/api/v1/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: {
      syllabus: 'Môn Toán Cao Cấp...',
      todos: ['Ôn chương 1', 'Làm bài tập'],
      preferences: {
        study_hours_per_day: 3,
        theme: 'light'
      }
    },
    session_id: crypto.randomUUID()
  })
});

const data = await response.json();
if (data.success) {
  // Render HTML in iframe
  iframe.srcdoc = data.data.html_content;
}
```

### Python

```python
import httpx

async def generate_plan(syllabus: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/generate",
            json={
                "input": {
                    "syllabus": syllabus,
                    "todos": [],
                    "preferences": {}
                },
                "session_id": "test-session"
            }
        )
        return response.json()
```
