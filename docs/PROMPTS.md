# 📝 Prompt Templates

> Tài liệu này chứa tất cả các prompt templates cho hệ thống.
> **QUAN TRỌNG:** Prompts được version control trên **LangSmith Hub** để hỗ trợ A/B testing và rollback.

---

## 🔄 LangSmith Hub Integration

### Setup

```python
# core/langsmith/versioning.py
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "student-planner"

client = Client()

class PromptManager:
    """
    Quản lý prompt versions trên LangSmith Hub
    Hub repo: maisonhai3/student-planner
    """
    
    HUB_OWNER = "maisonhai3"
    HUB_REPO = "student-planner"
    
    PROMPTS = {
        "router": "router-classifier",
        "planner": "study-planner", 
        "coder": "html-generator",
        "judge": "quality-judge",
        "refine": "plan-refiner"
    }
    
    @classmethod
    def get_prompt(cls, name: str, version: str = None) -> ChatPromptTemplate:
        """
        Pull prompt từ LangSmith Hub
        
        Args:
            name: router | planner | coder | judge | refine
            version: specific commit hash hoặc None for latest
        """
        prompt_path = f"{cls.HUB_OWNER}/{cls.PROMPTS[name]}"
        if version:
            prompt_path = f"{prompt_path}:{version}"
        
        return hub.pull(prompt_path)
    
    @classmethod
    def push_prompt(cls, name: str, prompt: ChatPromptTemplate, message: str = ""):
        """
        Push prompt mới lên LangSmith Hub (creates new version)
        """
        prompt_path = f"{cls.HUB_OWNER}/{cls.PROMPTS[name]}"
        hub.push(prompt_path, prompt, new_repo_description=message)
        
    @classmethod
    def get_current_versions(cls) -> dict:
        """
        Get current version hash for all prompts
        """
        versions = {}
        for name, hub_name in cls.PROMPTS.items():
            try:
                prompt = hub.pull(f"{cls.HUB_OWNER}/{hub_name}")
                # Get the latest commit hash from metadata
                versions[name] = getattr(prompt, '_lc_id', 'unknown')[:8]
            except Exception:
                versions[name] = "not_found"
        return versions
```

### Usage in Django Views

```python
# apps/planner/services/planner.py
from core.langsmith.versioning import PromptManager

class PlannerService:
    def __init__(self):
        # Pull latest prompts from LangSmith Hub
        self.router_prompt = PromptManager.get_prompt("router")
        self.planner_prompt = PromptManager.get_prompt("planner")
        self.coder_prompt = PromptManager.get_prompt("coder")
        
        # Store versions for tracking
        self.prompt_versions = PromptManager.get_current_versions()
```

---

## 1. Router Prompt (Classifier)

**Hub Path:** `maisonhai3/router-classifier`  
**Mục đích:** Phân loại input của sinh viên là "dễ" hay "khó" để route đến model phù hợp.  
**Model:** Gemini 2.5 Flash

### Template

```python
from langchain_core.prompts import ChatPromptTemplate

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an intelligent classifier for a student study planning system.

Your job is to analyze the student's input and determine the COMPLEXITY level.

## Classification Rules:

### EASY (Route to Gemini Flash):
- Simple weekly schedule requests
- Single subject planning
- Clear, structured syllabus input
- Basic to-do list organization
- Less than 5 tasks/subjects
- No conflicting constraints

### HARD (Route to Gemini 2.5 Pro):
- Multiple subjects with complex dependencies
- Exam preparation with time constraints
- Project deadlines overlapping with exams
- Vague or unstructured input requiring interpretation
- Requests involving priority optimization
- More than 5 subjects or 10+ tasks
- Special constraints (work schedule, health issues, etc.)

## Output Format:
Respond with ONLY a JSON object:
{{
  "complexity": "easy" | "hard",
  "confidence": 0.0-1.0,
  "reason": "Brief explanation in Vietnamese"
}}"""),
    ("human", """Analyze this student input and classify its complexity:

---
{user_input}
---""")
])

# Push to LangSmith Hub
# hub.push("maisonhai3/router-classifier", ROUTER_PROMPT)
```

---

## 2. Planner Prompt (Study Plan Generator)

**Hub Path:** `maisonhai3/study-planner`  
**Mục đích:** Tạo kế hoạch học tập có cấu trúc JSON từ input của sinh viên.  
**Model:** Gemini 2.5 Flash (Easy) hoặc Gemini 2.5 Pro (Hard)

### Template

