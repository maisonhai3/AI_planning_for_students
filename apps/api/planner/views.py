"""
Planner API Views
"""

import uuid
import logging
import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .guards.input_guard import InputGuard
from .services import generate_plan_html
from core.langchain.chains import ChainFactory, create_safe_generation_chain
from core.firebase import study_plan_repo

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


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
            # 2. Run generation chain
            chain = create_safe_generation_chain()
            result = chain.invoke({
                "user_input": user_input,
                "study_hours_per_day": request.data.get("study_hours_per_day", "3-4"),
                "available_days": request.data.get("available_days", "Tất cả các ngày"),
            })
            
            # 3. Generate HTML from plan
            plan_data = result.get("plan", {})
            html_content = generate_plan_html(plan_data)
            
            # 4. Generate plan ID
            plan_id = str(uuid.uuid4())
            
            return Response({
                "success": True,
                "planId": plan_id,
                "plan": plan_data,
                "html": html_content,
                "model_used": result.get("model_used"),
                "router_decision": result.get("router_decision"),
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
            logger.error(f"Generation failed: {error_msg}")
            return Response(
                {"error": str(e), "code": "GENERATION_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            # Gemini API error or unexpected error
            logger.exception("Unexpected error in generate")
            return Response(
                {
                    "error": "Generation failed. Please try again.",
                    "code": "API_ERROR"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class PlanDetailView(APIView):
    """
    GET /api/v1/plans/{id}/
    Get saved plan by ID
    """
    
    def get(self, request, plan_id):
        plan = run_async(study_plan_repo.get(plan_id))
        
        if not plan:
            return Response(
                {"error": "Plan not found", "code": "NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            "success": True,
            "plan": plan,
        })



class PlanCreateView(APIView):
    """
    POST /api/v1/plans/
    Save new plan to Firestore
    """
    
    def post(self, request):
        plan_id = request.data.get("planId") or str(uuid.uuid4())
        plan_data = request.data.get("plan", {})
        html_content = request.data.get("html", "")
        user_id = request.data.get("userId")
        
        if not plan_data:
            return Response(
                {"error": "Plan data is required", "code": "MISSING_DATA"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save to Firestore
        document = {
            "plan": plan_data,
            "html": html_content,
            "userId": user_id,
        }
        
        saved = run_async(study_plan_repo.save(plan_id, document))
        
        return Response({
            "success": True,
            "planId": plan_id,
            "savedAt": saved.get("createdAt"),
        }, status=status.HTTP_201_CREATED)


class HealthCheckView(APIView):
    """
    GET /api/v1/health/
    Health check endpoint
    """
    
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "student-planner-api",
            "version": "1.0.0",
        })
