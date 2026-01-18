# 📊 Evaluation Methodology

> Hướng dẫn đánh giá chất lượng hệ thống Study Planner sử dụng F1 Score

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

## 4. LLM-as-a-Judge Pipeline

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
         ▼ GPT-4o Judge
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

### Sampling Strategy

```python
def should_sample_for_judge(plan_metadata: dict) -> bool:
    """
    Quyết định có gửi plan này cho Judge không.
    """
    import random
    
    # Base rate: 5%
    if random.random() > 0.05:
        return False
    
    # Ưu tiên sample các cases thú vị
    priority_cases = [
        plan_metadata.get("regenerate_count", 0) >= 2,  # Nhiều regenerate
        plan_metadata.get("router_decision") == "hard", # Complex inputs
        plan_metadata.get("model_used") == "gpt-4o",    # Expensive model
    ]
    
    if any(priority_cases):
        return random.random() < 0.20  # 20% cho priority cases
    
    return True
```

### Judge Evaluation Code

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

class JudgeScore(BaseModel):
    completeness: int = Field(ge=1, le=5)
    feasibility: int = Field(ge=1, le=5)
    pedagogical_soundness: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    personalization: int = Field(ge=1, le=5)
    overall_score: float = Field(ge=1.0, le=5.0)
    verdict: Literal["good", "acceptable", "poor"]
    feedback: str
    
