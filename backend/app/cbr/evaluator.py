"""
Model Evaluator Module
======================
Modul untuk mengevaluasi performa model CBR menggunakan Label-Based Classification.

Metodologi Evaluasi:
1. Split data menjadi training (case base) dan testing
2. Untuk setiap test case, cari K tetangga terdekat dari training set
3. Gunakan majority voting dari label K tetangga untuk prediksi
4. Bandingkan dengan label asli dan hitung metrik

Metrik yang dihitung:
- Accuracy
- Precision
- Recall
- F1-Score

Skenario Evaluasi:
- 70% Training - 30% Testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import json
import os
from collections import Counter
from pathlib import Path

from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    confusion_matrix as sklearn_confusion_matrix
)

from .weighted_euclidean import WeightedEuclideanDistance
from ..utils.data_loader import DataLoader
from ..utils.preprocessing import DataPreprocessor
from ..models.evaluation import (
    EvaluationMetrics, 
    ConfusionMatrixData, 
    EvaluationResult,
    EvaluationComparison
)
from ..config import settings

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Class untuk mengevaluasi performa model CBR.
    
    Metodologi Evaluasi (Label-Based Classification):
    1. Split data menjadi training (case base) dan testing
    2. Untuk setiap test case, cari K tetangga terdekat
    3. Gunakan majority voting untuk prediksi label
    4. Bandingkan dengan label asli dan hitung metrik
    
    Labels:
    - Gaming: HP untuk gaming
    - Photographer: HP untuk photography  
    - Daily: HP untuk penggunaan sehari-hari
    
    Example:
        >>> evaluator = ModelEvaluator()
        >>> results = evaluator.evaluate_all_scenarios()
        >>> print(results.best_scenario)
    """
    
    LABELS = ['Gaming', 'Photographer', 'Daily']
    
    def __init__(self, weights: Dict[str, float] = None, k: int = 5):
        """
        Inisialisasi evaluator.
        
        Args:
            weights: Bobot untuk perhitungan similarity
            k: Jumlah tetangga untuk majority voting
        """
        self.weights = weights or settings.DEFAULT_WEIGHTS.copy()
        self.k = k
        self.preprocessor = DataPreprocessor()
        self.distance_calculator = WeightedEuclideanDistance(self.weights)
        
        self.evaluation_results: List[EvaluationResult] = []
        
    def load_processed_data(self, scenario_name: str = "70-30") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load data training dan testing yang sudah diproses.
        
        Args:
            scenario_name: Nama skenario, contoh "70-30"
            
        Returns:
            Tuple (train_df, test_df)
        """
        # Path: backend/app/cbr/evaluator.py -> Final_Project/data/processed
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent  # Final_Project
        processed_dir = project_root / "data" / "processed"
        
        train_path = processed_dir / f"train_{scenario_name}.csv"
        test_path = processed_dir / f"test_{scenario_name}.csv"
        
        if not train_path.exists() or not test_path.exists():
            raise FileNotFoundError(
                f"Data files not found for scenario {scenario_name}. "
                f"Run prepare_data.py first."
            )
        
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        logger.info(f"Loaded {len(train_df)} training and {len(test_df)} testing samples")
        
        return train_df, test_df
    
    def extract_features(self, row: pd.Series, normalized_df: pd.DataFrame, idx: int) -> Dict[str, float]:
        """
        Extract feature vector dari row untuk distance calculation.
        
        Args:
            row: Pandas Series dengan data HP
            normalized_df: DataFrame yang sudah dinormalisasi
            idx: Index row
            
        Returns:
            Dictionary fitur yang sudah dinormalisasi
        """
        norm_row = normalized_df.loc[idx] if idx in normalized_df.index else normalized_df.iloc[0]
        
        feature_map = {
            'Harga': 'Harga_norm',
            'Ram': 'Ram_norm',
            'Memori_internal': 'Memori_internal_norm',
            'Kapasitas_baterai': 'Kapasitas_baterai_norm',
            'Ukuran_layar': 'Ukuran_layar_norm',
            'Rating_pengguna': 'Rating_pengguna_norm',
            'Resolusi_kamera_num': 'Resolusi_kamera_num_norm'
        }
        
        features = {}
        for weight_key, col_name in feature_map.items():
            if col_name in norm_row.index:
                val = norm_row.get(col_name, 0)
                features[weight_key] = float(val) if pd.notna(val) else 0.0
            else:
                # Fallback to original column
                orig_col = weight_key.replace('_num', '')
                if orig_col in norm_row.index:
                    val = norm_row.get(orig_col, 0)
                    features[weight_key] = float(val) if pd.notna(val) else 0.0
        
        return features
    
    def predict_label(
        self, 
        query_features: Dict[str, float],
        train_df: pd.DataFrame,
        train_normalized: pd.DataFrame
    ) -> str:
        """
        Prediksi label menggunakan majority voting dari K tetangga terdekat.
        
        Args:
            query_features: Fitur query yang sudah dinormalisasi
            train_df: DataFrame training (dengan label asli)
            train_normalized: DataFrame training yang sudah dinormalisasi
            
        Returns:
            Label prediksi (Gaming/Photographer/Daily)
        """
        similarities = []
        
        for idx in train_df.index:
            case_features = self.extract_features(train_df.loc[idx], train_normalized, idx)
            
            # Calculate similarity
            similarity = self.distance_calculator.calculate_similarity(
                query_features, 
                case_features
            )
            
            # Get original label
            label = train_df.loc[idx, 'Label']
            similarities.append((idx, similarity, label))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k neighbors
        top_k = similarities[:self.k]
        
        # Majority voting
        labels = [item[2] for item in top_k]
        label_counts = Counter(labels)
        predicted_label = label_counts.most_common(1)[0][0]
        
        return predicted_label
    
    def evaluate_scenario(
        self, 
        train_ratio: float = 0.7,
        similarity_threshold: float = 0.5,
        random_state: int = 42
    ) -> EvaluationResult:
        """
        Evaluasi model dengan skenario train-test split tertentu.
        
        Args:
            train_ratio: Rasio data training (contoh: 0.7 untuk 70%)
            similarity_threshold: Threshold (tidak digunakan dalam label-based)
            random_state: Seed untuk reproducibility
            
        Returns:
            EvaluationResult dengan metrik lengkap
        """
        scenario_name = f"{int(train_ratio * 100)}-{int((1-train_ratio) * 100)}"
        logger.info(f"Evaluating scenario: {scenario_name}")
        
        # Load processed data
        try:
            train_df, test_df = self.load_processed_data(scenario_name)
        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        
        # Fit preprocessor on training data
        self.preprocessor.fit(train_df)
        
        # Transform both datasets
        train_normalized = self.preprocessor.transform(train_df.copy())
        test_normalized = self.preprocessor.transform(test_df.copy())
        
        # Evaluate on test set
        y_true = []
        y_pred = []
        
        total = len(test_df)
        logger.info(f"Evaluating {total} test samples with K={self.k}")
        
        for i, idx in enumerate(test_df.index):
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
            
            # Extract features from test case
            query_features = self.extract_features(test_df.loc[idx], test_normalized, idx)
            
            # Predict using majority voting
            predicted = self.predict_label(query_features, train_df, train_normalized)
            
            # Get actual label
            actual = test_df.loc[idx, 'Label']
            
            y_true.append(actual)
            y_pred.append(predicted)
        
        logger.info(f"Evaluation completed: {total}/{total} (100%)")
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, labels=self.LABELS, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, labels=self.LABELS, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, labels=self.LABELS, average='weighted', zero_division=0)
        
        metrics = EvaluationMetrics(
            accuracy=round(accuracy, 4),
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            accuracy_pct=round(accuracy * 100, 2),
            precision_pct=round(precision * 100, 2),
            recall_pct=round(recall * 100, 2),
            f1_score_pct=round(f1 * 100, 2)
        )
        
        # Confusion matrix
        cm = sklearn_confusion_matrix(y_true, y_pred, labels=self.LABELS)
        cm_data = self._create_confusion_matrix_data(cm)
        
        # Create result
        result = EvaluationResult(
            scenario_name=scenario_name,
            train_size=len(train_df),
            test_size=len(test_df),
            train_percentage=train_ratio * 100,
            test_percentage=(1 - train_ratio) * 100,
            metrics=metrics,
            confusion_matrix=cm_data,
            evaluation_time=datetime.now().isoformat(),
            weights_used=self.weights
        )
        
        self.evaluation_results.append(result)
        
        logger.info(f"Scenario {scenario_name} - Accuracy: {metrics.accuracy_pct:.2f}%, F1: {metrics.f1_score_pct:.2f}%")
        
        return result
    
    def evaluate_all_scenarios(
        self,
        scenarios: List[Dict[str, int]] = None,
        similarity_threshold: float = 0.5
    ) -> EvaluationComparison:
        """
        Evaluasi semua skenario yang didefinisikan.
        
        Args:
            scenarios: List skenario, contoh: [{"train": 70, "test": 30}, ...]
            similarity_threshold: Threshold similarity
            
        Returns:
            EvaluationComparison dengan perbandingan semua skenario
        """
        if scenarios is None:
            scenarios = [
                {"train": 70, "test": 30}
            ]
        
        self.evaluation_results = []
        
        for scenario in scenarios:
            train_ratio = scenario["train"] / 100
            result = self.evaluate_scenario(
                train_ratio=train_ratio,
                similarity_threshold=similarity_threshold
            )
        
        # Find best scenario
        best_scenario = max(
            self.evaluation_results, 
            key=lambda x: x.metrics.f1_score
        )
        
        # Create comparison
        comparison = EvaluationComparison(
            scenarios=self.evaluation_results,
            best_scenario=best_scenario.scenario_name,
            comparison_summary=self._create_comparison_summary()
        )
        
        return comparison
    
    def _create_confusion_matrix_data(
        self, 
        cm: np.ndarray
    ) -> ConfusionMatrixData:
        """
        Membuat ConfusionMatrixData dari numpy array.
        
        Args:
            cm: Confusion matrix dari sklearn (3x3 untuk 3 labels)
            
        Returns:
            ConfusionMatrixData object
        """
        # For multi-class, we'll provide the full matrix
        # Calculate TP, FP, FN for the dominant class or weighted average
        
        # Sum of diagonal = total true positives
        tp = int(np.trace(cm))
        # Total samples
        total = int(np.sum(cm))
        # False predictions = total - true positives
        fp_fn = total - tp
        
        return ConfusionMatrixData(
            true_positives=tp,
            true_negatives=0,  # Not applicable for multi-class
            false_positives=fp_fn // 2,
            false_negatives=fp_fn // 2,
            matrix=cm.tolist(),
            labels=self.LABELS
        )
    
    def _create_comparison_summary(self) -> Dict:
        """
        Membuat ringkasan perbandingan antar skenario.
        
        Returns:
            Dictionary ringkasan
        """
        if not self.evaluation_results:
            return {}
        
        summary = {
            "total_scenarios": len(self.evaluation_results),
            "metrics_comparison": {}
        }
        
        for result in self.evaluation_results:
            summary["metrics_comparison"][result.scenario_name] = {
                "accuracy": result.metrics.accuracy_pct,
                "precision": result.metrics.precision_pct,
                "recall": result.metrics.recall_pct,
                "f1_score": result.metrics.f1_score_pct
            }
        
        # Calculate averages
        avg_accuracy = np.mean([r.metrics.accuracy_pct for r in self.evaluation_results])
        avg_f1 = np.mean([r.metrics.f1_score_pct for r in self.evaluation_results])
        
        summary["average_metrics"] = {
            "accuracy": round(avg_accuracy, 2),
            "f1_score": round(avg_f1, 2)
        }
        
        return summary
    
    def generate_visualization_data(self) -> Dict:
        """
        Generate data untuk visualisasi di frontend.
        
        Returns:
            Dictionary berisi data untuk charts
        """
        if not self.evaluation_results:
            return {}
        
        data = {
            "bar_chart": {
                "labels": [r.scenario_name for r in self.evaluation_results],
                "datasets": [
                    {
                        "label": "Accuracy",
                        "data": [r.metrics.accuracy_pct for r in self.evaluation_results]
                    },
                    {
                        "label": "Precision",
                        "data": [r.metrics.precision_pct for r in self.evaluation_results]
                    },
                    {
                        "label": "Recall",
                        "data": [r.metrics.recall_pct for r in self.evaluation_results]
                    },
                    {
                        "label": "F1-Score",
                        "data": [r.metrics.f1_score_pct for r in self.evaluation_results]
                    }
                ]
            },
            "confusion_matrices": [
                {
                    "scenario": r.scenario_name,
                    "matrix": r.confusion_matrix.matrix,
                    "labels": r.confusion_matrix.labels
                }
                for r in self.evaluation_results
            ],
            "radar_chart": {
                "labels": ["Accuracy", "Precision", "Recall", "F1-Score"],
                "datasets": [
                    {
                        "label": r.scenario_name,
                        "data": [
                            r.metrics.accuracy_pct,
                            r.metrics.precision_pct,
                            r.metrics.recall_pct,
                            r.metrics.f1_score_pct
                        ]
                    }
                    for r in self.evaluation_results
                ]
            }
        }
        
        return data
    
    def export_results(self, output_dir: str = None) -> str:
        """
        Export hasil evaluasi ke file JSON.
        
        Args:
            output_dir: Directory untuk output
            
        Returns:
            Path ke file output
        """
        if output_dir is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent  # Final_Project
            output_dir = project_root / "outputs"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "evaluation_results.json"
        
        results = {
            "evaluation_date": datetime.now().isoformat(),
            "method": "Label-Based Classification with Majority Voting (K=5)",
            "weights_used": self.weights,
            "scenarios": [
                {
                    "name": r.scenario_name,
                    "train_size": r.train_size,
                    "test_size": r.test_size,
                    "metrics": {
                        "accuracy": r.metrics.accuracy_pct,
                        "precision": r.metrics.precision_pct,
                        "recall": r.metrics.recall_pct,
                        "f1_score": r.metrics.f1_score_pct
                    },
                    "confusion_matrix": r.confusion_matrix.matrix,
                    "labels": r.confusion_matrix.labels
                }
                for r in self.evaluation_results
            ],
            "visualization_data": self.generate_visualization_data()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results exported to: {output_file}")
        return str(output_file)


# Singleton instance
_evaluator: Optional[ModelEvaluator] = None

def get_evaluator() -> ModelEvaluator:
    """
    Factory function untuk mendapatkan evaluator instance.
    
    Returns:
        ModelEvaluator instance
    """
    global _evaluator
    
    if _evaluator is None:
        _evaluator = ModelEvaluator()
    
    return _evaluator
