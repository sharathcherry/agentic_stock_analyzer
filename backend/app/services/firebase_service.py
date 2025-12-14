"""
Firebase Admin SDK Service for Firestore operations.
Handles initialization and database operations for predictions, user data, and agent memory.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.config import settings


class FirebaseService:
    """Service class for Firebase Firestore operations."""
    
    _initialized = False
    _db = None
    _available = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK (call once at startup)."""
        if cls._initialized:
            return
            
        cls._initialized = True
        
        try:
            import os
            service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_PATH', './serviceAccountKey.json')
            
            if not os.path.exists(service_account_path):
                print(f"⚠️ Firebase service account not found at {service_account_path}")
                print("   Firebase features will be disabled. Predictions will not be saved.")
                cls._available = False
                return
                
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            cls._db = firestore.client()
            cls._available = True
            print("✅ Firebase initialized successfully")
        except Exception as e:
            print(f"⚠️ Firebase initialization skipped: {e}")
            cls._available = False
    
    @classmethod
    def get_db(cls):
        """Get Firestore database instance."""
        if not cls._initialized:
            cls.initialize()
        if not cls._available:
            return None
        return cls._db
    
    @staticmethod
    def save_prediction(
        symbol: str,
        prediction_data: Dict[str, Any]
    ) -> str:
        """
        Save a stock prediction to Firestore.
        
        Args:
            symbol: Stock symbol (e.g., 'TATAMOTORS')
            prediction_data: Dictionary containing prediction details
            
        Returns:
            Document ID of the saved prediction
        """
        db = FirebaseService.get_db()
        
        if db is None:
            print(f"⚠️ Firebase not available - prediction not saved for {symbol}")
            return None
        
        # Prepare prediction document
        prediction_doc = {
            "symbol": symbol,
            "timestamp": datetime.utcnow(),
            "status": "PENDING",  # PENDING, CORRECT, INCORRECT
            "verdict": prediction_data.get("verdict", "HOLD"),
            "explanation": prediction_data.get("explanation", ""),
            "confidence": prediction_data.get("confidence", 0.0),
            "current_price": prediction_data.get("current_price", 0.0),
            "target_price": prediction_data.get("target_price", None),
            "technical_indicators": prediction_data.get("technical_indicators", {}),
            "news_sentiment": prediction_data.get("news_sentiment", {}),
            "ai_reasoning": prediction_data.get("ai_reasoning", ""),
        }
        
        # Save to 'predictions' collection
        doc_ref = db.collection("predictions").add(prediction_doc)
        prediction_id = doc_ref[1].id
        
        print(f"✅ Prediction saved: {prediction_id} for {symbol}")
        return prediction_id
    
    @staticmethod
    def get_predictions(
        symbol: Optional[str] = None,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve predictions from Firestore.
        
        Args:
            symbol: Filter by stock symbol (optional)
            limit: Maximum number of predictions to retrieve
            status: Filter by status (PENDING, CORRECT, INCORRECT)
            
        Returns:
            List of prediction documents
        """
        db = FirebaseService.get_db()
        
        if db is None:
            return []
            
        query = db.collection("predictions")
        
        # Apply filters
        if symbol:
            query = query.where("symbol", "==", symbol)
        if status:
            query = query.where("status", "==", status)
        
        # Order by timestamp (most recent first) and limit
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        
        # Execute query
        docs = query.stream()
        predictions = []
        
        for doc in docs:
            pred_data = doc.to_dict()
            pred_data["id"] = doc.id
            predictions.append(pred_data)
        
        return predictions
    
    @staticmethod
    def update_prediction_status(
        prediction_id: str,
        status: str,
        actual_price: Optional[float] = None
    ) -> bool:
        """
        Update the status of a prediction after validation.
        
        Args:
            prediction_id: Document ID of the prediction
            status: New status (CORRECT, INCORRECT)
            actual_price: The actual price observed (optional)
            
        Returns:
            True if update was successful
        """
        db = FirebaseService.get_db()
        
        try:
            update_data = {
                "status": status,
                "validated_at": datetime.utcnow()
            }
            
            if actual_price is not None:
                update_data["actual_price"] = actual_price
            
            db.collection("predictions").document(prediction_id).update(update_data)
            print(f"✅ Prediction {prediction_id} updated to {status}")
            return True
        except Exception as e:
            print(f"❌ Error updating prediction: {e}")
            return False
    
    @staticmethod
    def save_user_watchlist(
        user_id: str,
        symbols: List[str]
    ) -> bool:
        """
        Save or update a user's watchlist.
        
        Args:
            user_id: Firebase Auth user ID
            symbols: List of stock symbols
            
        Returns:
            True if save was successful
        """
        db = FirebaseService.get_db()
        
        try:
            watchlist_doc = {
                "user_id": user_id,
                "symbols": symbols,
                "updated_at": datetime.utcnow()
            }
            
            db.collection("watchlists").document(user_id).set(
                watchlist_doc, 
                merge=True
            )
            print(f"✅ Watchlist saved for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving watchlist: {e}")
            return False
    
    @staticmethod
    def get_user_watchlist(user_id: str) -> List[str]:
        """
        Retrieve a user's watchlist.
        
        Args:
            user_id: Firebase Auth user ID
            
        Returns:
            List of stock symbols
        """
        db = FirebaseService.get_db()
        
        try:
            doc = db.collection("watchlists").document(user_id).get()
            if doc.exists:
                return doc.to_dict().get("symbols", [])
            return []
        except Exception as e:
            print(f"❌ Error retrieving watchlist: {e}")
            return []


# Initialize Firebase when module is imported
FirebaseService.initialize()