async def evaluate_plan(
    original_input: str,
    generated_plan: dict,
    user_action: str
) -> JudgeScore:
    """
    Đánh giá chất lượng plan bằng GPT-4o.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(JudgeScore)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", JUDGE_SYSTEM_PROMPT),
        ("human", JUDGE_USER_TEMPLATE)
    ])
    
    chain = prompt | structured_llm
    
    result = await chain.ainvoke({
        "original_input": original_input,
        "generated_plan": json.dumps(generated_plan, ensure_ascii=False),
        "user_action": user_action
    })
    
    return result
```

---

## 5. Metrics Dashboard

### Daily Metrics

```python
@dataclass
class DailyMetrics:
    date: str
    total_generations: int
    unique_users: int
    
    # Core metrics
    save_count: int
    regenerate_count: int
    abandon_count: int
    
    # Calculated
    @property
    def precision(self) -> float:
        denom = self.save_count + self.regenerate_count
        return self.save_count / denom if denom > 0 else 0
    
    # Cost metrics
    gemini_flash_calls: int
    gpt4o_calls: int
    total_cost_usd: float
    
    # Performance
    avg_response_time_ms: int
    p95_response_time_ms: int
    
    # Router accuracy
    router_easy_correct: int  # Easy → Flash → Saved
    router_hard_correct: int  # Hard → GPT4 → Saved
    router_easy_wrong: int    # Easy → Flash → Regenerated
    router_hard_wrong: int    # Hard → GPT4 → Regenerated
```

### Weekly Report Template

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

### 💰 Cost Analysis
- Total API cost: $45.20
- Cost per generation: $0.032
- Gemini Flash: 89% of calls, 23% of cost
- GPT-4o: 11% of calls, 77% of cost

### 🐛 Top Issues (from Regenerations)
1. "Plan quá dày đặc" - 23 occurrences
2. "Thiếu breaks" - 18 occurrences
3. "Thời gian không hợp lý" - 12 occurrences

### 🎯 Action Items
- [ ] Adjust Planner prompt to reduce density
- [ ] Add explicit break scheduling rule
- [ ] Review time estimation logic
```

---

## 6. Feedback Loop (Tự cải thiện)

### Automatic Prompt Tuning

```python
async def analyze_failures_and_suggest_improvements():
    """
    Phân tích các plans bị regenerate nhiều,
    đề xuất cải thiện prompt.
    """
    # 1. Lấy 20 plans bị regenerate >= 2 lần
    failed_plans = await db.get_failed_plans(limit=20)
    
    # 2. Tìm pattern chung
    analysis_prompt = """
    Analyze these failed study plans and identify common issues:
    {failed_plans}
    
    Output:
    - Top 3 recurring problems
    - Suggested prompt modifications
    - Example improvements
    """
    
    # 3. Update prompt suggestions (con người review)
    suggestions = await llm.ainvoke(analysis_prompt)
    await notify_team(suggestions)
```

### A/B Testing Framework

```python
class PromptExperiment:
    """
    Test 2 versions of prompt để xem version nào có F1 cao hơn.
    """
    def __init__(self, name: str, control: str, treatment: str):
        self.name = name
        self.control_prompt = control
        self.treatment_prompt = treatment
        self.traffic_split = 0.5  # 50/50
        
    async def get_prompt(self, session_id: str) -> str:
        # Consistent assignment based on session
        is_treatment = hash(session_id) % 100 < (self.traffic_split * 100)
        return self.treatment_prompt if is_treatment else self.control_prompt
    
    async def analyze_results(self, min_samples: int = 100) -> dict:
        control_f1 = await self._calculate_f1("control")
        treatment_f1 = await self._calculate_f1("treatment")
        
        return {
            "control_f1": control_f1,
            "treatment_f1": treatment_f1,
            "winner": "treatment" if treatment_f1 > control_f1 else "control",
            "confidence": self._calculate_significance()
        }
```

---

## 7. LangSmith Integration

### Logging Code

```python
import os
from langsmith import Client
from langchain.callbacks import LangChainTracer

# Setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "student-planner-prod"

client = Client()

# Create dataset for evaluation
def log_for_evaluation(
    run_id: str,
    input_data: dict,
    output_data: dict,
    user_action: str
):
    """
    Log data point cho F1 calculation.
    """
    client.create_example(
        dataset_name="planner-quality-eval",
        inputs=input_data,
        outputs={
            **output_data,
            "user_action": user_action,
            "is_positive": user_action == "save"
        }
    )
```

### Running Evaluation

```python
from langsmith.evaluation import evaluate

def quality_evaluator(run, example):
    """
    Custom evaluator cho LangSmith.
    """
    prediction = run.outputs.get("json_plan", {})
    reference_action = example.outputs.get("user_action")
    
    # Simple heuristic
    if reference_action == "save":
        return {"score": 1.0, "label": "positive"}
    elif reference_action == "regenerate":
        return {"score": 0.0, "label": "negative"}
    else:
        return {"score": 0.5, "label": "neutral"}

# Run evaluation
results = evaluate(
    lambda x: generate_plan(x["input"]),
    data="planner-quality-eval",
    evaluators=[quality_evaluator],
    experiment_prefix="prompt-v2"
)

print(f"Overall F1: {results.summary['f1_score']}")
```

---

## 8. Targets & Alerts

### Quality Thresholds

```yaml
# alerts.yaml
metrics:
  f1_score:
    warning: 0.65
    critical: 0.55
    target: 0.75
    
  precision:
    warning: 0.60
    critical: 0.50
    target: 0.70
    
  avg_response_time_ms:
    warning: 8000
    critical: 15000
    target: 5000
    
  cost_per_generation_usd:
    warning: 0.08
    critical: 0.15
    target: 0.05

alerts:
  - name: "F1 Score Drop"
    condition: "f1_score < warning for 1 hour"
    action: "slack_notify"
    
  - name: "High Regenerate Rate"
    condition: "regenerate_count / total > 0.4 for 30 min"
    action: "slack_notify + pause_traffic"
```

---

## 9. Checklist Trước Production

- [ ] LangSmith project created và configured
- [ ] Sampling rate set (5% default)
- [ ] Judge prompt tested và validated
- [ ] Daily metrics dashboard deployed
- [ ] Alerting rules configured
- [ ] Feedback table in Firestore created
- [ ] First 50 manual labels for baseline
- [ ] A/B testing framework ready

---

*Document version: 1.0*  
*Last updated: 2026-01-18*
