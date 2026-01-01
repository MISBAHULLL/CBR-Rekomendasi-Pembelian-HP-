"""
API endpoints untuk evaluasi model CBR
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..cbr import get_evaluator
from ..models.evaluation import EvaluationRequest

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


class EvaluationConfig(BaseModel):
    """Konfigurasi untuk menjalankan evaluasi."""
    scenarios: List[Dict[str, int]] = Field(
        default=[
            {"train": 70, "test": 30}
        ],
        description="Skenario train-test split (70% training, 30% testing)"
    )
    similarity_threshold: float = Field(
        default=0.5,
        ge=0,
        le=1.0,
        description="Threshold untuk menentukan relevansi"
    )
    custom_weights: Optional[Dict[str, float]] = Field(
        None,
        description="Bobot kustom untuk evaluasi"
    )


@router.post("/run", response_model=Dict)
async def run_evaluation(config: EvaluationConfig) -> Dict:
    """
    Menjalankan evaluasi model CBR.
    
    Evaluasi dilakukan dengan skenario yang ditentukan:
    - Default: 70-30 dan 80-20 split
    
    Metrik yang dihitung:
    - Accuracy
    - Precision
    - Recall
    - F1-Score
    
    Returns:
        Hasil evaluasi lengkap dengan perbandingan skenario
    """
    try:
        evaluator = get_evaluator()
        
        # Set custom weights if provided
        if config.custom_weights:
            evaluator.weights = config.custom_weights
        
        # Run all scenarios
        comparison = evaluator.evaluate_all_scenarios(
            scenarios=config.scenarios,
            similarity_threshold=config.similarity_threshold
        )
        
        return {
            "success": True,
            "message": "Evaluation completed successfully",
            "best_scenario": comparison.best_scenario,
            "scenarios": [
                {
                    "name": result.scenario_name,
                    "train_size": result.train_size,
                    "test_size": result.test_size,
                    "metrics": {
                        "accuracy": result.metrics.accuracy_pct,
                        "precision": result.metrics.precision_pct,
                        "recall": result.metrics.recall_pct,
                        "f1_score": result.metrics.f1_score_pct
                    },
                    "confusion_matrix": {
                        "matrix": result.confusion_matrix.matrix,
                        "labels": result.confusion_matrix.labels,
                        "tp": result.confusion_matrix.true_positives,
                        "tn": result.confusion_matrix.true_negatives,
                        "fp": result.confusion_matrix.false_positives,
                        "fn": result.confusion_matrix.false_negatives
                    }
                }
                for result in comparison.scenarios
            ],
            "comparison_summary": comparison.comparison_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running evaluation: {str(e)}"
        )


@router.get("/results", response_model=Dict)
async def get_evaluation_results() -> Dict:
    """
    Mendapatkan hasil evaluasi terakhir.
    """
    try:
        evaluator = get_evaluator()
        
        if not evaluator.evaluation_results:
            return {
                "success": True,
                "message": "No evaluation results available. Run evaluation first.",
                "results": []
            }
        
        return {
            "success": True,
            "results": [
                {
                    "scenario": result.scenario_name,
                    "metrics": {
                        "accuracy": result.metrics.accuracy_pct,
                        "precision": result.metrics.precision_pct,
                        "recall": result.metrics.recall_pct,
                        "f1_score": result.metrics.f1_score_pct
                    },
                    "evaluated_at": result.evaluation_time
                }
                for result in evaluator.evaluation_results
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/visualization-data", response_model=Dict)
async def get_visualization_data() -> Dict:
    """
    Mendapatkan data untuk visualisasi hasil evaluasi.
    
    Data ini dapat digunakan untuk membuat:
    - Bar chart perbandingan metrik
    - Confusion matrix heatmap
    - Radar chart
    """
    try:
        evaluator = get_evaluator()
        
        if not evaluator.evaluation_results:
            return {
                "success": False,
                "message": "No evaluation results. Run evaluation first.",
                "data": None
            }
        
        viz_data = evaluator.generate_visualization_data()
        
        return {
            "success": True,
            "data": viz_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.post("/export", response_model=Dict)
async def export_results() -> Dict:
    """
    Export hasil evaluasi ke file JSON.
    """
    try:
        evaluator = get_evaluator()
        
        if not evaluator.evaluation_results:
            raise HTTPException(
                status_code=400,
                detail="No evaluation results to export. Run evaluation first."
            )
        
        output_path = evaluator.export_results()
        
        return {
            "success": True,
            "message": "Results exported successfully",
            "file_path": output_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting results: {str(e)}"
        )


@router.get("/compare/{scenario1}/{scenario2}", response_model=Dict)
async def compare_scenarios(scenario1: str, scenario2: str) -> Dict:
    """
    Membandingkan dua skenario evaluasi.
    
    Args:
        scenario1: Nama skenario pertama (contoh: "70-30")
        scenario2: Nama skenario kedua (contoh: "80-20")
    """
    try:
        evaluator = get_evaluator()
        
        if not evaluator.evaluation_results:
            raise HTTPException(
                status_code=400,
                detail="No evaluation results. Run evaluation first."
            )
        
        # Find scenarios
        s1 = next((r for r in evaluator.evaluation_results if r.scenario_name == scenario1), None)
        s2 = next((r for r in evaluator.evaluation_results if r.scenario_name == scenario2), None)
        
        if not s1:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario1} not found")
        if not s2:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario2} not found")
        
        # Calculate differences
        diff = {
            "accuracy": round(s1.metrics.accuracy_pct - s2.metrics.accuracy_pct, 2),
            "precision": round(s1.metrics.precision_pct - s2.metrics.precision_pct, 2),
            "recall": round(s1.metrics.recall_pct - s2.metrics.recall_pct, 2),
            "f1_score": round(s1.metrics.f1_score_pct - s2.metrics.f1_score_pct, 2)
        }
        
        # Determine better scenario
        better = scenario1 if s1.metrics.f1_score > s2.metrics.f1_score else scenario2
        
        return {
            "success": True,
            "scenario1": {
                "name": scenario1,
                "metrics": {
                    "accuracy": s1.metrics.accuracy_pct,
                    "precision": s1.metrics.precision_pct,
                    "recall": s1.metrics.recall_pct,
                    "f1_score": s1.metrics.f1_score_pct
                }
            },
            "scenario2": {
                "name": scenario2,
                "metrics": {
                    "accuracy": s2.metrics.accuracy_pct,
                    "precision": s2.metrics.precision_pct,
                    "recall": s2.metrics.recall_pct,
                    "f1_score": s2.metrics.f1_score_pct
                }
            },
            "difference": diff,
            "better_scenario": better,
            "recommendation": f"Scenario {better} shows better performance based on F1-Score"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
