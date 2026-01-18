# 📊 Evaluation Methodology

> Hướng dẫn đánh giá chất lượng hệ thống Study Planner sử dụng F1 Score
> Tích hợp với **LangSmith** cho tracing và prompt versioning

---

## 1. Tổng quan Phương pháp Đánh giá

### Vấn đề: Làm sao biết AI tạo plan tốt?

Với LLM applications, không có "ground truth" rõ ràng như classification tasks. Chúng ta sử dụng **Implicit Feedback** (feedback ngầm) từ hành vi user.

### Nguồn cảm hứng

> "User dissatisfaction can be inferred from behavioral patterns, particularly query reformulation."
> — Bing Research, 2023

---

## 2. Implicit Signals (Tín hiệu Ngầm)

### Positive Signals (Plan tốt) ✅

| Signal | Weight | Interpretation |
|--------|--------|----------------|
| **Save** | 1.0 | User hài lòng, muốn giữ lại |
| **Share** | 1.2 | User tự tin share cho người khác |
| **Time spent > 60s** | 0.5 | User đọc kỹ plan |
| **Scroll to bottom** | 0.3 | User xem hết nội dung |
| **Return visit** | 0.8 | User quay lại xem plan |

### Negative Signals (Plan không tốt) ❌

| Signal | Weight | Interpretation |
|--------|--------|----------------|
| **Regenerate** | -1.0 | User không hài lòng |
| **Regenerate x2** | -1.5 | Vẫn không hài lòng sau lần 2 |
| **Regenerate x3+** | -2.0 | Hệ thống fail hoàn toàn |
| **Abandon < 10s** | -0.8 | User bỏ đi ngay |
| **Close tab < 30s** | -0.5 | Không quan tâm đến plan |

---

## 3. Tính F1 Score

### Định nghĩa cho Context này

```
True Positive (TP)  = Plan được Save (user hài lòng)
False Positive (FP) = Plan được generate nhưng bị Regenerate (AI nghĩ ok, user nghĩ không)
False Negative (FN) = Plan hay nhưng user không Save (khó đo, ước lượng từ sampling)
True Negative (TN)  = Không áp dụng
```

### Công thức

```
Precision = TP / (TP + FP)
          = Saved / (Saved + Regenerated)
          = "Trong số plans AI tạo ra, bao nhiêu % user thực sự dùng?"

Recall = TP / (TP + FN)
       = "Trong số plans user cần, bao nhiêu % AI tạo đúng?"
       ≈ Ước lượng từ LLM-as-a-Judge

F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

### Ví dụ Tính toán

```python
# Tuần 1 data
total_generations = 100
saved = 65
regenerated = 30
abandoned = 5

# Precision
precision = saved / (saved + regenerated)
# = 65 / 95 = 0.684 (68.4%)

# Recall (từ LLM Judge trên 5% sample)
# Judge đánh giá 5 plans: 4 "good", 1 "poor but user saved anyway"
recall = 4 / 5 = 0.80

# F1 Score
f1 = 2 * (0.684 * 0.80) / (0.684 + 0.80)
# = 0.736 (73.6%)
```

---

## 4. LangSmith Integration

### 4.1 Tracing Setup (Django)

```python
# core/langsmith/client.py
import os
from langsmith import Client
from langsmith.wrappers import wrap_openai
from functools import wraps

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "student-planner"

client = Client()

class LangSmithClient:
    """
    LangSmith client cho tracing và evaluation
    """
    
    def __init__(self):
        self.client = Client()
        self.project_name = os.getenv("LANGCHAIN_PROJECT", "student-planner")
    
    def log_feedback(self, run_id: str, action: str, score: float = None):
        """
        Log user feedback to LangSmith run
        """
        if score is None:
            score = 1.0 if action == "save" else 0.0
            
        self.client.create_feedback(
            run_id=run_id,
            key="user_action",
            value=action,
            score=score,
        )
    
    def create_dataset_from_runs(self, name: str, days: int = 7):
        """
        Tạo evaluation dataset từ runs gần đây
        """
        from datetime import datetime, timedelta
        
        runs = self.client.list_runs(
            project_name=self.project_name,
            start_time=datetime.now() - timedelta(days=days),
            filter='has(feedback_keys, "user_action")'
        )
        
        dataset = self.client.create_dataset(name)
        
        for run in runs:
            self.client.create_example(
                dataset_id=dataset.id,
                inputs=run.inputs,
                outputs=run.outputs,
                metadata={
                    "user_action": run.feedback_stats.get("user_action"),
                    "prompt_versions": run.extra.get("prompt_versions", {})
                }
            )
        
        return dataset