```python
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert study planning assistant for Vietnamese university students.

## Your Task:
Convert the student's unstructured input (syllabus, to-do list, notes) into a structured study plan.

## Planning Principles:
1. **Spaced Repetition**: Distribute study sessions, don't cram
2. **Active Recall**: Include review sessions
3. **Pomodoro-friendly**: Sessions should be 25-50 minutes
4. **Buffer Time**: Leave 20% buffer for unexpected events
5. **Energy Management**: Hard tasks in morning, reviews in evening

## Output Schema:
{{
  "plan_title": "Kế hoạch học tập - [Subject/Period]",
  "duration": {{
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "total_days": number
  }},
  "subjects": [
    {{
      "name": "Subject name",
      "priority": "high" | "medium" | "low",
      "total_hours": number,
      "color": "#hexcode"
    }}
  ],
  "schedule": [
    {{
      "date": "YYYY-MM-DD",
      "day_of_week": "Monday",
      "sessions": [
        {{
          "start_time": "HH:MM",
          "end_time": "HH:MM",
          "subject": "Subject name",
          "task": "Specific task description",
          "type": "study" | "review" | "practice" | "break",
          "notes": "Optional tips"
        }}
      ]
    }}
  ],
  "milestones": [
    {{
      "date": "YYYY-MM-DD",
      "title": "Milestone name",
      "description": "What should be achieved"
    }}
  ],
  "tips": [
    "Personalized study tips based on the plan"
  ]
}}

## Important Rules:
- Always respond in Vietnamese for titles and descriptions
- Use 24-hour time format
- Include at least one review session per subject per week
- Never schedule more than 4 hours of intensive study per day
- Include breaks between sessions"""),
    ("human", """Create a study plan based on this input:

---
{user_input}
---

Additional context:
- Current date: {current_date}
- Preferred study hours per day: {study_hours_per_day}
- Available days: {available_days}""")
])

# Push to LangSmith Hub
# hub.push("maisonhai3/study-planner", PLANNER_PROMPT)
```

---

## 3. Coder Prompt (HTML/Tailwind Generator)

**Hub Path:** `maisonhai3/html-generator`  
**Mục đích:** Chuyển đổi JSON plan thành HTML có thể render trong Iframe.  
**Model:** Gemini 2.5 Flash

### Template

```python
CODER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Frontend Developer specializing in creating beautiful, responsive HTML pages.

## Your Task:
Convert the given Study Plan JSON into a SINGLE, SELF-CONTAINED HTML file.

## Technical Requirements:
1. Use Tailwind CSS via CDN (include in <head>)
2. The HTML must be completely self-contained (no external files except CDN)
3. Must be mobile-responsive
4. Use modern, clean design with good typography
5. Include smooth animations for better UX

## Design Guidelines:
1. **Color Scheme**: Use the colors from the plan's subject.color field
2. **Layout**: 
   - Calendar view for weekly schedule
   - Card-based layout for daily tasks
   - Progress indicators for milestones
3. **Typography**:
   - Vietnamese-friendly fonts (Inter, Roboto)
   - Clear hierarchy (h1 > h2 > h3)
4. **Interactive Elements**:
   - Hover effects on cards
   - Collapsible sections for daily details
   - Visual progress bars

## Required Sections:
1. Header with plan title and date range
2. Subject overview with color-coded cards
3. Weekly calendar view OR daily timeline
4. Milestones timeline
5. Tips section at the bottom

## Output Format:
Return ONLY the complete HTML code. No explanations, no markdown code blocks.
Start with <!DOCTYPE html> and end with </html>.

## Security Rules:
- NO JavaScript event handlers (onclick, etc.)
- NO inline scripts that execute code
- NO external resources except Tailwind CDN
- NO forms or input elements"""),
    ("human", """Convert this Study Plan JSON into a beautiful HTML page:

```json
{plan_json}
```

Style preferences:
- Theme: {theme} (light/dark)
- Accent color: {accent_color}
- Layout: {layout} (calendar/timeline/cards)""")
])

# Push to LangSmith Hub
# hub.push("maisonhai3/html-generator", CODER_PROMPT)
```

---

## 4. Judge Prompt (LLM-as-a-Judge)

**Hub Path:** `maisonhai3/quality-judge`  
**Mục đích:** Đánh giá chất lượng kế hoạch học tập để tính F1 Score.  
**Model:** Gemini 2.5 Pro (cần model mạnh nhất)

### Template

```python
JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert evaluator for student study plans.

## Your Task:
Evaluate the quality of a generated study plan based on multiple criteria.

## Evaluation Criteria (Score 1-5 each):

### 1. Completeness (Đầy đủ)
- Does it cover all subjects/tasks from input?
- Are there review sessions?
- Are milestones defined?

### 2. Feasibility (Khả thi)
- Is the daily study load reasonable (< 6 hours)?
- Are breaks included?
- Is there buffer time?

### 3. Pedagogical Soundness (Phương pháp học)
- Is spaced repetition applied?
- Are difficult tasks scheduled at optimal times?
- Is there variety in study activities?

### 4. Clarity (Rõ ràng)
- Are task descriptions specific?
- Is the schedule easy to follow?
- Are priorities clear?

### 5. Personalization (Cá nhân hóa)
- Does it consider student's constraints?
- Are tips relevant to the student's situation?
- Is the workload adapted to available time?

## Output Format:
{{
  "scores": {{
    "completeness": 1-5,
    "feasibility": 1-5,
    "pedagogical_soundness": 1-5,
    "clarity": 1-5,
    "personalization": 1-5
  }},
  "overall_score": 1-5 (weighted average),
  "verdict": "good" | "acceptable" | "poor",
  "feedback": "Detailed feedback in Vietnamese",
  "suggestions": ["List of improvement suggestions"]
}}"""),
    ("human", """## Original Student Input:
{original_input}

## Generated Study Plan:
{generated_plan}

## User Action:
{user_action} (saved/regenerated/abandoned)

Please evaluate this study plan.""")
])

# Push to LangSmith Hub
# hub.push("maisonhai3/quality-judge", JUDGE_PROMPT)
```

