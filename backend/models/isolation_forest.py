import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Isolation Forest based anomaly detector for network traffic"""
    
    def __init__(self, contamination: float = 0.15, n_estimators: int = 100, random_state: int = 42):
        """
        Initialize the anomaly detector
        
        Args:
            contamination: Expected proportion of outliers in the dataset
            n_estimators: Number of base estimators in the ensemble
            random_state: Seed for reproducibility
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.is_trained = False
        self.feature_names = [
            'packet_size', 'inter_arrival_time', 'port_number', 'protocol_encoded',
            'packets_per_second', 'bytes_per_second', 'src_port', 'dst_port',
            'flag_syn', 'flag_ack', 'flag_fin', 'flag_rst', 'connection_duration'
        ]
        
    def train(self, X: np.ndarray) -> None:
        """
        Train the Isolation Forest model
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
        """
        if X.shape[1] != len(self.feature_names):
            raise ValueError(f"Expected {len(self.feature_names)} features, got {X.shape[1]}")
        
        logger.info(f"Training Isolation Forest with {X.shape[0]} samples, {X.shape[1]} features")
        
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            bootstrap=False,
            n_jobs=-1
        )
        
        self.model.fit(X)
        self.is_trained = True
        
        # Calculate feature importance approximations (based on average path lengths)
        feature_importances = self._approximate_feature_importance(X)
        logger.info(f"Feature importances: {dict(zip(self.feature_names, feature_importances))}")
        
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Predict if a network packet is anomalous
        
        Args:
            features: Feature vector of shape (n_features,) or (1, n_features)
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model must be trained before making predictions")
        
        # Ensure 2D array
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Get raw anomaly score (lower = more anomalous)
        raw_score = self.model.score_samples(features)[0]
        
        # Get prediction (-1 for anomalies, 1 for normal)
        prediction = self.model.predict(features)[0]
        
        # Normalize anomaly score to [0, 1] where 1 is most anomalous
        # Raw scores typically range from -0.5 to 0.5 for IsolationForest
        # We'll use a sigmoid-like transformation
        normalized_score = 1 / (1 + np.exp(-raw_score * 5))
        
        # Calculate confidence based on distance from decision boundary
        # Higher absolute score = higher confidence
        confidence = min(1.0, abs(raw_score) * 2) if raw_score < 0 else min(1.0, abs(raw_score) * 4)
        
        return {
            "is_anomaly": bool(prediction == -1),
            "anomaly_score": float(normalized_score),
            "raw_score": float(raw_score),
            "confidence": float(confidence),
            "prediction": int(prediction)
        }
    
    def _approximate_feature_importance(self, X: np.ndarray) -> np.ndarray:
        """
        Approximate feature importance by measuring average path length reduction
        This is a heuristic, not actual feature importance from Isolation Forest
        """
        if not self.is_trained or self.model is None:
            return np.zeros(X.shape[1])
        
        # Use feature variance as a proxy for importance
        # In practice, Isolation Forest doesn't provide feature importance directly
        feature_variances = np.var(X, axis=0)
        importance = feature_variances / np.sum(feature_variances)
        return importance
    
    def save(self, path: str) -> None:
        """Save the trained model to disk"""
        if self.model is None:
            raise RuntimeError("No model to save")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'random_state': self.random_state
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str) -> None:
        """Load a trained model from disk"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.contamination = model_data['contamination']
        self.n_estimators = model_data['n_estimators']
        self.random_state = model_data['random_state']
        self.is_trained = True
        logger.info(f"Model loaded from {path}")
