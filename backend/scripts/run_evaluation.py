"""
Script evaluasi model CBR - menghasilkan metrics_report.txt dan confusion_matrix.png
Menggunakan majority voting dari Top-K neighbors untuk klasifikasi.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

from app.utils.preprocessing import DataPreprocessor
from app.cbr.weighted_euclidean import WeightedEuclideanDistance
from app.config import settings


class LabelBasedEvaluator:
    """
    Evaluator untuk CBR berbasis label klasifikasi.
    
    Menggunakan majority voting dari Top-K neighbors untuk prediksi label.
    """
    
    def __init__(self, weights: dict = None, k: int = 5):
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
        
        self.results = {}
    
    def load_and_prepare_data(self, train_path: Path, test_path: Path) -> tuple:
        """
        Load dan prepare training dan testing data.
        
        Args:
            train_path: Path ke file training CSV
            test_path: Path ke file testing CSV
            
        Returns:
            Tuple (train_df, test_df)
        """
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        # Fit preprocessor on training data
        self.preprocessor.fit(train_df)
        
        # Transform both datasets
        train_normalized = self.preprocessor.transform(train_df.copy())
        test_normalized = self.preprocessor.transform(test_df.copy())
        
        return train_df, test_df, train_normalized, test_normalized
    
    def extract_features(self, row: pd.Series) -> dict:
        """
        Extract feature vector dari row untuk distance calculation.
        
        Args:
            row: Pandas Series dengan data HP (sudah dinormalisasi)
            
        Returns:
            Dictionary fitur yang sudah dinormalisasi
        """
        # Mapping: weight_key -> normalized column name
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
            if col_name in row.index:
                val = row.get(col_name, 0)
                features[weight_key] = float(val) if pd.notna(val) else 0.0
            else:
                # Fallback: try non-normalized column
                fallback_col = weight_key.replace('_num', '')
                if fallback_col in row.index:
                    val = row.get(fallback_col, 0)
                    features[weight_key] = float(val) if pd.notna(val) else 0.0
        
        return features
    
    def predict_label(self, query_features: dict, train_df: pd.DataFrame, 
                      train_normalized: pd.DataFrame) -> str:
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
        
        for idx, row in train_normalized.iterrows():
            case_features = self.extract_features(row)
            
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
    
    def evaluate_scenario(self, train_path: Path, test_path: Path, 
                          scenario_name: str) -> dict:
        """
        Evaluasi satu skenario train-test split.
        
        Args:
            train_path: Path ke training CSV
            test_path: Path ke testing CSV
            scenario_name: Nama skenario (e.g., "70-30")
            
        Returns:
            Dictionary hasil evaluasi
        """
        print(f"\n{'='*50}")
        print(f"Evaluating Scenario: {scenario_name}")
        print(f"{'='*50}")
        
        # Load data
        train_df, test_df, train_norm, test_norm = self.load_and_prepare_data(
            train_path, test_path
        )
        
        print(f"Training samples: {len(train_df)}")
        print(f"Testing samples: {len(test_df)}")
        print(f"K neighbors: {self.k}")
        print()
        
        y_true = []
        y_pred = []
        
        # Evaluate each test case
        total = len(test_df)
        for i, (idx, row) in enumerate(test_norm.iterrows()):
            if (i + 1) % 50 == 0 or i == 0:
                print(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
            
            # Extract features from test case
            query_features = self.extract_features(row)
            
            # Predict using majority voting
            predicted = self.predict_label(query_features, train_df, train_norm)
            
            # Get actual label
            actual = test_df.loc[idx, 'Label']
            
            y_true.append(actual)
            y_pred.append(predicted)
        
        print(f"Progress: {total}/{total} (100.0%)")
        print()
        
        # Calculate metrics
        labels = ['Gaming', 'Photographer', 'Daily']
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, labels=labels, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, labels=labels, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, labels=labels, average='weighted', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        
        # Classification report
        report = classification_report(y_true, y_pred, labels=labels, zero_division=0)
        
        result = {
            'scenario_name': scenario_name,
            'train_size': len(train_df),
            'test_size': len(test_df),
            'k_neighbors': self.k,
            'metrics': {
                'accuracy': round(accuracy * 100, 2),
                'precision': round(precision * 100, 2),
                'recall': round(recall * 100, 2),
                'f1_score': round(f1 * 100, 2)
            },
            'confusion_matrix': cm.tolist(),
            'labels': labels,
            'classification_report': report,
            'y_true': y_true,
            'y_pred': y_pred,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results[scenario_name] = result
        
        print(f"Results for {scenario_name}:")
        print(f"  • Accuracy:  {result['metrics']['accuracy']:.2f}%")
        print(f"  • Precision: {result['metrics']['precision']:.2f}%")
        print(f"  • Recall:    {result['metrics']['recall']:.2f}%")
        print(f"  • F1-Score:  {result['metrics']['f1_score']:.2f}%")
        
        return result
    
    def save_metrics_report(self, output_path: Path) -> None:
        """
        Simpan laporan metrik ke file txt.
        
        Args:
            output_path: Path ke file output
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("CBR PHONE RECOMMENDATION - EVALUATION REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Method: Weighted Euclidean Distance with Majority Voting (K={self.k})\n")
            f.write("\n")
            
            f.write("WEIGHTS USED:\n")
            f.write("-" * 40 + "\n")
            for attr, weight in self.weights.items():
                f.write(f"  {attr}: {weight}%\n")
            f.write("\n")
            
            for scenario_name, result in self.results.items():
                f.write("=" * 70 + "\n")
                f.write(f"SCENARIO: {scenario_name}\n")
                f.write("=" * 70 + "\n")
                f.write(f"Training Size: {result['train_size']}\n")
                f.write(f"Testing Size: {result['test_size']}\n")
                f.write(f"K Neighbors: {result['k_neighbors']}\n")
                f.write("\n")
                
                f.write("EVALUATION METRICS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"  Accuracy:  {result['metrics']['accuracy']:.2f}%\n")
                f.write(f"  Precision: {result['metrics']['precision']:.2f}%\n")
                f.write(f"  Recall:    {result['metrics']['recall']:.2f}%\n")
                f.write(f"  F1-Score:  {result['metrics']['f1_score']:.2f}%\n")
                f.write("\n")
                
                f.write("CLASSIFICATION REPORT:\n")
                f.write("-" * 40 + "\n")
                f.write(result['classification_report'])
                f.write("\n")
                
                f.write("CONFUSION MATRIX:\n")
                f.write("-" * 40 + "\n")
                f.write("              Predicted\n")
                f.write("              Gaming  Photo   Daily\n")
                cm = result['confusion_matrix']
                labels = ['Gaming', 'Photo.', 'Daily']
                for i, label in enumerate(labels):
                    row = "  ".join(f"{v:6d}" for v in cm[i])
                    f.write(f"Actual {label:6s}  {row}\n")
                f.write("\n")
            
            # Summary comparison
            f.write("=" * 70 + "\n")
            f.write("SUMMARY COMPARISON\n")
            f.write("=" * 70 + "\n")
            f.write(f"{'Scenario':<12} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}\n")
            f.write("-" * 60 + "\n")
            for scenario_name, result in self.results.items():
                m = result['metrics']
                f.write(f"{scenario_name:<12} {m['accuracy']:<12.2f} {m['precision']:<12.2f} {m['recall']:<12.2f} {m['f1_score']:<12.2f}\n")
            
            # Best scenario
            best = max(self.results.items(), key=lambda x: x[1]['metrics']['f1_score'])
            f.write("\n")
            f.write(f"BEST SCENARIO: {best[0]} (F1-Score: {best[1]['metrics']['f1_score']:.2f}%)\n")
        
        print(f"\n[OK] Metrics report saved to: {output_path}")
    
    def save_confusion_matrix_plot(self, output_path: Path) -> None:
        """
        Simpan visualisasi confusion matrix ke file PNG.
        
        Args:
            output_path: Path ke file output
        """
        n_scenarios = len(self.results)
        fig, axes = plt.subplots(1, n_scenarios, figsize=(6 * n_scenarios, 5))
        
        if n_scenarios == 1:
            axes = [axes]
        
        for ax, (scenario_name, result) in zip(axes, self.results.items()):
            cm = np.array(result['confusion_matrix'])
            labels = result['labels']
            
            # Create heatmap
            sns.heatmap(
                cm, 
                annot=True, 
                fmt='d', 
                cmap='Blues',
                xticklabels=labels,
                yticklabels=labels,
                ax=ax
            )
            
            ax.set_title(f'Confusion Matrix - Scenario {scenario_name}\n'
                        f'Accuracy: {result["metrics"]["accuracy"]:.1f}%')
            ax.set_xlabel('Predicted Label')
            ax.set_ylabel('Actual Label')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Confusion matrix plot saved to: {output_path}")
    
    def save_results_json(self, output_path: Path) -> None:
        """Save results to JSON for frontend consumption."""
        # Remove y_true and y_pred from saved results (too large)
        export_results = {}
        for scenario, result in self.results.items():
            export_results[scenario] = {
                k: v for k, v in result.items() 
                if k not in ['y_true', 'y_pred']
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_results, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Results JSON saved to: {output_path}")


def main():
    """Main function untuk menjalankan evaluasi."""
    print("=" * 60)
    print("CBR Phone Recommendation - Model Evaluation")
    print("=" * 60)
    print()
    
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    processed_dir = base_dir / "data" / "processed"
    outputs_dir = base_dir / "outputs"
    
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize evaluator
    evaluator = LabelBasedEvaluator(k=5)
    
    print(f"Using weights: {evaluator.weights}")
    print(f"K neighbors: {evaluator.k}")
    print()
    
    # Evaluate 70-30 scenario
    train_70 = processed_dir / "train_70-30.csv"
    test_70 = processed_dir / "test_70-30.csv"
    
    if train_70.exists() and test_70.exists():
        evaluator.evaluate_scenario(train_70, test_70, "70-30")
    else:
        print(f"⚠ Files not found for 70-30 scenario. Run prepare_data.py first.")
    
    if evaluator.results:
        print()
        print("=" * 60)
        print("Generating Output Files...")
        print("=" * 60)
        
        # Save outputs
        evaluator.save_metrics_report(outputs_dir / "metrics_report.txt")
        evaluator.save_confusion_matrix_plot(outputs_dir / "confusion_matrix.png")
        evaluator.save_results_json(outputs_dir / "evaluation_results.json")
        
        print()
        print("=" * 60)
        print("✅ Evaluation completed successfully!")
        print("=" * 60)
    else:
        print("\n⚠ No evaluation performed. Please run prepare_data.py first.")


if __name__ == "__main__":
    main()