---

## 5. Refinement Prompt (Khi user Regenerate)

**Hub Path:** `maisonhai3/plan-refiner`  
**Mục đích:** Cải thiện plan dựa trên feedback ngầm (user bấm Regenerate).  
**Model:** Gemini 2.5 Pro

### Template

```python
REFINE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a study plan improvement specialist.

The student was not satisfied with the previous plan and requested a new one.
Analyze what might be wrong and generate an IMPROVED plan.

## Common Issues to Fix:
1. Too intensive schedule
2. Not enough breaks
3. Subjects not properly distributed
4. Missing important topics
5. Unrealistic time estimates

## Improvement Strategy:
- If previous plan was too dense → Add more breaks, reduce daily hours
- If previous plan was too sparse → Add more structure, specific tasks
- If layout was confusing → Simplify, use clearer groupings
- Always try a DIFFERENT approach than before

## Output:
Generate a completely new plan JSON following the standard schema.
Make it noticeably different from the previous attempt."""),
    ("human", """## Original Input:
{original_input}

## Previous Plan (User rejected this):
{previous_plan}

## Attempt Number: {attempt_number}

Generate an improved study plan.""")
])

# Push to LangSmith Hub
# hub.push("maisonhai3/plan-refiner", REFINE_PROMPT)
```

---

## 📌 Prompt Version History

Tracked automatically on LangSmith Hub. View at:
`https://smith.langchain.com/hub/maisonhai3`

### Manual Version Log

| Prompt | Version | Date | Changes |
|--------|---------|------|---------|
| router-classifier | v1.0 | 2026-01-18 | Initial version |
| study-planner | v1.0 | 2026-01-18 | Initial version |
| html-generator | v1.0 | 2026-01-18 | Initial version |
| quality-judge | v1.0 | 2026-01-18 | Initial version |
| plan-refiner | v1.0 | 2026-01-18 | Initial version |

---

## 🔧 CLI Commands for Prompt Management

```bash
# Push all prompts to LangSmith Hub
cd apps/api
uv run python -m core.langsmith.push_prompts

# Pull specific version
uv run python -c "from langchain import hub; print(hub.pull('maisonhai3/study-planner:abc123'))"

# Compare two versions
uv run python -m core.langsmith.compare_prompts study-planner v1.0 v1.1
```

### Push Script

```python
# core/langsmith/push_prompts.py
from langchain import hub
from .prompts import ROUTER_PROMPT, PLANNER_PROMPT, CODER_PROMPT, JUDGE_PROMPT, REFINE_PROMPT

PROMPTS = {
    "maisonhai3/router-classifier": ROUTER_PROMPT,
    "maisonhai3/study-planner": PLANNER_PROMPT,
    "maisonhai3/html-generator": CODER_PROMPT,
    "maisonhai3/quality-judge": JUDGE_PROMPT,
    "maisonhai3/plan-refiner": REFINE_PROMPT,
}

def push_all():
    for path, prompt in PROMPTS.items():
        print(f"Pushing {path}...")
        hub.push(path, prompt)
        print(f"✅ {path} pushed successfully")

if __name__ == "__main__":
    push_all()
```

---

## 🧪 Testing Prompts

### Easy Input Example:
```
Tuần sau tôi có bài kiểm tra môn Toán Cao Cấp.
Cần ôn tập 3 chương: Giới hạn, Đạo hàm, Tích phân.
Mỗi ngày tôi có thể học 2 tiếng buổi tối.
```

### Hard Input Example:
```
Em là sinh viên năm 3 ngành CNTT. Học kỳ này em có:
- Đồ án môn học (deadline 15/2)
- Thi cuối kỳ 5 môn (từ 20/2 - 28/2)
- Thực tập công ty part-time (T2, T4, T6 sáng)
- Muốn học thêm AWS để thi chứng chỉ

Em không biết sắp xếp thế nào vì đồ án còn dang dở mà thi cũng gần.
Buổi tối em hay mệt nên chỉ học được nhẹ nhàng thôi.
```

### Test Command

```bash
cd apps/api
uv run python -m tests.test_prompts
```

---

*Document version: 2.0*  
*Last updated: 2026-01-18*  
*LangSmith Hub: maisonhai3/student-planner*
