"""
CBR Engine Module
=================
Case-Based Reasoning Engine untuk Sistem Rekomendasi Handphone.

Implementasi lengkap 4 fase CBR (R4):
1. RETRIEVE - Mengambil kasus yang mirip dari case base
2. REUSE - Menggunakan solusi dari kasus yang mirip
3. REVISE - Menyesuaikan solusi jika diperlukan
4. RETAIN - Menyimpan kasus baru yang berhasil

Menggunakan Weighted Euclidean Distance untuk perhitungan similarity.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

from .weighted_euclidean import WeightedEuclideanDistance
from ..utils.data_loader import DataLoader
from ..utils.preprocessing import DataPreprocessor
from ..config import settings

logger = logging.getLogger(__name__)


class CBREngine:
    """
    Case-Based Reasoning Engine untuk rekomendasi handphone.
    
    Mengimplementasikan siklus CBR lengkap:
    - Retrieve: Mencari HP yang mirip dengan preferensi user
    - Reuse: Menggunakan HP tersebut sebagai rekomendasi
    - Revise: Menyesuaikan ranking berdasarkan preferensi tambahan
    - Retain: Menyimpan feedback untuk pembelajaran
    
    Attributes:
        case_base: DataFrame berisi semua HP dalam database
        preprocessor: DataPreprocessor untuk normalisasi
        distance_calculator: WeightedEuclideanDistance untuk similarity
        weights: Bobot atribut dalam persentase
    
    Example:
        >>> engine = CBREngine()
        >>> engine.load_case_base("data.xlsx")
        >>> recommendations = engine.recommend(user_preferences, top_k=10)
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Inisialisasi CBR Engine.
        
        Args:
            weights: Bobot atribut dalam persentase (optional)
        """
        self.case_base: Optional[pd.DataFrame] = None
        self.case_base_normalized: Optional[pd.DataFrame] = None
        self.data_loader: Optional[DataLoader] = None
        self.preprocessor = DataPreprocessor()
        
        # Set weights
        self.weights = weights or settings.DEFAULT_WEIGHTS.copy()
        self.distance_calculator = WeightedEuclideanDistance(self.weights)
        
        self.is_initialized = False
        logger.info("CBR Engine initialized")
        
    def load_case_base(self, file_path: str = None) -> None:
        """
        Memuat case base dari file Excel.
        
        Args:
            file_path: Path ke file dataset (optional, default dari settings)
        """
        file_path = file_path or settings.DATASET_PATH
        
        logger.info(f"Loading case base from: {file_path}")
        
        # Load data
        self.data_loader = DataLoader(file_path)
        self.case_base = self.data_loader.load(validate=True)
        
        # Preprocess and normalize
        self.case_base_normalized = self.preprocessor.fit_transform(self.case_base)
        
        self.is_initialized = True
        logger.info(f"Case base loaded: {len(self.case_base)} cases")
        
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Set bobot baru untuk perhitungan similarity.
        
        Args:
            weights: Dictionary bobot dalam persentase
        """
        self.weights = weights
        self.distance_calculator.set_weights(weights)
        logger.info(f"Weights updated: {weights}")
        
    def get_weights(self) -> Dict[str, float]:
        """
        Mendapatkan bobot saat ini.
        
        Returns:
            Dictionary bobot dalam persentase
        """
        return self.weights.copy()
    
    # ==================== RETRIEVE PHASE ====================
    def retrieve(
        self, 
        query: Dict[str, Any], 
        top_k: int = 10,
        min_similarity: float = 0.3
    ) -> List[Tuple[int, Dict, float]]:
        """
        RETRIEVE Phase: Mengambil kasus yang mirip dari case base.
        
        Mencari HP dalam database yang memiliki similarity tinggi
        dengan preferensi yang diberikan user.
        
        Args:
            query: Dictionary berisi preferensi user
                   Contoh: {"Ram": 8, "Harga": 5000000, ...}
            top_k: Jumlah maksimum hasil yang dikembalikan
            min_similarity: Threshold minimum similarity
            
        Returns:
            List of tuples: (index, case_dict, similarity_score)
            Sorted by similarity descending
        """
        if not self.is_initialized:
            raise ValueError("Case base belum dimuat. Panggil load_case_base() terlebih dahulu.")
        
        logger.info(f"RETRIEVE: Searching for similar cases with query: {query}")
        
        # Normalize query
        normalized_query = self._prepare_query(query)
        
        results = []
        
        for idx, row in self.case_base_normalized.iterrows():
            # Prepare case vector
            case_vector = self._extract_case_vector(row)
            
            # Calculate similarity
            similarity = self.distance_calculator.calculate_similarity(
                normalized_query, 
                case_vector
            )
            
            if similarity >= min_similarity:
                # Get original case data
                original_case = self.case_base.iloc[idx].to_dict()
                results.append((idx, original_case, similarity))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[2], reverse=True)
        
        # Return top_k
        retrieved = results[:top_k]
        
        logger.info(f"RETRIEVE: Found {len(retrieved)} matching cases")
        return retrieved
    
    def _prepare_query(self, query: Dict[str, Any]) -> Dict[str, float]:
        """
        Prepare dan normalisasi query dari user.
        
        Args:
            query: Raw query dari user
            
        Returns:
            Normalized query dictionary
        """
        normalized = {}
        
        # Mapping field names
        field_mapping = {
            'ram': 'Ram',
            'memori_internal': 'Memori_internal',
            'storage': 'Memori_internal',
            'ukuran_layar': 'Ukuran_layar',
            'screen_size': 'Ukuran_layar',
            'kapasitas_baterai': 'Kapasitas_baterai',
            'min_baterai': 'Kapasitas_baterai',
            'battery': 'Kapasitas_baterai',
            'rating': 'Rating_pengguna',
            'min_rating': 'Rating_pengguna',
            'harga': 'Harga',
            'max_harga': 'Harga',
            'price': 'Harga',
            'resolusi_kamera': 'Resolusi_kamera_num',
            'camera': 'Resolusi_kamera_num'
        }
        
        for key, value in query.items():
            if value is None:
                continue
            
            # Map to standard column name
            std_key = field_mapping.get(key.lower(), key)
            
            # Handle camera resolution string
            if key.lower() in ['resolusi_kamera', 'camera'] and isinstance(value, str):
                value = self.preprocessor.parse_camera_resolution(value)
                std_key = 'Resolusi_kamera_num'
            
            if isinstance(value, (int, float)):
                # Normalize using preprocessor
                normalized[std_key] = self.preprocessor.normalize_value(value, std_key)
        
        return normalized
    
    def _extract_case_vector(self, row: pd.Series) -> Dict[str, float]:
        """
        Extract normalized feature vector from a case.
        
        Args:
            row: Pandas Series dari case_base_normalized
            
        Returns:
            Dictionary of normalized features
        """
        vector = {}
        
        feature_columns = [
            'Harga_norm', 'Ram_norm', 'Memori_internal_norm',
            'Ukuran_layar_norm', 'Kapasitas_baterai_norm',
            'Resolusi_kamera_num_norm', 'Rating_pengguna_norm'
        ]
        
        # Map normalized column to standard name
        for col in feature_columns:
            std_name = col.replace('_norm', '')
            if col in row.index:
                vector[std_name] = row[col] if not pd.isna(row[col]) else 0.5
        
        return vector
    
    # ==================== REUSE PHASE ====================
    def reuse(
        self, 
        retrieved_cases: List[Tuple[int, Dict, float]],
        user_preferences: Dict = None
    ) -> List[Dict]:
        """
        REUSE Phase: Menggunakan kasus yang ditemukan sebagai solusi.
        
        Dalam konteks rekomendasi HP, fase reuse berarti:
        - Menggunakan HP yang ditemukan sebagai rekomendasi
        - Menambahkan informasi tambahan (penjelasan kemiripan)
        
        Args:
            retrieved_cases: Hasil dari fase RETRIEVE
            user_preferences: Preferensi tambahan user
            
        Returns:
            List of recommendation dictionaries
        """
        logger.info("REUSE: Preparing recommendations from retrieved cases")
        
        recommendations = []
        
        for rank, (idx, case, similarity) in enumerate(retrieved_cases, 1):
            recommendation = {
                "rank": rank,
                "phone": case,
                "similarity_score": similarity,
                "similarity_percentage": round(similarity * 100, 2),
                "explanations": self._generate_explanations(case, user_preferences),
                "match_highlights": self._generate_highlights(case, user_preferences)
            }
            recommendations.append(recommendation)
        
        logger.info(f"REUSE: Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _generate_explanations(
        self, 
        case: Dict, 
        user_preferences: Dict = None
    ) -> List[Dict]:
        """
        Generate penjelasan mengapa HP ini direkomendasikan.
        
        Args:
            case: Data HP yang direkomendasikan
            user_preferences: Preferensi user
            
        Returns:
            List of explanation dictionaries
        """
        explanations = []
        
        if not user_preferences:
            return explanations
        
        # Compare each attribute
        attribute_mappings = {
            'ram': ('Ram', 'GB'),
            'memori_internal': ('Memori_internal', 'GB'),
            'max_harga': ('Harga', 'Rp'),
            'min_baterai': ('Kapasitas_baterai', 'mAh'),
            'min_rating': ('Rating_pengguna', ''),
            'ukuran_layar': ('Ukuran_layar', 'inch')
        }
        
        for pref_key, (case_key, unit) in attribute_mappings.items():
            if pref_key in user_preferences and user_preferences[pref_key] is not None:
                user_value = user_preferences[pref_key]
                case_value = case.get(case_key)
                
                # Skip if case_value is None
                if case_value is None:
                    continue
                
                # Calculate match score
                if isinstance(user_value, (int, float)) and isinstance(case_value, (int, float)):
                    if user_value != 0 and case_value != 0:
                        match_score = 1 - abs(user_value - case_value) / max(user_value, case_value)
                    else:
                        match_score = 0.5
                else:
                    match_score = 0.5
                
                match_score = max(0, min(1, match_score))
                
                # Format values safely
                if isinstance(user_value, (int, float)):
                    user_str = f"{int(user_value):,} {unit}".strip()
                else:
                    user_str = str(user_value) if user_value else "-"
                    
                if isinstance(case_value, (int, float)):
                    case_str = f"{int(case_value):,} {unit}".strip()
                else:
                    case_str = str(case_value) if case_value else "-"
                
                explanations.append({
                    "attribute": case_key,
                    "user_value": user_str,
                    "phone_value": case_str,
                    "match_score": round(match_score, 2),
                    "contribution": round(match_score * self.weights.get(case_key, 10), 2)
                })
        
        return explanations
    
    def _generate_highlights(
        self, 
        case: Dict, 
        user_preferences: Dict = None
    ) -> List[str]:
        """
        Generate highlight mengapa HP ini cocok.
        
        Args:
            case: Data HP
            user_preferences: Preferensi user
            
        Returns:
            List of highlight strings
        """
        highlights = []
        
        if not user_preferences:
            return highlights
        
        # Check budget
        if 'max_harga' in user_preferences and user_preferences['max_harga']:
            if case.get('Harga', 0) <= user_preferences['max_harga']:
                highlights.append("✓ Harga sesuai budget")
        
        # Check RAM
        if 'ram' in user_preferences and user_preferences['ram']:
            if case.get('Ram', 0) >= user_preferences['ram']:
                highlights.append("✓ RAM memenuhi kebutuhan")
        
        # Check Battery
        if 'min_baterai' in user_preferences and user_preferences['min_baterai']:
            if case.get('Kapasitas_baterai', 0) >= user_preferences['min_baterai']:
                highlights.append("✓ Baterai besar")
        
        # Check Rating
        if 'min_rating' in user_preferences and user_preferences['min_rating']:
            if case.get('Rating_pengguna', 0) >= user_preferences['min_rating']:
                highlights.append("✓ Rating tinggi")
        
        # Check Brand preference
        if 'preferred_brands' in user_preferences and user_preferences['preferred_brands']:
            if case.get('Brand', '') in user_preferences['preferred_brands']:
                highlights.append(f"✓ Brand favorit ({case.get('Brand')})")
        
        # Check OS preference
        if 'preferred_os' in user_preferences and user_preferences['preferred_os']:
            if case.get('Os', '').lower() == user_preferences['preferred_os'].lower():
                highlights.append(f"✓ OS sesuai ({case.get('Os')})")
        
        # Add general highlights based on specs
        if case.get('Rating_pengguna', 0) >= 4.5:
            highlights.append("⭐ Rating sangat tinggi")
        
        if case.get('Kapasitas_baterai', 0) >= 5000:
            highlights.append("🔋 Baterai jumbo")
        
        return highlights
    
    # ==================== REVISE PHASE ====================
    def revise(
        self, 
        recommendations: List[Dict],
        additional_filters: Dict = None
    ) -> List[Dict]:
        """
        REVISE Phase: Menyesuaikan rekomendasi berdasarkan kriteria tambahan.
        
        Revisi dilakukan untuk:
        - Filter berdasarkan ketersediaan stok
        - Filter berdasarkan brand preference
        - Re-ranking berdasarkan preferensi OS
        
        Args:
            recommendations: Hasil dari fase REUSE
            additional_filters: Filter tambahan dari user
            
        Returns:
            Revised recommendations
        """
        logger.info("REVISE: Applying additional filters and adjustments")
        
        revised = recommendations.copy()
        
        if not additional_filters:
            return revised
        
        # Filter by stock availability
        if additional_filters.get('only_in_stock', False):
            revised = [r for r in revised if r['phone'].get('Stok_tersedia', True)]
        
        # Filter by brand
        if additional_filters.get('preferred_brands'):
            brands = additional_filters['preferred_brands']
            # Boost matching brands
            for r in revised:
                if r['phone'].get('Brand') in brands:
                    r['similarity_score'] *= 1.1  # 10% boost
                    r['similarity_percentage'] = round(min(100, r['similarity_score'] * 100), 2)
        
        # Filter by OS
        if additional_filters.get('preferred_os'):
            target_os = additional_filters['preferred_os'].lower()
            for r in revised:
                if r['phone'].get('Os', '').lower() == target_os:
                    r['similarity_score'] *= 1.05  # 5% boost
                    r['similarity_percentage'] = round(min(100, r['similarity_score'] * 100), 2)
        
        # Re-sort by adjusted similarity
        revised.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Update ranks
        for i, r in enumerate(revised, 1):
            r['rank'] = i
        
        logger.info(f"REVISE: {len(revised)} recommendations after revision")
        return revised
    
    # ==================== RETAIN PHASE ====================
    def retain(self, new_case: Dict, feedback: Dict = None) -> bool:
        """
        RETAIN Phase: Menyimpan kasus baru ke case base.
        
        Kasus baru dapat berupa:
        - HP baru yang ditambahkan admin
        - Feedback positif dari user yang menghasilkan kasus baru
        
        Args:
            new_case: Dictionary berisi data HP baru
            feedback: Optional feedback dari user
            
        Returns:
            True jika berhasil disimpan
        """
        logger.info("RETAIN: Adding new case to case base")
        
        try:
            # Validate new case
            required_fields = ['Nama_hp', 'Brand', 'Harga', 'Ram', 'Memori_internal']
            for field in required_fields:
                if field not in new_case:
                    logger.error(f"RETAIN: Missing required field: {field}")
                    return False
            
            # Add to case base
            if self.data_loader:
                success = self.data_loader.add_new_case(new_case)
                
                if success:
                    # Reload case base
                    self.load_case_base()
                    logger.info(f"RETAIN: New case added successfully")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"RETAIN: Error adding new case: {e}")
            return False
    
    # ==================== MAIN RECOMMENDATION METHOD ====================
    def recommend(
        self,
        user_input: Dict,
        top_k: int = 10,
        min_similarity: float = 0.3,
        apply_filters: bool = True
    ) -> Dict:
        """
        Main method untuk mendapatkan rekomendasi HP.
        
        Menjalankan siklus CBR lengkap:
        1. RETRIEVE - Cari HP yang mirip
        2. REUSE - Gunakan sebagai rekomendasi
        3. REVISE - Sesuaikan berdasarkan preferensi
        
        Args:
            user_input: Dictionary berisi preferensi user
            top_k: Jumlah rekomendasi maksimum
            min_similarity: Threshold minimum similarity
            apply_filters: Apakah apply filter tambahan
            
        Returns:
            Dictionary berisi rekomendasi lengkap
        """
        logger.info(f"Starting CBR recommendation cycle with input: {user_input}")
        
        # Prepare query from user input
        query = self._extract_query_from_input(user_input)
        
        # RETRIEVE
        retrieved = self.retrieve(query, top_k=top_k * 2, min_similarity=min_similarity)
        
        # REUSE
        recommendations = self.reuse(retrieved, user_input)
        
        # REVISE
        if apply_filters:
            additional_filters = {
                'preferred_brands': user_input.get('preferred_brands'),
                'preferred_os': user_input.get('preferred_os'),
                'only_in_stock': user_input.get('only_in_stock', False)
            }
            recommendations = self.revise(recommendations, additional_filters)
        
        # Limit to top_k
        recommendations = recommendations[:top_k]
        
        # Prepare response
        response = {
            "success": True,
            "message": f"Ditemukan {len(recommendations)} rekomendasi HP",
            "total_results": len(recommendations),
            "query_summary": self._summarize_query(user_input),
            "weights_used": self.weights,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _extract_query_from_input(self, user_input: Dict) -> Dict:
        """
        Extract query values from user input.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Cleaned query dictionary
        """
        query = {}
        
        # Direct numeric mappings
        if user_input.get('ram'):
            query['ram'] = user_input['ram']
        if user_input.get('memori_internal'):
            query['memori_internal'] = user_input['memori_internal']
        if user_input.get('max_harga'):
            query['harga'] = user_input['max_harga']
        elif user_input.get('min_harga') and user_input.get('max_harga'):
            query['harga'] = (user_input['min_harga'] + user_input['max_harga']) / 2
        if user_input.get('min_baterai'):
            query['kapasitas_baterai'] = user_input['min_baterai']
        if user_input.get('min_rating'):
            query['rating'] = user_input['min_rating']
        if user_input.get('ukuran_layar'):
            query['ukuran_layar'] = user_input['ukuran_layar']
        if user_input.get('resolusi_kamera'):
            query['resolusi_kamera'] = user_input['resolusi_kamera']
        
        return query
    
    def _summarize_query(self, user_input: Dict) -> Dict:
        """
        Create summary of user query for response.
        
        Args:
            user_input: User input dictionary
            
        Returns:
            Summary dictionary
        """
        summary = {}
        
        min_h = user_input.get('min_harga')
        max_h = user_input.get('max_harga')
        
        if min_h is not None or max_h is not None:
            min_val = int(min_h) if min_h is not None else 0
            max_val = int(max_h) if max_h is not None else 50000000
            summary['budget'] = f"Rp {min_val:,} - Rp {max_val:,}"
        
        if user_input.get('ram') is not None:
            summary['ram'] = f"{user_input['ram']} GB"
        
        if user_input.get('memori_internal') is not None:
            summary['storage'] = f"{user_input['memori_internal']} GB"
        
        if user_input.get('min_baterai') is not None:
            summary['battery'] = f"Min {user_input['min_baterai']} mAh"
        
        if user_input.get('preferred_brands'):
            summary['brands'] = user_input['preferred_brands']
        
        if user_input.get('preferred_os'):
            summary['os'] = user_input['preferred_os']
        
        return summary
    
    def get_statistics(self) -> Dict:
        """
        Mendapatkan statistik case base.
        
        Returns:
            Dictionary berisi statistik
        """
        if not self.is_initialized:
            return {"error": "Case base belum dimuat"}
        
        return self.data_loader.get_statistics()


# Singleton instance
_cbr_engine: Optional[CBREngine] = None

def get_cbr_engine() -> CBREngine:
    """
    Factory function untuk mendapatkan CBR Engine instance.
    
    Returns:
        CBREngine instance yang sudah di-initialize
    """
    global _cbr_engine
    
    if _cbr_engine is None:
        _cbr_engine = CBREngine()
        _cbr_engine.load_case_base()
    
    return _cbr_engine
