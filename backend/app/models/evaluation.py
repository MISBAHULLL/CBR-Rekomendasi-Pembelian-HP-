"""
Pydantic models untuk hasil evaluasi CBR
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class EvaluationMetrics(BaseModel):
    """
    Metrik evaluasi untuk satu skenario training-testing.
    """
    accuracy: float = Field(..., ge=0, le=1.0, description="Akurasi model")
    precision: float = Field(..., ge=0, le=1.0, description="Presisi model")
    recall: float = Field(..., ge=0, le=1.0, description="Recall model")
    f1_score: float = Field(..., ge=0, le=1.0, description="F1-Score model")
    
    # Dalam persentase untuk display
    accuracy_pct: float = Field(..., ge=0, le=100, description="Akurasi dalam persen")
    precision_pct: float = Field(..., ge=0, le=100, description="Presisi dalam persen")
    recall_pct: float = Field(..., ge=0, le=100, description="Recall dalam persen")
    f1_score_pct: float = Field(..., ge=0, le=100, description="F1-Score dalam persen")
    
    class Config:
        json_schema_extra = {
            "example": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85,
                "accuracy_pct": 85.0,
                "precision_pct": 82.0,
                "recall_pct": 88.0,
                "f1_score_pct": 85.0
            }
        }


class ConfusionMatrixData(BaseModel):
    """
    Data confusion matrix untuk visualisasi.
    """
    true_positives: int = Field(..., ge=0, description="True Positives (TP)")
    true_negatives: int = Field(..., ge=0, description="True Negatives (TN)")
    false_positives: int = Field(..., ge=0, description="False Positives (FP)")
    false_negatives: int = Field(..., ge=0, description="False Negatives (FN)")
    
    # Matrix dalam format 2D untuk heatmap
    matrix: List[List[int]] = Field(..., description="Confusion matrix 2D")
    labels: List[str] = Field(default=["Tidak Relevan", "Relevan"], description="Label kelas")


class EvaluationResult(BaseModel):
    """
    Hasil evaluasi lengkap untuk satu skenario.
    """
    scenario_name: str = Field(..., description="Nama skenario (contoh: '70-30')")
    train_size: int = Field(..., ge=0, description="Jumlah data training")
    test_size: int = Field(..., ge=0, description="Jumlah data testing")
    train_percentage: float = Field(..., ge=0, le=100, description="Persentase training")
    test_percentage: float = Field(..., ge=0, le=100, description="Persentase testing")
    
    metrics: EvaluationMetrics = Field(..., description="Metrik evaluasi")
    confusion_matrix: ConfusionMatrixData = Field(..., description="Confusion matrix")
    
    # Metadata
    evaluation_time: str = Field(..., description="Waktu evaluasi dilakukan")
    weights_used: Dict[str, float] = Field(..., description="Bobot yang digunakan saat evaluasi")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_name": "70-30",
                "train_size": 700,
                "test_size": 300,
                "train_percentage": 70.0,
                "test_percentage": 30.0,
                "metrics": {
                    "accuracy": 0.85,
                    "precision": 0.82,
                    "recall": 0.88,
                    "f1_score": 0.85,
                    "accuracy_pct": 85.0,
                    "precision_pct": 82.0,
                    "recall_pct": 88.0,
                    "f1_score_pct": 85.0
                },
                "confusion_matrix": {
                    "true_positives": 120,
                    "true_negatives": 135,
                    "false_positives": 25,
                    "false_negatives": 20,
                    "matrix": [[135, 25], [20, 120]],
                    "labels": ["Tidak Relevan", "Relevan"]
                },
                "evaluation_time": "2024-12-08T23:50:00",
                "weights_used": {
                    "Harga": 25.0,
                    "Ram": 15.0
                }
            }
        }


class EvaluationComparison(BaseModel):
    """
    Perbandingan hasil evaluasi dari berbagai skenario.
    """
    scenarios: List[EvaluationResult] = Field(..., description="List hasil evaluasi tiap skenario")
    best_scenario: str = Field(..., description="Skenario terbaik berdasarkan F1-Score")
    comparison_summary: Dict = Field(..., description="Ringkasan perbandingan")
    
    # Path ke visualisasi jika ada
    confusion_matrix_plots: Optional[List[str]] = Field(None, description="Path gambar confusion matrix")
    metrics_comparison_plot: Optional[str] = Field(None, description="Path gambar perbandingan metrik")


class EvaluationRequest(BaseModel):
    """
    Request untuk menjalankan evaluasi.
    """
    scenarios: List[Dict[str, int]] = Field(
        default=[{"train": 70, "test": 30}, {"train": 80, "test": 20}],
        description="Skenario pembagian data"
    )
    custom_weights: Optional[Dict[str, float]] = Field(
        None,
        description="Bobot kustom untuk evaluasi"
    )
    similarity_threshold: float = Field(
        0.5,
        ge=0,
        le=1.0,
        description="Threshold untuk menentukan relevansi"
    )
