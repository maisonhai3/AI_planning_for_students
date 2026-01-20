"""
LangChain Chains - Router, Planner, Coder chains
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from langchain_core.runnables import RunnableLambda, RunnableBranch
from langchain_core.output_parsers import StrOutputParser

from planner.guards.input_guard import InputGuard
from planner.guards.output_guard import (
    OutputGuard, 
    StudyPlan, 
    RouterDecision,
    study_plan_guard,
    router_guard,
)
from core.langsmith.versioning import PromptManager

logger = logging.getLogger(__name__)


class ChainFactory:
    """Factory for creating LangChain chains with guards"""
    
    @staticmethod
    def create_router_chain():
        """
        Create Router chain để phân loại input
        
        Returns:
            Chain that outputs RouterDecision
        """
        prompt = PromptManager.get_prompt("router")
        llm = InputGuard.get_safe_llm_flash(temperature=0)
        
        chain = prompt | llm | StrOutputParser() | RunnableLambda(
            lambda x: router_guard.parse(x).model_dump()
        )
        
        return chain
    
    @staticmethod
    def create_planner_chain(use_pro: bool = False):
        """
        Create Planner chain với guards
        
        Args:
            use_pro: True để dùng Gemini Pro cho Hard tasks
            
        Returns:
            Chain that outputs StudyPlan dict
        """
        prompt = PromptManager.get_prompt("planner")
        
        # Inject format instructions
        prompt = prompt.partial(
            format_instructions=study_plan_guard.get_format_instructions()
        )
        
        # Choose model based on complexity
        if use_pro:
            llm = InputGuard.get_safe_llm_pro(temperature=0.7)
        else:
            llm = InputGuard.get_safe_llm_flash(temperature=0.7)
        
        chain = prompt | llm | StrOutputParser() | RunnableLambda(
            lambda x: study_plan_guard.parse(x).model_dump()
        )
        
        return chain
    
    @staticmethod
    def create_coder_chain():
        """
        Create Coder chain để generate HTML
        
        Returns:
            Chain that outputs HTML string
        """
        prompt = PromptManager.get_prompt("coder")
        llm = InputGuard.get_safe_llm_flash(temperature=0.5)
        
        chain = prompt | llm | StrOutputParser()
        
        return chain
    
    @staticmethod
    def create_full_chain():
        """
        Create full chain: Input → Router → Planner → Coder
        
        Returns:
            Chain that takes user_input and returns {plan, html}
        """
        router_chain = ChainFactory.create_router_chain()
        planner_easy = ChainFactory.create_planner_chain(use_pro=False)
        planner_hard = ChainFactory.create_planner_chain(use_pro=True)
        coder_chain = ChainFactory.create_coder_chain()
        
        def route_to_planner(data: Dict[str, Any]) -> Dict[str, Any]:
            """Route based on complexity"""
            user_input = data["user_input"]
            
            # Run router
            router_result = router_chain.invoke({"user_input": user_input})
            complexity = router_result.get("complexity", "easy")
            
            logger.info(f"Router decision: {complexity} (confidence: {router_result.get('confidence', 0)})")
            
            # Choose planner based on complexity
            if complexity == "hard":
                plan = planner_hard.invoke({
                    "user_input": user_input,
                    "current_date": datetime.now().strftime("%Y-%m-%d"),
                    "study_hours_per_day": data.get("study_hours_per_day", "3-4"),
                    "available_days": data.get("available_days", "Tất cả các ngày"),
                })
            else:
                plan = planner_easy.invoke({
                    "user_input": user_input,
                    "current_date": datetime.now().strftime("%Y-%m-%d"),
                    "study_hours_per_day": data.get("study_hours_per_day", "3-4"),
                    "available_days": data.get("available_days", "Tất cả các ngày"),
                })
            
            return {
                "plan": plan,
                "router_decision": router_result,
                "model_used": "gemini-2.5-pro" if complexity == "hard" else "gemini-2.5-flash",
            }
        
        def generate_html(data: Dict[str, Any]) -> Dict[str, Any]:
            """Generate HTML from plan"""
            import json
            
            plan = data["plan"]
            
            html = coder_chain.invoke({
                "plan_json": json.dumps(plan, ensure_ascii=False, indent=2),
                "theme": "light",
                "accent_color": plan.get("subjects", [{}])[0].get("color", "#3b82f6"),
                "layout": "calendar",
            })
            
            return {
                **data,
                "html": html,
            }
        
        # Build full chain
        full_chain = (
            RunnableLambda(route_to_planner)
            | RunnableLambda(generate_html)
        )
        
        return full_chain


def create_safe_generation_chain():
    """
    Create full generation chain with Input Guard
    
    This is the main entry point for the API
    """
    def validate_and_generate(data: Dict[str, Any]) -> Dict[str, Any]:
        user_input = data.get("user_input", "")
        
        # Input Guard
        is_safe, reason = InputGuard.check_input(user_input)
        if not is_safe:
            raise ValueError(f"Input blocked: {reason}")
        
        # Run full chain
        full_chain = ChainFactory.create_full_chain()
        result = full_chain.invoke(data)
        
        return result
    
    return RunnableLambda(validate_and_generate)
