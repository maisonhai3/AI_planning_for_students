"""
Output Guard - Đảm bảo output từ LLM là JSON hợp lệ
Sử dụng LangChain AutoFixParser nếu lỗi
"""

import logging
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator
from langchain_core.output_parsers import PydanticOutputParser

from .input_guard import InputGuard

logger = logging.getLogger(__name__)


# ============================================
# Pydantic Models cho Structured Output
# ============================================

class StudySession(BaseModel):
    """Một buổi học trong ngày"""
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Start time in HH:MM format")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="End time in HH:MM format")
    subject: str = Field(..., min_length=1, max_length=100, description="Subject name")
    task: str = Field(..., min_length=1, max_length=500, description="Specific task description")
    type: str = Field(..., pattern=r"^(study|review|practice|break)$", description="Session type")
    notes: Optional[str] = Field(None, max_length=500, description="Optional tips")
    
    @field_validator('end_time')
    @classmethod
    def end_after_start(cls, v, info):
        start_time = info.data.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('end_time must be after start_time')
        return v


class DailySchedule(BaseModel):
    """Lịch học trong một ngày"""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    day_of_week: str = Field(..., description="Day name in Vietnamese")
    sessions: List[StudySession] = Field(default_factory=list, description="List of study sessions")


class Milestone(BaseModel):
    """Mốc quan trọng"""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    title: str = Field(..., min_length=1, max_length=200, description="Milestone title")
    description: str = Field(..., max_length=500, description="Milestone description")


class Subject(BaseModel):
    """Môn học"""
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    priority: str = Field(..., pattern=r"^(high|medium|low)$", description="Priority level")
    total_hours: float = Field(..., gt=0, le=100, description="Total study hours")
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")


class StudyPlan(BaseModel):
    """Kế hoạch học tập hoàn chỉnh"""
    title: str = Field(..., min_length=1, max_length=200, description="Plan title")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Start date")
    end_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="End date")
    subjects: List[Subject] = Field(..., min_length=1, description="List of subjects")
    schedule: List[DailySchedule] = Field(..., min_length=1, description="Daily schedules")
    milestones: List[Milestone] = Field(default_factory=list, description="Milestones")
    tips: List[str] = Field(default_factory=list, max_length=10, description="Study tips")
    
    @field_validator('end_date')
    @classmethod
    def end_after_start_date(cls, v, info):
        start_date = info.data.get('start_date')
        if start_date and v < start_date:
            raise ValueError('end_date must be after start_date')
        return v


class RouterDecision(BaseModel):
    """Kết quả phân loại từ Router"""
    complexity: str = Field(..., pattern=r"^(easy|hard)$", description="Task complexity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: str = Field(..., max_length=500, description="Explanation in Vietnamese")


# ============================================
# Output Guard với AutoFix
# ============================================

class OutputGuard:
    """
    Đảm bảo output từ LLM là JSON hợp lệ
    Sử dụng retry với LLM nếu lỗi parse
    """
    
    def __init__(self, model_class: type = StudyPlan, max_retries: int = 2):
        self.model_class = model_class
        self.max_retries = max_retries
        self._llm = None  # Lazy initialization
        
        # Parser chính
        self.parser = PydanticOutputParser(pydantic_object=model_class)
    
    @property
    def llm(self):
        """Lazy LLM initialization to avoid requiring API key at import time"""
        if self._llm is None:
            self._llm = InputGuard.get_safe_llm_flash(temperature=0)
        return self._llm
    
    def parse(self, output: str) -> BaseModel:
        """
        Parse output với auto-fix
        
        Flow:
        1. Thử parse trực tiếp
        2. Nếu lỗi → Thử extract JSON từ output
        3. Nếu vẫn lỗi → Raise exception
        """
        import json
        import re
        
        first_error = None
        
        # Thử parse trực tiếp
        try:
            return self.parser.parse(output)
        except Exception as e:
            first_error = e
            logger.warning(f"First parse failed: {e}")
        
        # Thử extract JSON từ markdown code blocks
        json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        matches = re.findall(json_pattern, output)
        
        for match in matches:
            try:
                data = json.loads(match.strip())
                return self.model_class(**data)
            except Exception:
                continue
        
        # Thử tìm JSON object trực tiếp
        try:
            # Tìm first { và last }
            start = output.find('{')
            end = output.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = output[start:end + 1]
                data = json.loads(json_str)
                return self.model_class(**data)
        except Exception as extract_error:
            logger.warning(f"JSON extraction failed: {extract_error}")
        
        raise ValueError(
            f"Cannot parse LLM output. "
            f"Original error: {first_error}"
        )
    
    def get_format_instructions(self) -> str:
        """
        Trả về format instructions để inject vào prompt
        """
        return self.parser.get_format_instructions()


# Pre-configured guards (lazy initialization - no API key required at import)
study_plan_guard = OutputGuard(model_class=StudyPlan)
router_guard = OutputGuard(model_class=RouterDecision, max_retries=1)
