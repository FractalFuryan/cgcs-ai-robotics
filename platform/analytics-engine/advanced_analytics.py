"""
Advanced Analytics Engine with ML for predictive safety

This module provides machine learning-powered analytics for the Linear C platform,
including predictive safety modeling, anomaly detection, and fleet pattern analysis.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging
from dataclasses import dataclass, asdict
import asyncio

# Optional ML dependencies with graceful fallback
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("scikit-learn not installed, ML features will be limited")

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logging.warning("XGBoost not installed, using fallback predictor")

logger = logging.getLogger(__name__)

@dataclass
class SafetyPrediction:
    """Safety prediction result"""
    robot_id: str
    prediction: str  # "safe", "warning", "danger"
    confidence: float
    risk_factors: List[str]
    recommended_action: str
    time_horizon_minutes: int

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    robot_id: str
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    features_contributing: List[str]
    severity: str

class AdvancedAnalyticsEngine:
    """
    Advanced analytics with ML for predictive safety and anomaly detection
    """
    def __init__(self, storage_backend=None):
        self.storage = storage_backend
        
        # ML Models (lazy initialization)
        self.predictive_model = None
        self.anomaly_model = None
        self.clustering_model = None
        
        # Scaler
        if HAS_SKLEARN:
            self.scaler = StandardScaler()
        else:
            self.scaler = None
        
        # Feature store
        self.feature_store: Dict[str, List] = {}
        
        # Initialize models
        if HAS_SKLEARN or HAS_XGBOOST:
            self.initialize_models()
    
    def initialize_models(self):
        """Initialize ML models"""
        try:
            # Predictive model for safety violations
            if HAS_XGBOOST:
                self.predictive_model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    objective='binary:logistic',
                    random_state=42
                )
            elif HAS_SKLEARN:
                self.predictive_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=6,
                    random_state=42
                )
            
            # Anomaly detection model
            if HAS_SKLEARN:
                self.anomaly_model = IsolationForest(
                    n_estimators=100,
                    contamination=0.1,
                    random_state=42
                )
            
            # Clustering model for pattern discovery
            if HAS_SKLEARN:
                self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
                
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    async def predict_safety_risk(self, robot_id: str, features: Dict) -> SafetyPrediction:
        """Predict safety risk for a robot"""
        # Simple rule-based prediction if ML not available
        if not self.predictive_model or not HAS_SKLEARN:
            return self._rule_based_prediction(robot_id, features)
        
        try:
            # Convert features to DataFrame
            feature_df = pd.DataFrame([features])
            
            # Scale features
            feature_scaled = self.scaler.transform(feature_df)
            
            # Make prediction
            prediction_proba = self.predictive_model.predict_proba(feature_scaled)[0]
            prediction_class = self.predictive_model.predict(feature_scaled)[0]
            
            # Determine risk level
            if prediction_proba[1] > 0.7:  # High probability of violation
                risk_level = "danger"
                confidence = prediction_proba[1]
            elif prediction_proba[1] > 0.3:
                risk_level = "warning"
                confidence = prediction_proba[1]
            else:
                risk_level = "safe"
                confidence = prediction_proba[0]
            
            # Identify risk factors
            risk_factors = self.identify_risk_factors(features)
            
            # Recommend action
            recommended_action = self.recommend_action(risk_level, risk_factors)
            
            return SafetyPrediction(
                robot_id=robot_id,
                prediction=risk_level,
                confidence=confidence,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                time_horizon_minutes=60  # Predict next hour
            )
        except Exception as e:
            logger.error(f"ML prediction failed: {e}, using rule-based fallback")
            return self._rule_based_prediction(robot_id, features)
    
    def _rule_based_prediction(self, robot_id: str, features: Dict) -> SafetyPrediction:
        """Simple rule-based prediction without ML"""
        risk_factors = self.identify_risk_factors(features)
        
        # Determine risk level based on risk factors
        if len(risk_factors) >= 3:
            risk_level = "danger"
            confidence = 0.9
        elif len(risk_factors) >= 1:
            risk_level = "warning"
            confidence = 0.7
        else:
            risk_level = "safe"
            confidence = 0.95
        
        recommended_action = self.recommend_action(risk_level, risk_factors)
        
        return SafetyPrediction(
            robot_id=robot_id,
            prediction=risk_level,
            confidence=confidence,
            risk_factors=risk_factors,
            recommended_action=recommended_action,
            time_horizon_minutes=60
        )
    
    async def detect_anomalies(self, robot_id: str, recent_data: List[Dict]) -> AnomalyDetection:
        """Detect anomalies in robot behavior"""
        if not self.anomaly_model or not HAS_SKLEARN or not recent_data:
            return self._rule_based_anomaly_detection(robot_id, recent_data)
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(recent_data)
            
            # Extract features for anomaly detection
            features = self.extract_anomaly_features(df)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_model.decision_function(features_scaled)
            anomaly_predictions = self.anomaly_model.predict(features_scaled)
            
            # Most recent prediction
            is_anomaly = anomaly_predictions[-1] == -1
            anomaly_score = abs(anomaly_scores[-1])
            
            # Determine anomaly type
            anomaly_type = self.classify_anomaly_type(recent_data[-1])
            
            # Get contributing features
            contributing_features = self.get_contributing_features(
                recent_data[-1], 
                features_scaled[-1]
            )
            
            # Determine severity
            severity = "high" if anomaly_score > 0.7 else "medium" if anomaly_score > 0.4 else "low"
            
            return AnomalyDetection(
                robot_id=robot_id,
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                anomaly_type=anomaly_type,
                features_contributing=contributing_features,
                severity=severity
            )
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}, using rule-based fallback")
            return self._rule_based_anomaly_detection(robot_id, recent_data)
    
    def _rule_based_anomaly_detection(self, robot_id: str, recent_data: List[Dict]) -> AnomalyDetection:
        """Simple rule-based anomaly detection"""
        if not recent_data:
            return AnomalyDetection(
                robot_id=robot_id,
                is_anomaly=False,
                anomaly_score=0.0,
                anomaly_type="none",
                features_contributing=[],
                severity="low"
            )
        
        # Check for anomalies based on simple rules
        latest = recent_data[-1]
        
        # High violation rate
        violation_rate = sum(1 for d in recent_data if not d.get('is_valid', True)) / len(recent_data)
        
        is_anomaly = violation_rate > 0.5
        anomaly_score = violation_rate
        anomaly_type = "high_violation_rate" if is_anomaly else "normal"
        severity = "high" if violation_rate > 0.7 else "medium" if violation_rate > 0.5 else "low"
        
        contributing_features = []
        if is_anomaly:
            contributing_features.append(f"Violation rate: {violation_rate:.1%}")
        
        return AnomalyDetection(
            robot_id=robot_id,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            anomaly_type=anomaly_type,
            features_contributing=contributing_features,
            severity=severity
        )
    
    async def generate_safety_report(self, robot_data: List[Dict], time_period: str = "daily") -> Dict:
        """Generate comprehensive safety report"""
        # Calculate metrics
        metrics = self.calculate_safety_metrics(robot_data)
        
        # Identify trends
        trends = self.identify_safety_trends(robot_data)
        
        # Generate insights
        insights = self.generate_safety_insights(metrics, trends)
        
        # Create recommendations
        recommendations = self.generate_recommendations(insights)
        
        return {
            'period': time_period,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics,
            'trends': trends,
            'insights': insights,
            'recommendations': recommendations
        }
    
    def identify_risk_factors(self, features: Dict) -> List[str]:
        """Identify key risk factors from features"""
        risk_factors = []
        
        # Check various risk indicators
        if features.get('velocity', 0) > 1.0:
            risk_factors.append("High velocity")
        
        if features.get('proximity_to_human', float('inf')) < 0.5:
            risk_factors.append("Close human proximity")
        
        if features.get('battery_level', 100) < 20:
            risk_factors.append("Low battery")
        
        if features.get('violation_count_1h', 0) > 3:
            risk_factors.append("Multiple recent violations")
        
        if features.get('cpu_temperature', 40) > 70:
            risk_factors.append("High CPU temperature")
        
        if features.get('avg_response_time', 0) > 100:
            risk_factors.append("Slow response time")
        
        return risk_factors
    
    def recommend_action(self, risk_level: str, risk_factors: List[str]) -> str:
        """Recommend action based on risk level"""
        if risk_level == "danger":
            return "Immediate safety intervention required. Consider emergency stop."
        elif risk_level == "warning":
            if "High velocity" in risk_factors:
                return "Reduce speed and increase monitoring."
            elif "Close human proximity" in risk_factors:
                return "Increase safe distance from humans."
            elif "Multiple recent violations" in risk_factors:
                return "Review safety logs and retrain safety patterns."
            else:
                return "Increase monitoring frequency and review safety logs."
        else:
            return "Continue normal operation with routine monitoring."
    
    def extract_anomaly_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = []
        
        # Statistical features
        if 'validation_time_ms' in data.columns:
            features.append(data['validation_time_ms'].mean())
            features.append(data['validation_time_ms'].std())
        else:
            features.extend([0.0, 0.0])
        
        if 'is_valid' in data.columns:
            valid_rate = data['is_valid'].astype(int).mean()
            violation_count = len(data[data['is_valid'] == False])
            features.append(valid_rate)
            features.append(violation_count)
        else:
            features.extend([1.0, 0.0])
        
        # Temporal features
        if 'timestamp' in data.columns:
            try:
                time_diffs = pd.to_datetime(data['timestamp']).diff().dt.total_seconds().fillna(0)
                features.append(time_diffs.mean())
                features.append(time_diffs.std())
            except:
                features.extend([0.0, 0.0])
        else:
            features.extend([0.0, 0.0])
        
        return np.array(features).reshape(1, -1)
    
    def classify_anomaly_type(self, data_point: Dict) -> str:
        """Classify type of anomaly"""
        if data_point.get('validation_time_ms', 0) > 100:
            return "Slow validation response"
        elif not data_point.get('is_valid', True):
            return "Safety violation pattern"
        elif 'proximity' in data_point and data_point['proximity'] < 0.2:
            return "Critical proximity"
        else:
            return "Behavioral anomaly"
    
    def get_contributing_features(self, data_point: Dict, scaled_features: np.ndarray) -> List[str]:
        """Get features contributing to anomaly"""
        contributing = []
        feature_names = ['avg_response', 'response_std', 'valid_rate', 'violation_count', 'time_diff_mean', 'time_diff_std']
        
        # Identify features far from mean (z-score > 2)
        for i, (name, value) in enumerate(zip(feature_names, scaled_features)):
            if i < len(scaled_features) and abs(value) > 2:
                contributing.append(f"{name} (z-score: {value:.2f})")
        
        return contributing
    
    def calculate_safety_metrics(self, data: List[Dict]) -> Dict:
        """Calculate safety metrics"""
        if not data:
            return {
                'total_validations': 0,
                'violations': 0,
                'violation_rate': 0.0,
                'avg_response_time_ms': 0.0
            }
        
        validations = len(data)
        violations = sum(1 for d in data if not d.get('is_valid', True))
        violation_rate = violations / validations if validations > 0 else 0.0
        
        response_times = [float(d.get('validation_time_ms', 0)) for d in data]
        avg_response_time = np.mean(response_times) if response_times else 0.0
        
        metrics = {
            'total_validations': validations,
            'violations': violations,
            'violation_rate': violation_rate,
            'avg_response_time_ms': avg_response_time,
            'p95_response_time_ms': np.percentile(response_times, 95) if response_times else 0.0
        }
        
        return metrics
    
    def identify_safety_trends(self, data: List[Dict]) -> Dict:
        """Identify safety trends"""
        if not data or len(data) < 2:
            return {
                'violation_trend': 'stable',
                'response_time_trend': 'stable'
            }
        
        # Split data into first and second half
        mid = len(data) // 2
        first_half = data[:mid]
        second_half = data[mid:]
        
        # Calculate violation rates
        first_violations = sum(1 for d in first_half if not d.get('is_valid', True)) / len(first_half)
        second_violations = sum(1 for d in second_half if not d.get('is_valid', True)) / len(second_half)
        
        violation_trend = 'increasing' if second_violations > first_violations * 1.2 else 'decreasing' if second_violations < first_violations * 0.8 else 'stable'
        
        # Calculate response time trends
        first_rt = np.mean([float(d.get('validation_time_ms', 0)) for d in first_half])
        second_rt = np.mean([float(d.get('validation_time_ms', 0)) for d in second_half])
        
        response_time_trend = 'increasing' if second_rt > first_rt * 1.2 else 'decreasing' if second_rt < first_rt * 0.8 else 'stable'
        
        return {
            'violation_trend': violation_trend,
            'response_time_trend': response_time_trend
        }
    
    def generate_safety_insights(self, metrics: Dict, trends: Dict) -> List[Dict]:
        """Generate safety insights"""
        insights = []
        
        # High violation rate insight
        if metrics.get('violation_rate', 0) > 0.1:
            insights.append({
                'type': 'high_risk',
                'title': 'High violation rate detected',
                'description': f"Violation rate is {metrics['violation_rate']*100:.1f}%, above 10% threshold",
                'severity': 'high',
                'recommendation': 'Review safety patterns and consider adding new constraints'
            })
        
        # Slow response time insight
        if metrics.get('p95_response_time_ms', 0) > 50:
            insights.append({
                'type': 'performance',
                'title': 'Slow validation response times',
                'description': f"95th percentile response time is {metrics['p95_response_time_ms']:.1f}ms",
                'severity': 'medium',
                'recommendation': 'Optimize validation patterns or scale resources'
            })
        
        # Increasing trend insight
        if trends.get('violation_trend') == 'increasing':
            insights.append({
                'type': 'trend',
                'title': 'Increasing violation trend',
                'description': 'Violations are increasing over time',
                'severity': 'medium',
                'recommendation': 'Investigate root causes and consider safety protocol review'
            })
        
        # Positive insights
        if metrics.get('violation_rate', 0) < 0.01:
            insights.append({
                'type': 'positive',
                'title': 'Excellent safety performance',
                'description': f"Violation rate is only {metrics['violation_rate']*100:.2f}%",
                'severity': 'info',
                'recommendation': 'Maintain current safety practices'
            })
        
        return insights
    
    def generate_recommendations(self, insights: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for insight in insights:
            if insight['severity'] == 'high':
                priority = 'immediate'
            elif insight['severity'] == 'medium':
                priority = 'soon'
            else:
                priority = 'when_convenient'
            
            recommendations.append({
                'insight_id': insight.get('type', 'unknown'),
                'priority': priority,
                'action': insight['recommendation'],
                'estimated_effort': 'medium',
                'expected_impact': 'high' if insight['severity'] == 'high' else 'medium'
            })
        
        return recommendations
    
    async def update_feature_store(self, robot_id: str, validation: Dict):
        """Update feature store with new validation"""
        if robot_id not in self.feature_store:
            self.feature_store[robot_id] = []
        
        self.feature_store[robot_id].append(validation)
        
        # Keep only last 1000 entries
        if len(self.feature_store[robot_id]) > 1000:
            self.feature_store[robot_id] = self.feature_store[robot_id][-1000:]
    
    def get_current_features(self, robot_id: str) -> Dict:
        """Get current features for a robot"""
        if robot_id not in self.feature_store or len(self.feature_store[robot_id]) < 10:
            return {
                'velocity': 0.0,
                'proximity_to_human': 1.0,
                'battery_level': 100.0,
                'violation_count_1h': 0,
                'cpu_temperature': 40.0,
                'avg_response_time': 5.0,
                'validity_rate': 1.0
            }
        
        recent_data = self.feature_store[robot_id][-10:]
        
        features = {
            'velocity': 0.0,  # Would come from robot state
            'proximity_to_human': 1.0,  # Would come from sensors
            'battery_level': 100.0,  # Would come from power system
            'violation_count_1h': sum(1 for v in recent_data if not v.get('is_valid', True)),
            'cpu_temperature': 40.0,  # Would come from system monitoring
            'avg_response_time': np.mean([float(v.get('validation_time_ms', 0)) for v in recent_data]),
            'validity_rate': sum(1 for v in recent_data if v.get('is_valid', True)) / len(recent_data)
        }
        
        return features


# Standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create analytics engine
    engine = AdvancedAnalyticsEngine()
    
    # Test with sample data
    sample_features = {
        'velocity': 0.5,
        'proximity_to_human': 1.5,
        'battery_level': 85.0,
        'violation_count_1h': 1,
        'cpu_temperature': 45.0,
        'avg_response_time': 10.0,
        'validity_rate': 0.95
    }
    
    # Test prediction
    import asyncio
    
    async def test():
        prediction = await engine.predict_safety_risk("test-robot-001", sample_features)
        print("Safety Prediction:")
        print(f"  Robot: {prediction.robot_id}")
        print(f"  Risk Level: {prediction.prediction}")
        print(f"  Confidence: {prediction.confidence:.2%}")
        print(f"  Risk Factors: {', '.join(prediction.risk_factors) or 'None'}")
        print(f"  Recommended Action: {prediction.recommended_action}")
    
    asyncio.run(test())
