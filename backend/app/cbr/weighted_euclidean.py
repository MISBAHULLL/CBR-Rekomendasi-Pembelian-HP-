"""
Weighted Euclidean Distance untuk CBR
Formula: d(x, y) = sqrt(Σ w_i * (x_i - y_i)²)
Similarity = 1 / (1 + distance)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class WeightedEuclideanDistance:
    """
    Calculator untuk Weighted Euclidean Distance.
    Bobot dalam PERSENTASE (0-100), total harus 100%.
    """
    
    # Atribut default yang digunakan untuk perhitungan
    DEFAULT_ATTRIBUTES = [
        "Harga", "Ram", "Memori_internal", "Ukuran_layar",
        "Kapasitas_baterai", "Resolusi_kamera_num", "Rating_pengguna"
    ]
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Inisialisasi calculator dengan bobot.
        
        Args:
            weights: Dictionary bobot dalam persentase
                     Contoh: {"Harga": 25, "Ram": 20, ...}
                     Total harus 100%
        """
        self.weights = weights or self._get_default_weights()
        self._validate_weights()
        self._normalized_weights = self._normalize_weights()
        
    def _get_default_weights(self) -> Dict[str, float]:
        """
        Mendapatkan bobot default (dalam persentase).
        
        Returns:
            Dictionary bobot default
        """
        return {
            "Harga": 25.0,              # 25% - Harga paling penting
            "Ram": 15.0,                # 15% - RAM untuk performa
            "Memori_internal": 10.0,    # 10% - Storage
            "Kapasitas_baterai": 15.0,  # 15% - Daya tahan baterai
            "Resolusi_kamera_num": 15.0,# 15% - Kualitas kamera
            "Ukuran_layar": 5.0,        # 5% - Ukuran layar
            "Rating_pengguna": 15.0     # 15% - Rating user
        }
    
    def _validate_weights(self) -> None:
        """
        Validasi bahwa total bobot = 100% dan tidak ada bobot 0.
        
        Raises:
            ValueError: Jika total tidak 100% atau ada bobot 0
        """
        total = sum(self.weights.values())
        
        # Toleransi untuk floating point
        if not (99.0 <= total <= 101.0):
            logger.warning(f"Total bobot = {total}%, akan dinormalisasi ke 100%")
        
        # Check for zero weights
        zero_weights = [k for k, v in self.weights.items() if v == 0]
        if zero_weights:
            logger.warning(f"Bobot 0 ditemukan untuk: {zero_weights}. Akan diganti dengan nilai minimal.")
            for k in zero_weights:
                self.weights[k] = 0.01  # Minimal weight
    
    def _normalize_weights(self) -> Dict[str, float]:
        """
        Normalisasi bobot sehingga total = 1.0.
        
        Returns:
            Dictionary bobot yang sudah dinormalisasi
        """
        total = sum(self.weights.values())
        return {k: v / total for k, v in self.weights.items()}
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Set bobot baru (dalam persentase).
        
        Args:
            weights: Dictionary bobot baru
        """
        self.weights = weights
        self._validate_weights()
        self._normalized_weights = self._normalize_weights()
        logger.info(f"Weights updated: {self.weights}")
    
    def get_weights_percentage(self) -> Dict[str, float]:
        """
        Mendapatkan bobot dalam persentase.
        
        Returns:
            Dictionary bobot dalam persentase
        """
        return self.weights.copy()
    
    def calculate_distance(
        self, 
        query: Dict[str, float], 
        case: Dict[str, float]
    ) -> float:
        """
        Hitung Weighted Euclidean Distance antara query dan case.
        
        Formula: d(x,y) = sqrt(Σ w_i * (x_i - y_i)²)
        
        Args:
            query: Dictionary fitur query (nilai sudah dinormalisasi 0-1)
            case: Dictionary fitur case (nilai sudah dinormalisasi 0-1)
            
        Returns:
            Nilai distance (0 = identik, semakin besar semakin berbeda)
        """
        squared_diff_sum = 0.0
        
        for attr, weight in self._normalized_weights.items():
            # Get values, default to 0.5 if not present (middle value)
            q_val = query.get(attr, 0.5)
            c_val = case.get(attr, 0.5)
            
            # Skip if query doesn't have this attribute
            if attr not in query:
                continue
            
            # Calculate weighted squared difference
            diff = q_val - c_val
            squared_diff_sum += weight * (diff ** 2)
        
        # Square root untuk Euclidean
        distance = np.sqrt(squared_diff_sum)
        
        return distance
    
    def calculate_similarity(
        self, 
        query: Dict[str, float], 
        case: Dict[str, float]
    ) -> float:
        """
        Hitung similarity score antara query dan case.
        
        Menggunakan formula: similarity = 1 / (1 + distance)
        Alternatif: similarity = 1 - distance (jika distance maksimal = 1)
        
        Args:
            query: Dictionary fitur query
            case: Dictionary fitur case
            
        Returns:
            Similarity score (0-1), semakin tinggi semakin mirip
        """
        distance = self.calculate_distance(query, case)
        
        # Convert distance to similarity
        # Menggunakan formula: sim = 1 / (1 + d)
        # Ini memastikan similarity selalu dalam range (0, 1]
        similarity = 1 / (1 + distance)
        
        return similarity
    
    def calculate_similarity_batch(
        self, 
        query: Dict[str, float], 
        cases: List[Dict[str, float]]
    ) -> List[Tuple[int, float]]:
        """
        Hitung similarity untuk batch cases.
        
        Args:
            query: Dictionary fitur query
            cases: List of dictionaries, masing-masing adalah satu case
            
        Returns:
            List of tuples (index, similarity_score), sorted by similarity descending
        """
        results = []
        
        for i, case in enumerate(cases):
            sim = self.calculate_similarity(query, case)
            results.append((i, sim))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def get_attribute_contributions(
        self, 
        query: Dict[str, float], 
        case: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Mendapatkan kontribusi setiap atribut terhadap similarity.
        Berguna untuk menjelaskan mengapa sebuah HP direkomendasikan.
        
        Args:
            query: Dictionary fitur query
            case: Dictionary fitur case
            
        Returns:
            Dictionary berisi kontribusi setiap atribut
        """
        contributions = {}
        total_similarity = self.calculate_similarity(query, case)
        
        for attr, weight in self._normalized_weights.items():
            q_val = query.get(attr, 0.5)
            c_val = case.get(attr, 0.5)
            
            # Calculate individual attribute similarity
            diff = abs(q_val - c_val)
            attr_similarity = 1 - diff  # Simple similarity for single attribute
            
            # Weight contribution
            weighted_contribution = weight * attr_similarity
            
            contributions[attr] = {
                "query_value": q_val,
                "case_value": c_val,
                "difference": diff,
                "attribute_similarity": attr_similarity,
                "weight_percentage": self.weights.get(attr, 0),
                "weighted_contribution": weighted_contribution * 100,  # In percentage
                "match_quality": self._get_match_quality(attr_similarity)
            }
        
        return contributions
    
    def _get_match_quality(self, similarity: float) -> str:
        """
        Mendapatkan deskripsi kualitas kecocokan.
        
        Args:
            similarity: Nilai similarity (0-1)
            
        Returns:
            String deskripsi
        """
        if similarity >= 0.9:
            return "Sangat Cocok"
        elif similarity >= 0.7:
            return "Cocok"
        elif similarity >= 0.5:
            return "Cukup Cocok"
        elif similarity >= 0.3:
            return "Kurang Cocok"
        else:
            return "Tidak Cocok"


# Fungsi helper untuk penggunaan cepat
def calculate_weighted_euclidean(
    query: Dict[str, float],
    case: Dict[str, float],
    weights: Dict[str, float] = None
) -> float:
    """
    Helper function untuk menghitung weighted euclidean distance.
    
    Args:
        query: Fitur query
        case: Fitur case
        weights: Bobot (optional)
        
    Returns:
        Distance value
    """
    calculator = WeightedEuclideanDistance(weights)
    return calculator.calculate_distance(query, case)


def calculate_similarity(
    query: Dict[str, float],
    case: Dict[str, float],
    weights: Dict[str, float] = None
) -> float:
    """
    Helper function untuk menghitung similarity.
    
    Args:
        query: Fitur query
        case: Fitur case
        weights: Bobot (optional)
        
    Returns:
        Similarity score (0-1)
    """
    calculator = WeightedEuclideanDistance(weights)
    return calculator.calculate_similarity(query, case)
