"""
Firebase Firestore client for storing and retrieving study plans.
"""
import os
import json
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Firebase Admin SDK (lazy initialization)
_db = None
_initialized = False


def _initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Supports both service account JSON file and environment variable.
    """
    global _db, _initialized
    
    if _initialized:
        return _db
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if already initialized
        try:
            firebase_admin.get_app()
            _db = firestore.client()
            _initialized = True
            return _db
        except ValueError:
            pass  # App not initialized yet
        
        # Try to get credentials from environment
        cred = None
        
        # Option 1: Service account JSON file path
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            logger.info(f"Using Firebase service account from: {service_account_path}")
        
        # Option 2: Service account JSON as environment variable
        elif os.getenv("FIREBASE_SERVICE_ACCOUNT"):
            service_account_info = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))
            cred = credentials.Certificate(service_account_info)
            logger.info("Using Firebase service account from environment variable")
        
        # Option 3: Application Default Credentials (for Cloud Run, etc.)
        else:
            cred = credentials.ApplicationDefault()
            logger.info("Using Firebase Application Default Credentials")
        
        # Initialize the app
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        _initialized = True
        
        logger.info("Firebase initialized successfully")
        return _db
        
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}")
        logger.info("Running in demo mode without Firebase")
        return None


def get_firestore_client():
    """Get the Firestore client instance."""
    return _initialize_firebase()


class StudyPlanRepository:
    """
    Repository for study plan CRUD operations.
    Falls back to in-memory storage if Firebase is not configured.
    """
    
    COLLECTION = "study_plans"
    
    def __init__(self):
        self.db = get_firestore_client()
        self._in_memory_store = {}  # Fallback for demo mode
    
    async def save(self, plan_id: str, plan_data: dict) -> dict:
        """
        Save a study plan to Firestore.
        
        Args:
            plan_id: Unique identifier for the plan
            plan_data: The study plan data to save
            
        Returns:
            The saved plan with metadata
        """
        now = datetime.utcnow().isoformat()
        
        document = {
            **plan_data,
            "id": plan_id,
            "createdAt": plan_data.get("createdAt", now),
            "updatedAt": now,
        }
        
        if self.db:
            try:
                doc_ref = self.db.collection(self.COLLECTION).document(plan_id)
                doc_ref.set(document)
                logger.info(f"Saved plan {plan_id} to Firestore")
            except Exception as e:
                logger.error(f"Failed to save plan to Firestore: {e}")
                self._in_memory_store[plan_id] = document
        else:
            # Demo mode: use in-memory storage
            self._in_memory_store[plan_id] = document
            logger.info(f"Saved plan {plan_id} to in-memory store (demo mode)")
        
        return document
    
    async def get(self, plan_id: str) -> Optional[dict]:
        """
        Retrieve a study plan by ID.
        
        Args:
            plan_id: The plan ID to retrieve
            
        Returns:
            The study plan data or None if not found
        """
        if self.db:
            try:
                doc_ref = self.db.collection(self.COLLECTION).document(plan_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    return doc.to_dict()
                return None
                
            except Exception as e:
                logger.error(f"Failed to get plan from Firestore: {e}")
                return self._in_memory_store.get(plan_id)
        else:
            # Demo mode
            return self._in_memory_store.get(plan_id)
    
    async def update(self, plan_id: str, updates: dict) -> Optional[dict]:
        """
        Update specific fields of a study plan.
        
        Args:
            plan_id: The plan ID to update
            updates: Dictionary of fields to update
            
        Returns:
            The updated plan or None if not found
        """
        updates["updatedAt"] = datetime.utcnow().isoformat()
        
        if self.db:
            try:
                doc_ref = self.db.collection(self.COLLECTION).document(plan_id)
                doc = doc_ref.get()
                
                if not doc.exists:
                    return None
                
                doc_ref.update(updates)
                return doc_ref.get().to_dict()
                
            except Exception as e:
                logger.error(f"Failed to update plan in Firestore: {e}")
                if plan_id in self._in_memory_store:
                    self._in_memory_store[plan_id].update(updates)
                    return self._in_memory_store[plan_id]
                return None
        else:
            # Demo mode
            if plan_id in self._in_memory_store:
                self._in_memory_store[plan_id].update(updates)
                return self._in_memory_store[plan_id]
            return None
    
    async def delete(self, plan_id: str) -> bool:
        """
        Delete a study plan.
        
        Args:
            plan_id: The plan ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if self.db:
            try:
                doc_ref = self.db.collection(self.COLLECTION).document(plan_id)
                doc = doc_ref.get()
                
                if not doc.exists:
                    return False
                
                doc_ref.delete()
                logger.info(f"Deleted plan {plan_id} from Firestore")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete plan from Firestore: {e}")
                if plan_id in self._in_memory_store:
                    del self._in_memory_store[plan_id]
                    return True
                return False
        else:
            # Demo mode
            if plan_id in self._in_memory_store:
                del self._in_memory_store[plan_id]
                return True
            return False
    
    async def list_by_user(self, user_id: str, limit: int = 10) -> list:
        """
        List study plans for a specific user.
        
        Args:
            user_id: The user ID to filter by
            limit: Maximum number of plans to return
            
        Returns:
            List of study plans
        """
        if self.db:
            try:
                query = (
                    self.db.collection(self.COLLECTION)
                    .where("userId", "==", user_id)
                    .order_by("createdAt", direction="DESCENDING")
                    .limit(limit)
                )
                
                docs = query.stream()
                return [doc.to_dict() for doc in docs]
                
            except Exception as e:
                logger.error(f"Failed to list plans from Firestore: {e}")
                return []
        else:
            # Demo mode
            user_plans = [
                plan for plan in self._in_memory_store.values()
                if plan.get("userId") == user_id
            ]
            return sorted(
                user_plans,
                key=lambda x: x.get("createdAt", ""),
                reverse=True
            )[:limit]


class FeedbackRepository:
    """
    Repository for user feedback CRUD operations.
    """
    
    COLLECTION = "feedback"
    
    def __init__(self):
        self.db = get_firestore_client()
        self._in_memory_store = {}
    
    async def save(self, feedback_id: str, feedback_data: dict) -> dict:
        """Save user feedback."""
        now = datetime.utcnow().isoformat()
        
        document = {
            **feedback_data,
            "id": feedback_id,
            "createdAt": now,
        }
        
        if self.db:
            try:
                doc_ref = self.db.collection(self.COLLECTION).document(feedback_id)
                doc_ref.set(document)
                logger.info(f"Saved feedback {feedback_id} to Firestore")
            except Exception as e:
                logger.error(f"Failed to save feedback to Firestore: {e}")
                self._in_memory_store[feedback_id] = document
        else:
            self._in_memory_store[feedback_id] = document
            logger.info(f"Saved feedback {feedback_id} to in-memory store")
        
        return document
    
    async def get_by_plan(self, plan_id: str) -> list:
        """Get all feedback for a specific plan."""
        if self.db:
            try:
                query = (
                    self.db.collection(self.COLLECTION)
                    .where("planId", "==", plan_id)
                    .order_by("createdAt", direction="DESCENDING")
                )
                
                docs = query.stream()
                return [doc.to_dict() for doc in docs]
                
            except Exception as e:
                logger.error(f"Failed to get feedback from Firestore: {e}")
                return []
        else:
            return [
                fb for fb in self._in_memory_store.values()
                if fb.get("planId") == plan_id
            ]


# Singleton instances
study_plan_repo = StudyPlanRepository()
feedback_repo = FeedbackRepository()
