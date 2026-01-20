"""
LangSmith Prompt Versioning Manager
Quản lý prompt versions trên LangSmith Hub
"""

import os
import logging
from typing import Optional, Dict, Any

from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

# Try to import langsmith hub - it may not be available
try:
    from langsmith import hub
    HUB_AVAILABLE = True
except ImportError:
    try:
        from langhub import hub
        HUB_AVAILABLE = True
    except ImportError:
        HUB_AVAILABLE = False
        logger.warning("LangSmith hub not available - using local prompts")


class PromptManager:
    """
    Quản lý prompt versions trên LangSmith Hub
    
    Usage:
        # Pull latest version
        prompt = PromptManager.get_prompt("planner")
        
        # Pull specific version
        prompt = PromptManager.get_prompt("planner", version="v1.2")
        
        # Push new version
        PromptManager.push_prompt("planner", my_prompt, "Fixed JSON format")
    """
    
    PROMPT_REPO = settings.LANGSMITH_HUB_REPO if hasattr(settings, 'LANGSMITH_HUB_REPO') else "maisonhai3/student-planner"
    
    # Mapping short names to full hub paths
    PROMPT_NAMES = {
        "router": "router-classifier",
        "planner": "study-planner", 
        "coder": "html-generator",
        "judge": "quality-judge",
        "refiner": "plan-refiner",
    }
    
    @classmethod
    def get_prompt(cls, name: str, version: str = "latest") -> ChatPromptTemplate:
        """
        Pull prompt từ LangSmith Hub
        
        Args:
            name: router | planner | coder | judge | refiner
            version: specific version hoặc "latest"
            
        Returns:
            ChatPromptTemplate instance
        """
        # If hub not available, use local prompts
        if not HUB_AVAILABLE:
            return cls._get_local_prompt(name)
            
        prompt_suffix = cls.PROMPT_NAMES.get(name, name)
        prompt_path = f"{cls.PROMPT_REPO}/{prompt_suffix}"
        
        if version != "latest":
            prompt_path = f"{prompt_path}:{version}"
        
        try:
            logger.info(f"Pulling prompt from hub: {prompt_path}")
            return hub.pull(prompt_path)
        except Exception as e:
            logger.warning(f"Failed to pull from hub ({prompt_path}): {e}")
            # Fallback to local prompts
            return cls._get_local_prompt(name)
    
    @classmethod
    def push_prompt(
        cls, 
        name: str, 
        prompt: ChatPromptTemplate,
        description: str = "",
    ) -> str:
        """
        Push prompt mới lên LangSmith Hub
        
        Returns:
            URL of pushed prompt
        """
        if not HUB_AVAILABLE:
            raise RuntimeError("LangSmith hub not available - cannot push prompts")
            
        prompt_suffix = cls.PROMPT_NAMES.get(name, name)
        prompt_path = f"{cls.PROMPT_REPO}/{prompt_suffix}"
        
        try:
            url = hub.push(
                prompt_path,
                prompt,
                description=description,
            )
            logger.info(f"Pushed prompt to: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to push prompt ({prompt_path}): {e}")
            raise
    
    @classmethod
    def _get_local_prompt(cls, name: str) -> ChatPromptTemplate:
        """
        Fallback: Get local prompt template khi hub không available
        """
        from .prompts import LOCAL_PROMPTS
        
        if name in LOCAL_PROMPTS:
            logger.info(f"Using local prompt for: {name}")
            return LOCAL_PROMPTS[name]
        
        raise ValueError(f"Unknown prompt name: {name}")
