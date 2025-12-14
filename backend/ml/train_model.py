"""
XGBoost Model Training Script.
Trains a predictive model based on historical prediction accuracy.
"""
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
from datetime import datetime

from app.services.firebase_service import FirebaseService


class StockPredictorModel:
    """XGBoost-based stock prediction model."""
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'rsi',
            'sma_20',
            'sma_50',
            'macd',
            'volume_ratio',
            'sentiment_polarity',
            'sentiment_confidence',
            'current_price'
        ]
    
    def prepare_training_data(self):
        """
        Fetch validated predictions from Firestore and prepare training data.
        
        Returns:
            X: Features (technical indicators + sentiment)
            y: Labels (0=SELL, 1=HOLD, 2=BUY)
        """
        print("📊 Fetching training data from Firestore...")
        
        # Get all CORRECT and INCORRECT predictions
        all_predictions = FirebaseService.get_predictions(limit=10000)
        
        # Filter only validated predictions
        validated_predictions = [
            p for p in all_predictions 
            if p.get('status') in ['CORRECT', 'INCORRECT']
        ]
        
        print(f"Found {len(validated_predictions)} validated predictions")
        
        if len(validated_predictions) < 50:
            print("⚠️ Not enough training data. Need at least 50 validated predictions.")
            return None, None
        
        # Convert to DataFrame
        data = []
        for pred in validated_predictions:
            try:
                features = self._extract_features(pred)
                label = self._verdict_to_label(pred.get('verdict'))
                
                if features and label is not None:
                    features['label'] = label
                    data.append(features)
            except Exception as e:
                print(f"Error processing prediction: {e}")
                continue
        
        if not data:
            print("❌ No valid training data after processing")
            return None, None
        
        df = pd.DataFrame(data)
        
        X = df[self.feature_columns]
        y = df['label']
        
        return X, y
    
    def _extract_features(self, prediction: dict) -> dict:
        """Extract features from a prediction document."""
        tech = prediction.get('technical_indicators', {})
        sentiment = prediction.get('news_sentiment', {})
        
        return {
            'rsi': tech.get('rsi', {}).get('value', 50),
            'sma_20': tech.get('sma', {}).get('sma_20', 0),
            'sma_50': tech.get('sma', {}).get('sma_50', 0),
            'macd': tech.get('macd', {}).get('macd', 0),
            'volume_ratio': tech.get('volume', {}).get('current', 0) / max(tech.get('volume', {}).get('average_20d', 1), 1),
            'sentiment_polarity': sentiment.get('average_polarity', 0),
            'sentiment_confidence': sentiment.get('confidence', 0),
            'current_price': prediction.get('current_price', 0)
        }
    
    def _verdict_to_label(self, verdict: str) -> int:
        """Convert verdict to numeric label."""
        mapping = {'SELL': 0, 'HOLD': 1, 'BUY': 2}
        return mapping.get(verdict)
    
    def train(self):
        """Train the XGBoost model."""
        print("🤖 Starting XGBoost model training...")
        
        X, y = self.prepare_training_data()
        
        if X is None or y is None:
            print("❌ Training aborted: insufficient data")
            return False
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train XGBoost
        self.model = xgb.XGBClassifier(
            objective='multi:softmax',
            num_class=3,
            max_depth=5,
            learning_rate=0.1,
            n_estimators=100,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Model trained successfully!")
        print(f"Accuracy: {accuracy * 100:.2f}%")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['SELL', 'HOLD', 'BUY']))
        
        # Save model
        self.save_model()
        
        return True
    
    def save_model(self, path: str = "models/xgboost_model.pkl"):
        """Save the trained model to disk."""
        import os
        os.makedirs("models", exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"💾 Model saved to {path}")
    
    def load_model(self, path: str = "models/xgboost_model.pkl"):
        """Load a trained model from disk."""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"📂 Model loaded from {path}")
    
    def predict(self, features: dict) -> str:
        """Make a prediction using the trained model."""
        if self.model is None:
            print("⚠️ Model not loaded")
            return "HOLD"
        
        # Prepare features
        X = pd.DataFrame([features])[self.feature_columns]
        
        # Predict
        label = self.model.predict(X)[0]
        
        # Convert back to verdict
        label_to_verdict = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
        return label_to_verdict.get(label, 'HOLD')


def main():
    """Train the model."""
    model = StockPredictorModel()
    model.train()


if __name__ == "__main__":
    main()
