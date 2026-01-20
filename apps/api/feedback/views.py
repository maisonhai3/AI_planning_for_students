"""
Feedback API Views - Track user actions for F1 Score calculation
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class FeedbackView(APIView):
    """
    POST /api/v1/feedback/
    Track user actions (save, regenerate, share)
    
    Used for F1 Score calculation:
    - save = positive signal (TP)
    - regenerate = negative signal (FN)
    - share = strong positive signal
    """
    
    def post(self, request):
        plan_id = request.data.get("plan_id")
        action = request.data.get("action")  # save | regenerate | share
        
        if not plan_id or not action:
            return Response(
                {"error": "plan_id and action are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ["save", "regenerate", "share"]:
            return Response(
                {"error": "action must be one of: save, regenerate, share"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Save to Firestore and/or LangSmith
        logger.info(f"Feedback received: plan_id={plan_id}, action={action}")
        
        return Response({
            "success": True,
            "message": f"Feedback recorded: {action}",
        })
