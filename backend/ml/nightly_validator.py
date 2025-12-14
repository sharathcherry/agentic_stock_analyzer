"""
Nightly Validation Script.
Checks if yesterday's predictions were correct and updates Firestore.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.firebase_service import FirebaseService
from app.services.angel_one import AngelOneService


class PredictionValidator:
    """Validates predictions and calculates accuracy."""
    
    async def validate_yesterday_predictions(self):
        """
        Validate all PENDING predictions from yesterday.
        Check if the predictions were correct based on today's price.
        """
        print("🔍 Starting nightly prediction validation...")
        
        # Get all PENDING predictions
        pending_predictions = FirebaseService.get_predictions(status="PENDING", limit=1000)
        
        yesterday = datetime.now() - timedelta(days=1)
        validated_count = 0
        correct_count = 0
        
        for pred in pending_predictions:
            # Check if prediction is from yesterday or older
            pred_timestamp = pred.get("timestamp")
            
            if not pred_timestamp:
                continue
            
            # Convert Firestore timestamp to datetime
            pred_date = pred_timestamp.replace(tzinfo=None)
            
            # Skip if not from yesterday
            if pred_date.date() >= datetime.now().date():
                continue
            
            # Validate this prediction
            is_correct = await self._validate_prediction(pred)
            
            if is_correct is not None:
                status = "CORRECT" if is_correct else "INCORRECT"
                FirebaseService.update_prediction_status(
                    pred["id"],
                    status,
                    actual_price=pred.get("actual_price")
                )
                validated_count += 1
                if is_correct:
                    correct_count += 1
        
        accuracy = (correct_count / validated_count * 100) if validated_count > 0 else 0
        
        print(f"✅ Validation complete:")
        print(f"   Total validated: {validated_count}")
        print(f"   Correct: {correct_count}")
        print(f"   Accuracy: {accuracy:.2f}%")
        
        return {
            "validated": validated_count,
            "correct": correct_count,
            "accuracy": accuracy
        }
    
    async def _validate_prediction(self, prediction: Dict[str, Any]) -> bool:
        """
        Validate a single prediction.
        
        Logic:
        - BUY: Check if price increased
        - SELL: Check if price decreased
        - HOLD: Check if price stayed relatively stable
        
        Returns:
            True if prediction was correct, False otherwise, None if can't validate
        """
        symbol = prediction.get("symbol")
        verdict = prediction.get("verdict")
        predicted_price = prediction.get("current_price")
        
        if not all([symbol, verdict, predicted_price]):
            return None
        
        # Get current price
        try:
            current_price = AngelOneService.get_ltp(symbol, "NSE")
            if not current_price:
                return None
            
            # Calculate price change
            price_change_percent = ((current_price - predicted_price) / predicted_price) * 100
            
            # Update prediction with actual price
            prediction["actual_price"] = current_price
            
            # Validate based on verdict
            if verdict == "BUY":
                return price_change_percent > 1.0  # Price should have increased
            elif verdict == "SELL":
                return price_change_percent < -1.0  # Price should have decreased
            elif verdict == "HOLD":
                return abs(price_change_percent) < 2.0  # Price should be stable
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error validating prediction {prediction.get('id')}: {e}")
            return None


async def main():
    """Main entry point for nightly validation."""
    validator = PredictionValidator()
    await validator.validate_yesterday_predictions()


if __name__ == "__main__":
    asyncio.run(main())