```

### 4.2 Tracing Decorator for Django Views

```python
# core/langsmith/decorators.py
from langsmith import traceable
from functools import wraps

def trace_generation(func):
    """
    Decorator để trace generation requests
    """
    @wraps(func)
    @traceable(
        name="generate_plan",
        run_type="chain",
        tags=["production"]
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### 4.3 Usage in Django Service

```python
# apps/planner/services/planner.py
from langsmith import traceable
from core.langsmith.versioning import PromptManager

class PlannerService:
    def __init__(self):
        self.prompt_versions = PromptManager.get_current_versions()
    
    @traceable(name="route_request", run_type="chain")
    def route(self, user_input: str) -> str:
        """Route request to appropriate model"""
        router_prompt = PromptManager.get_prompt("router")
        # ... implementation
        
    @traceable(name="generate_plan", run_type="chain")
    def generate(self, input_data: dict) -> dict:
        """Generate study plan"""
        # Traces are automatically sent to LangSmith
        complexity = self.route(input_data["syllabus"])
        
        if complexity == "easy":
            plan = self._generate_with_flash(input_data)
        else:
            plan = self._generate_with_gpt4(input_data)
        
        html = self._generate_html(plan)
        
        return {
            "plan": plan,
            "html": html,
            "prompt_versions": self.prompt_versions
        }
```

---

## 5. LLM-as-a-Judge Pipeline

### Khi nào chạy Judge?

```
┌─────────────────┐
│ All Generations │
│    (100%)       │
└────────┬────────┘
         │
         ▼ Random Sample
┌─────────────────┐
│ 5% Sampled for  │
│ Quality Review  │
└────────┬────────┘
         │
         ▼ Gemini 2.5 Pro Judge
┌─────────────────┐
│ Scored Plans    │
│ (5 criteria)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ F1 Calculation  │
│ + Feedback Loop │
└─────────────────┘
```

### Django Celery Task for Evaluation

```python
# apps/feedback/tasks.py
from celery import shared_task
from langsmith import Client
from langsmith.evaluation import evaluate
from core.langsmith.versioning import PromptManager

client = Client()

@shared_task
def evaluate_sample_plans():
    """
    Celery task chạy mỗi ngày để evaluate 5% plans
    """
    from datetime import datetime, timedelta
    
    # Get yesterday's runs
    runs = list(client.list_runs(
        project_name="student-planner",
        start_time=datetime.now() - timedelta(days=1),
        end_time=datetime.now(),
        run_type="chain",
        filter='eq(name, "generate_plan")'
    ))
    
    # Sample 5%
    import random
    sample_size = max(1, len(runs) // 20)
    sampled_runs = random.sample(runs, sample_size)
    
    # Evaluate with Judge
    judge_prompt = PromptManager.get_prompt("judge")
    
    for run in sampled_runs:
        evaluate_single_run.delay(run.id)

@shared_task
def evaluate_single_run(run_id: str):
    """
    Evaluate một run với LLM-as-a-Judge
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from pydantic import BaseModel
    
    run = client.read_run(run_id)
    
    class JudgeScore(BaseModel):
        completeness: int
        feasibility: int
        pedagogical_soundness: int
        clarity: int
        personalization: int
        overall_score: float
        verdict: str
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    judge_prompt = PromptManager.get_prompt("judge")
    
    chain = judge_prompt | llm.with_structured_output(JudgeScore)
    
    result = chain.invoke({
        "original_input": run.inputs.get("user_input", ""),
        "generated_plan": run.outputs.get("plan", {}),
        "user_action": "unknown"  # Will be filled from feedback
    })
    
    # Log evaluation result
    client.create_feedback(
        run_id=run_id,
        key="judge_score",
        score=result.overall_score / 5.0,  # Normalize to 0-1
        value=result.model_dump()
    )
```

---

## 6. Prompt Version A/B Testing

### Setup A/B Test

```python
# core/langsmith/ab_testing.py
import random
from langsmith import Client
from typing import Literal

client = Client()

class PromptABTest:
    """
    A/B testing cho prompt versions
    """
    
    def __init__(self, prompt_name: str, control_version: str, treatment_version: str, traffic_split: float = 0.5):
        self.prompt_name = prompt_name
        self.control = control_version
        self.treatment = treatment_version
        self.traffic_split = traffic_split
    
    def get_variant(self, session_id: str) -> tuple[str, Literal["control", "treatment"]]:
        """
        Deterministic assignment based on session_id
        Returns (version_hash, variant_name)
        """
        # Consistent hashing for same user always gets same variant
        hash_value = hash(session_id) % 100
        
        if hash_value < (self.traffic_split * 100):
            return self.treatment, "treatment"
        else:
            return self.control, "control"
    
    def log_variant(self, run_id: str, variant: str):
        """Log which variant was used"""
        client.create_feedback(
            run_id=run_id,
            key=f"ab_test_{self.prompt_name}",
            value=variant
        )
    
    def analyze_results(self) -> dict:
        """
        Analyze A/B test results from LangSmith
        """
        control_runs = list(client.list_runs(
            project_name="student-planner",
            filter=f'has(feedback_keys, "ab_test_{self.prompt_name}") and eq(feedback_values.ab_test_{self.prompt_name}, "control")'
        ))
        
        treatment_runs = list(client.list_runs(
            project_name="student-planner", 
            filter=f'has(feedback_keys, "ab_test_{self.prompt_name}") and eq(feedback_values.ab_test_{self.prompt_name}, "treatment")'
        ))
        
        def calculate_save_rate(runs):
            saves = sum(1 for r in runs if r.feedback_stats.get("user_action") == "save")
            return saves / len(runs) if runs else 0
        
        control_rate = calculate_save_rate(control_runs)
        treatment_rate = calculate_save_rate(treatment_runs)
        
        return {
            "control_save_rate": control_rate,
            "treatment_save_rate": treatment_rate,
            "improvement": (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0,
            "control_n": len(control_runs),
            "treatment_n": len(treatment_runs),
            "recommendation": "treatment" if treatment_rate > control_rate else "control"
        }
```

### Usage in Service

```python
# apps/planner/services/planner.py
from core.langsmith.ab_testing import PromptABTest

class PlannerService:
    def __init__(self):
        # A/B test for planner prompt
        self.planner_ab_test = PromptABTest(
            prompt_name="planner",
            control_version="abc123",  # Current production
            treatment_version="def456", # New version to test
            traffic_split=0.1  # 10% get new version
        )
    
    def generate(self, input_data: dict, session_id: str):
        # Get A/B variant
        version, variant = self.planner_ab_test.get_variant(session_id)
        
        # Use the assigned version
        planner_prompt = PromptManager.get_prompt("planner", version=version)
        
        # ... generate plan ...
        
        # Log variant for analysis
        self.planner_ab_test.log_variant(run_id, variant)
```

---

## 7. Metrics Dashboard

### Daily Metrics Calculation (Django Management Command)

```python
# apps/feedback/management/commands/calculate_metrics.py
from django.core.management.base import BaseCommand
from langsmith import Client
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class DailyMetrics:
    date: str
    total_generations: int
    unique_sessions: int
    save_count: int
    regenerate_count: int
    abandon_count: int
    precision: float
    f1_score: float
    avg_response_time_ms: int
    total_cost_usd: float
    prompt_versions: dict

class Command(BaseCommand):
    help = 'Calculate daily metrics from LangSmith'
    
    def handle(self, *args, **options):
        client = Client()
        
        yesterday = datetime.now() - timedelta(days=1)
        
        runs = list(client.list_runs(
            project_name="student-planner",
            start_time=yesterday,
            end_time=datetime.now(),
            run_type="chain",
            filter='eq(name, "generate_plan")'
        ))
        
        # Calculate metrics
        save_count = sum(1 for r in runs if r.feedback_stats.get("user_action") == "save")
        regenerate_count = sum(1 for r in runs if r.feedback_stats.get("user_action") == "regenerate")
        
        precision = save_count / (save_count + regenerate_count) if (save_count + regenerate_count) > 0 else 0
        
        # Get recall from judge scores
        judged_runs = [r for r in runs if r.feedback_stats.get("judge_score")]
        recall = sum(r.feedback_stats["judge_score"]["score"] for r in judged_runs) / len(judged_runs) if judged_runs else 0.8
        
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = DailyMetrics(
            date=yesterday.strftime("%Y-%m-%d"),
            total_generations=len(runs),
            unique_sessions=len(set(r.inputs.get("session_id") for r in runs)),
            save_count=save_count,
            regenerate_count=regenerate_count,
            abandon_count=len(runs) - save_count - regenerate_count,
            precision=precision,
            f1_score=f1,
            avg_response_time_ms=sum(r.total_duration_ms for r in runs) // len(runs) if runs else 0,
            total_cost_usd=sum(r.total_cost or 0 for r in runs),
            prompt_versions={}  # Aggregate from runs
        )
        
        self.stdout.write(f"📊 Metrics for {metrics.date}")
        self.stdout.write(f"   F1 Score: {metrics.f1_score:.2%}")
        self.stdout.write(f"   Precision: {metrics.precision:.2%}")
        self.stdout.write(f"   Save Rate: {save_count}/{len(runs)}")
```

---

## 8. Weekly Report Template

```markdown
## Weekly Quality Report - Week 3, 2026

### 📊 Key Metrics
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| F1 Score | 0.74 | 0.71 | +4.2% ✅ |
| Precision | 0.68 | 0.65 | +4.6% ✅ |
| Recall (Judge) | 0.82 | 0.80 | +2.5% ✅ |

### 🔀 Router Performance
- Easy → Correct: 85%
- Hard → Correct: 78%
- Misrouted: 12%

### 📝 Prompt A/B Test Results
| Test | Control | Treatment | Winner |
|------|---------|-----------|--------|
| planner-v1.2 | 68% save | 73% save | Treatment ✅ |

### 💰 Cost Analysis
- Total API cost: $45.20
- Cost per generation: $0.032
- Gemini Flash: 89% of calls, 23% of cost
- Gemini 2.5 Pro: 11% of calls, 77% of cost

### 🎯 Action Items
- [x] Promote planner-v1.2 to 100%
- [ ] Investigate low Router accuracy for "project" inputs
- [ ] Add more break scheduling in planner prompt
```

---

## 9. Targets & Alerts

### Quality Thresholds (Django settings)

```python
# config/settings/base.py
QUALITY_THRESHOLDS = {
    "f1_score": {
        "warning": 0.65,
        "critical": 0.55,
        "target": 0.75,
    },
    "precision": {
        "warning": 0.60,
        "critical": 0.50,
        "target": 0.70,
    },
    "avg_response_time_ms": {
        "warning": 8000,
        "critical": 15000,
        "target": 5000,
    },
    "cost_per_generation_usd": {
        "warning": 0.08,
        "critical": 0.15,
        "target": 0.05,
    }
}
```

### Alert Task

```python
# apps/feedback/tasks.py
@shared_task
def check_quality_alerts():
    """Check metrics và send alerts nếu vượt threshold"""
    from django.conf import settings
    from .services import MetricsService
    
    metrics = MetricsService.get_latest()
    thresholds = settings.QUALITY_THRESHOLDS
    
    alerts = []
    
    if metrics.f1_score < thresholds["f1_score"]["critical"]:
        alerts.append(f"🚨 CRITICAL: F1 Score dropped to {metrics.f1_score:.2%}")
    elif metrics.f1_score < thresholds["f1_score"]["warning"]:
        alerts.append(f"⚠️ WARNING: F1 Score at {metrics.f1_score:.2%}")
    
    if alerts:
        send_slack_notification(alerts)
```

---

## 10. Checklist Trước Production

- [ ] LangSmith project created và configured
- [ ] Tracing enabled trong Django settings
- [ ] Sampling rate set (5% default)
- [ ] Judge prompt pushed to LangSmith Hub
- [ ] Daily metrics Celery task scheduled
- [ ] Alerting configured (Slack/Email)
- [ ] Feedback table in Firestore created
- [ ] First 50 manual labels for baseline
- [ ] A/B testing framework tested

---

*Document version: 2.0*  
*Last updated: 2026-01-18*  
*Framework: Django + LangSmith*
