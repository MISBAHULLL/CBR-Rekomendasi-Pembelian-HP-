"""
Model Evaluator Module
======================
Modul untuk mengevaluasi performa model CBR.

Metrik yang dihitung:
- Accuracy
- Precision
- Recall
- F1-Score

Skenario Evaluasi:
- 70% Training - 30% Testing
- 80% Training - 20% Testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import json
import os

from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    confusion_matrix
)

from .cbr_engine import CBREngine
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
    
    Metodologi Evaluasi:
    1. Split data menjadi training (case base) dan testing
    2. Untuk setiap test case, cari recommenation dari training set
    3. Bandingkan apakah HP yang direkomendasikan "relevan"
    4. Hitung metrik evaluasi
    
    Kriteria Relevansi:
    - HP dengan similarity >= threshold dianggap relevan
    - Ground truth: HP dengan karakteristik serupa (brand, range harga, dll)
    
    Example:
        >>> evaluator = ModelEvaluator()
        >>> results = evaluator.evaluate_all_scenarios()
        >>> print(results.best_scenario)
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Inisialisasi evaluator.
        
        Args:
            weights: Bobot untuk perhitungan similarity
        """
        self.weights = weights or settings.DEFAULT_WEIGHTS.copy()
        self.data_loader: Optional[DataLoader] = None
        self.preprocessor = DataPreprocessor()
        self.full_dataset: Optional[pd.DataFrame] = None
        
        self.evaluation_results: List[EvaluationResult] = []
        
    def load_data(self, file_path: str = None) -> None:
        """
        Load dataset untuk evaluasi.
        
        Args:
            file_path: Path ke file dataset
        """
        file_path = file_path or settings.DATASET_PATH
        
        self.data_loader = DataLoader(file_path)
        self.full_dataset = self.data_loader.load()
        self.full_dataset = self.preprocessor.fit_transform(self.full_dataset)
        
        logger.info(f"Loaded {len(self.full_dataset)} samples for evaluation")
    
    def evaluate_scenario(
        self, 
        train_ratio: float,
        similarity_threshold: float = 0.5,
        random_state: int = 42
    ) -> EvaluationResult:
        """
        Evaluasi model dengan skenario train-test split tertentu.
        
        Args:
            train_ratio: Rasio data training (contoh: 0.7 untuk 70%)
            similarity_threshold: Threshold untuk menentukan relevansi
            random_state: Seed untuk reproducibility
            
        Returns:
            EvaluationResult dengan metrik lengkap
        """
        if self.full_dataset is None:
            self.load_data()
        
        scenario_name = f"{int(train_ratio * 100)}-{int((1-train_ratio) * 100)}"
        logger.info(f"Evaluating scenario: {scenario_name}")
        
        # Split data
        train_df, test_df = self.data_loader.split_train_test(
            train_ratio=train_ratio,
            random_state=random_state
        )
        
        # Initialize CBR engine dengan training data
        cbr_engine = CBREngine(self.weights)
        cbr_engine.case_base = train_df
        cbr_engine.case_base_normalized = self.preprocessor.transform(train_df)
        cbr_engine.preprocessor = self.preprocessor
        cbr_engine.is_initialized = True
        
        # Evaluate on test set
        y_true = []  # Ground truth labels
        y_pred = []  # Predicted labels
        
        for idx, test_case in test_df.iterrows():
            # Create query from test case
            query = self._create_query_from_case(test_case)
            
            # Get recommendation
            retrieved = cbr_engine.retrieve(query, top_k=5, min_similarity=0.1)
            
            # Determine ground truth (is there a similar phone in retrieved?)
            is_relevant = self._determine_relevance(test_case, retrieved, similarity_threshold)
            
            # Prediction: if top recommendation has high similarity, predict relevant
            if retrieved and retrieved[0][2] >= similarity_threshold:
                predicted_relevant = 1
            else:
                predicted_relevant = 0
            
            y_true.append(1 if is_relevant else 0)
            y_pred.append(predicted_relevant)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_true, y_pred)
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
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
                {"train": 70, "test": 30},
                {"train": 80, "test": 20}
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
    
    def _create_query_from_case(self, case: pd.Series) -> Dict:
        """
        Membuat query dari test case.
        
        Args:
            case: Test case sebagai pandas Series
            
        Returns:
            Query dictionary
        """
        return {
            'harga': case.get('Harga', 0),
            'ram': case.get('Ram', 0),
            'memori_internal': case.get('Memori_internal', 0),
            'kapasitas_baterai': case.get('Kapasitas_baterai', 0),
            'ukuran_layar': case.get('Ukuran_layar', 0),
            'rating': case.get('Rating_pengguna', 0)
        }
    
    def _determine_relevance(
        self, 
        test_case: pd.Series, 
        retrieved: List, 
        threshold: float
    ) -> bool:
        """
        Menentukan apakah retrieved cases relevan dengan test case.
        
        Kriteria relevansi:
        - Similarity score >= threshold
        - Brand, price range, atau spec yang serupa
        
        Args:
            test_case: Test case
            retrieved: Retrieved cases
            threshold: Similarity threshold
            
        Returns:
            True jika ada case yang relevan
        """
        if not retrieved:
            return False
        
        for idx, case, similarity in retrieved:
            if similarity >= threshold:
                # Additional check: similar price range (within 30%)
                test_price = test_case.get('Harga', 0)
                case_price = case.get('Harga', 0)
                
                if test_price > 0 and case_price > 0:
                    price_diff = abs(test_price - case_price) / test_price
                    if price_diff <= 0.3:  # Within 30%
                        return True
                
                # Or same brand with similar specs
                if test_case.get('Brand') == case.get('Brand'):
                    return True
        
        # If top similarity is high enough, consider relevant
        if retrieved[0][2] >= threshold:
            return True
            
        return False
    
    def _calculate_metrics(
        self, 
        y_true: List[int], 
        y_pred: List[int]
    ) -> EvaluationMetrics:
        """
        Menghitung metrik evaluasi.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            
        Returns:
            EvaluationMetrics object
        """
        # Handle edge cases
        if len(set(y_true)) == 1 or len(set(y_pred)) == 1:
            # All same class
            acc = accuracy_score(y_true, y_pred)
            return EvaluationMetrics(
                accuracy=acc,
                precision=acc,
                recall=acc,
                f1_score=acc,
                accuracy_pct=acc * 100,
                precision_pct=acc * 100,
                recall_pct=acc * 100,
                f1_score_pct=acc * 100
            )
        
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        return EvaluationMetrics(
            accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
            accuracy_pct=round(acc * 100, 2),
            precision_pct=round(prec * 100, 2),
            recall_pct=round(rec * 100, 2),
            f1_score_pct=round(f1 * 100, 2)
        )
    
    def _create_confusion_matrix_data(
        self, 
        cm: np.ndarray
    ) -> ConfusionMatrixData:
        """
        Membuat ConfusionMatrixData dari numpy array.
        
        Args:
            cm: Confusion matrix dari sklearn
            
        Returns:
            ConfusionMatrixData object
        """
        # Handle different matrix sizes
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            # Single class case
            tn, fp, fn, tp = 0, 0, 0, cm[0][0]
        
        return ConfusionMatrixData(
            true_positives=int(tp),
            true_negatives=int(tn),
            false_positives=int(fp),
            false_negatives=int(fn),
            matrix=cm.tolist(),
            labels=["Tidak Relevan", "Relevan"]
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
            output_dir = os.path.dirname(settings.DATASET_PATH)
        
        output_file = os.path.join(output_dir, "evaluation_results.json")
        
        results = {
            "evaluation_date": datetime.now().isoformat(),
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
                    "confusion_matrix": r.confusion_matrix.matrix
                }
                for r in self.evaluation_results
            ],
            "visualization_data": self.generate_visualization_data()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results exported to: {output_file}")
        return output_file


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
