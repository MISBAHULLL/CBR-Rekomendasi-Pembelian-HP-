"""
Data Preprocessing Module
=========================
Modul untuk preprocessing data handphone sebelum digunakan dalam CBR.

Fitur:
- Normalisasi Min-Max
- Handle Missing Values
- Encode Categorical Variables
- Parse Camera Resolution
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Class untuk preprocessing data handphone.
    
    Melakukan:
    1. Normalisasi numerik (Min-Max Scaling)
    2. Handle missing values dengan fallback logic
    3. Encode categorical (Brand, OS, Camera Resolution)
    4. Parse dan convert data types
    
    Example:
        >>> preprocessor = DataPreprocessor()
        >>> normalized_df = preprocessor.fit_transform(df)
    """
    
    # Mapping resolusi kamera ke nilai numerik (dalam MP)
    CAMERA_RESOLUTION_MAP = {
        "5MP": 5,
        "8MP": 8,
        "12MP": 12,
        "13MP": 13,
        "16MP": 16,
        "20MP": 20,
        "24MP": 24,
        "32MP": 32,
        "48MP": 48,
        "50MP": 50,
        "64MP": 64,
        "100MP": 100,
        "108MP": 108,
        "200MP": 200
    }
    
    # Kolom numerik yang akan dinormalisasi
    NUMERIC_COLUMNS = [
        'Harga', 'Ram', 'Memori_internal', 'Ukuran_layar',
        'Kapasitas_baterai', 'Rating_pengguna', 'Resolusi_kamera_num'
    ]
    
    def __init__(self):
        """Inisialisasi preprocessor."""
        self.min_values: Dict[str, float] = {}
        self.max_values: Dict[str, float] = {}
        self.is_fitted = False
        
        # Untuk encoding
        self.brand_encoding: Dict[str, int] = {}
        self.os_encoding: Dict[str, int] = {}
        
    def parse_camera_resolution(self, resolution: str) -> int:
        """
        Parse resolusi kamera dari string ke nilai numerik.
        
        Args:
            resolution: String resolusi (contoh: "48MP", "108 MP")
            
        Returns:
            Nilai numerik dalam MP
        """
        if pd.isna(resolution):
            return 12  # Default fallback
        
        resolution = str(resolution).upper().replace(" ", "")
        
        # Cek mapping langsung
        if resolution in self.CAMERA_RESOLUTION_MAP:
            return self.CAMERA_RESOLUTION_MAP[resolution]
        
        # Parse dengan regex
        match = re.search(r'(\d+)\s*MP', resolution, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Fallback
        return 12
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values dengan strategi fallback.
        
        Strategi:
        - Numerik: Gunakan median
        - Kategorikal: Gunakan mode (nilai paling sering)
        - String: Gunakan "Unknown"
        
        Args:
            df: DataFrame input
            
        Returns:
            DataFrame tanpa missing values
        """
        df = df.copy()
        
        # Numeric columns - use median
        numeric_cols = ['Harga', 'Ram', 'Memori_internal', 'Ukuran_layar', 
                       'Kapasitas_baterai', 'Rating_pengguna']
        
        for col in numeric_cols:
            if col in df.columns and df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                logger.info(f"Filled {col} missing values with median: {median_val}")
        
        # Categorical columns - use mode
        categorical_cols = ['Brand', 'Os']
        for col in categorical_cols:
            if col in df.columns and df[col].isnull().any():
                mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else "Unknown"
                df[col].fillna(mode_val, inplace=True)
                logger.info(f"Filled {col} missing values with mode: {mode_val}")
        
        # String columns - use "Unknown"
        string_cols = ['Nama_hp', 'Resolusi_kamera']
        for col in string_cols:
            if col in df.columns and df[col].isnull().any():
                df[col].fillna("Unknown", inplace=True)
        
        # Boolean columns
        if 'Stok_tersedia' in df.columns:
            df['Stok_tersedia'].fillna(True, inplace=True)
        
        return df
    
    def add_camera_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tambahkan kolom numerik untuk resolusi kamera.
        
        Args:
            df: DataFrame input
            
        Returns:
            DataFrame dengan kolom Resolusi_kamera_num
        """
        df = df.copy()
        
        if 'Resolusi_kamera' in df.columns:
            df['Resolusi_kamera_num'] = df['Resolusi_kamera'].apply(
                self.parse_camera_resolution
            )
        
        return df
    
    def fit(self, df: pd.DataFrame) -> 'DataPreprocessor':
        """
        Fit preprocessor ke data (hitung min/max untuk normalisasi).
        
        Args:
            df: DataFrame training
            
        Returns:
            self
        """
        df = self.handle_missing_values(df)
        df = self.add_camera_numeric(df)
        
        # Calculate min/max for each numeric column
        for col in self.NUMERIC_COLUMNS:
            if col in df.columns:
                self.min_values[col] = df[col].min()
                self.max_values[col] = df[col].max()
                logger.info(f"{col}: min={self.min_values[col]}, max={self.max_values[col]}")
        
        # Build encodings
        if 'Brand' in df.columns:
            unique_brands = df['Brand'].unique()
            self.brand_encoding = {brand: i for i, brand in enumerate(unique_brands)}
        
        if 'Os' in df.columns:
            unique_os = df['Os'].unique()
            self.os_encoding = {os: i for i, os in enumerate(unique_os)}
        
        self.is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data menggunakan parameter yang sudah di-fit.
        
        Args:
            df: DataFrame to transform
            
        Returns:
            Transformed DataFrame
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor belum di-fit. Panggil fit() terlebih dahulu.")
        
        df = self.handle_missing_values(df)
        df = self.add_camera_numeric(df)
        
        # Create normalized columns
        for col in self.NUMERIC_COLUMNS:
            if col in df.columns and col in self.min_values:
                min_val = self.min_values[col]
                max_val = self.max_values[col]
                
                # Avoid division by zero
                if max_val - min_val != 0:
                    df[f'{col}_norm'] = (df[col] - min_val) / (max_val - min_val)
                else:
                    df[f'{col}_norm'] = 0
        
        return df
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit dan transform dalam satu langkah.
        
        Args:
            df: DataFrame input
            
        Returns:
            Transformed DataFrame
        """
        return self.fit(df).transform(df)
    
    def normalize_value(self, value: float, column: str) -> float:
        """
        Normalisasi satu nilai berdasarkan parameter yang sudah di-fit.
        
        Args:
            value: Nilai yang akan dinormalisasi
            column: Nama kolom
            
        Returns:
            Nilai yang sudah dinormalisasi (0-1)
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor belum di-fit.")
        
        if column not in self.min_values:
            return value
        
        min_val = self.min_values[column]
        max_val = self.max_values[column]
        
        if max_val - min_val == 0:
            return 0
        
        normalized = (value - min_val) / (max_val - min_val)
        
        # Clip to [0, 1]
        return max(0, min(1, normalized))
    
    def denormalize_value(self, normalized_value: float, column: str) -> float:
        """
        Denormalisasi nilai kembali ke skala asli.
        
        Args:
            normalized_value: Nilai yang sudah dinormalisasi (0-1)
            column: Nama kolom
            
        Returns:
            Nilai dalam skala asli
        """
        if column not in self.min_values:
            return normalized_value
        
        min_val = self.min_values[column]
        max_val = self.max_values[column]
        
        return normalized_value * (max_val - min_val) + min_val
    
    def normalize_user_input(self, user_input: Dict) -> Dict:
        """
        Normalisasi input user untuk perhitungan similarity.
        
        Args:
            user_input: Dictionary berisi spesifikasi yang diinginkan user
            
        Returns:
            Dictionary dengan nilai yang sudah dinormalisasi
        """
        normalized = {}
        
        # Mapping dari input field ke column name
        field_mapping = {
            'ram': 'Ram',
            'memori_internal': 'Memori_internal',
            'ukuran_layar': 'Ukuran_layar',
            'kapasitas_baterai': 'Kapasitas_baterai',
            'min_baterai': 'Kapasitas_baterai',
            'rating': 'Rating_pengguna',
            'min_rating': 'Rating_pengguna',
            'harga': 'Harga',
            'max_harga': 'Harga',
            'resolusi_kamera': 'Resolusi_kamera_num'
        }
        
        for key, value in user_input.items():
            if value is None:
                continue
                
            column = field_mapping.get(key.lower(), key)
            
            # Handle camera resolution
            if key.lower() in ['resolusi_kamera', 'camera']:
                if isinstance(value, str):
                    value = self.parse_camera_resolution(value)
                column = 'Resolusi_kamera_num'
            
            if isinstance(value, (int, float)):
                normalized[column] = self.normalize_value(value, column)
        
        return normalized
    
    def get_normalization_params(self) -> Dict:
        """
        Mendapatkan parameter normalisasi untuk frontend.
        
        Returns:
            Dictionary berisi min/max untuk setiap kolom
        """
        return {
            "min_values": self.min_values,
            "max_values": self.max_values,
            "brand_encoding": self.brand_encoding,
            "os_encoding": self.os_encoding
        }


# Singleton instance
_preprocessor_instance: Optional[DataPreprocessor] = None

def get_preprocessor() -> DataPreprocessor:
    """
    Factory function untuk mendapatkan preprocessor instance.
    
    Returns:
        DataPreprocessor instance
    """
    global _preprocessor_instance
    
    if _preprocessor_instance is None:
        _preprocessor_instance = DataPreprocessor()
    
    return _preprocessor_instance
