"""
Input Guard - Bảo vệ đầu vào với 2 lớp:
1. Regex/Keyword blacklist (nhanh)
2. Gemini Safety Settings (sâu)

Reference: https://ai.google.dev/gemini-api/docs/safety-settings
"""

import re
import logging
from typing import Tuple, List, Dict, Any

from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


class InputGuard:
    """
    Bảo vệ đầu vào với 2 lớp:
    1. Regex/Keyword blacklist (nhanh)
    2. Gemini Safety Settings (sâu)
    """
    
    # ============================================
    # Gemini Safety Settings Configuration
    # ============================================
    # 
    # Categories:
    #   - HARM_CATEGORY_HARASSMENT: Negative/harmful comments targeting identity
    #   - HARM_CATEGORY_HATE_SPEECH: Rude, disrespectful, or profane content
    #   - HARM_CATEGORY_SEXUALLY_EXPLICIT: Sexual acts or lewd content
    #   - HARM_CATEGORY_DANGEROUS_CONTENT: Promotes harmful acts
    #
    # Thresholds:
    #   - BLOCK_LOW_AND_ABOVE: Block khi xác suất thấp trở lên (strict nhất)
    #   - BLOCK_MEDIUM_AND_ABOVE: Block khi xác suất trung bình trở lên
    #   - BLOCK_ONLY_HIGH: Block khi xác suất cao
    #   - BLOCK_NONE / OFF: Không filter (default cho Gemini 2.5/3)
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
        r"(?i)pretend\s+(to\s+be|you're)",
        r"(?i)roleplay\s+as",
        
        # Code injection
        r"(?i)<script[^>]*>",
        r"(?i)javascript:",
        r"(?i)on\w+\s*=",
        r"(?i)eval\s*\(",
        
        # Path traversal
        r"\.\./",
        r"(?i)\/etc\/passwd",
        r"(?i)\/bin\/",
    ]
    
    # Suspicious keywords (log but don't block)
    SUSPICIOUS_KEYWORDS = [
        "password", "secret", "api_key", "token",
        "admin", "root", "sudo", "hack", "exploit",
        "inject", "bypass", "override",
    ]
    
    # Maximum input length
    MAX_INPUT_LENGTH = 10000
    
    @classmethod
    def check_input(cls, text: str) -> Tuple[bool, str]:
        """
        Kiểm tra input an toàn
        
        Returns:
            (is_safe, reason)
        """
        if not text or not text.strip():
            return False, "Input cannot be empty"
        
        # 1. Check length (prevent token bombing)
        if len(text) > cls.MAX_INPUT_LENGTH:
            return False, f"Input too long (max {cls.MAX_INPUT_LENGTH} characters)"
        
        # 2. Check dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text):
                logger.warning(f"Dangerous pattern detected: {pattern[:50]}...")
                return False, "Blocked: Suspicious pattern detected"
        
        # 3. Log suspicious keywords (but allow)
        for keyword in cls.SUSPICIOUS_KEYWORDS:
            if keyword.lower() in text.lower():
                logger.warning(f"Suspicious keyword in input: {keyword}")
        
        return True, "OK"
    
    @classmethod
    def get_safety_settings(cls) -> Dict[str, str]:
        """
        Tạo Safety Settings cho LangChain Google GenAI
        
        Sử dụng BLOCK_MEDIUM_AND_ABOVE cho cân bằng giữa:
        - Không quá strict (block false positive)
        - Đủ an toàn cho educational content
        
        Reference: https://ai.google.dev/gemini-api/docs/safety-settings
        """
        return {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }
    
    @classmethod
    def get_safe_llm(
        cls, 
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
    ) -> ChatGoogleGenerativeAI:
        """
        Tạo LangChain LLM instance với Safety Settings
        """
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=settings.GOOGLE_API_KEY,
            safety_settings=cls.get_safety_settings(),
        )
    
    @classmethod
    def get_safe_llm_pro(cls, temperature: float = 0.7) -> ChatGoogleGenerativeAI:
        """
        Tạo Gemini 2.5 Pro instance cho Hard tasks
        """
        return cls.get_safe_llm(
            model="gemini-2.5-pro",
            temperature=temperature,
        )
    
    @classmethod
    def get_safe_llm_flash(cls, temperature: float = 0.7) -> ChatGoogleGenerativeAI:
        """
        Tạo Gemini 2.5 Flash instance cho Easy tasks
        """
        return cls.get_safe_llm(
            model="gemini-2.5-flash",
            temperature=temperature,
        )
