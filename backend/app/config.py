"""
Configuration Module
====================
Konfigurasi aplikasi CBR Phone Recommendation System.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """
    Konfigurasi aplikasi menggunakan Pydantic Settings.
    Mendukung environment variables untuk deployment.
    """
    
    # Application Settings
    APP_NAME: str = "CBR Phone Recommendation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # Dataset Path
    DATASET_PATH: str = str(BASE_DIR / "data.xlsx")
    
    # CBR Settings
    # Bobot default dalam PERSENTASE (total harus 100%)
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "Harga": 25.0,              # 25% - Harga sangat penting
        "Ram": 15.0,                # 15% - RAM untuk performa
        "Memori_internal": 10.0,    # 10% - Storage
        "Kapasitas_baterai": 15.0,  # 15% - Daya tahan baterai
        "Resolusi_kamera": 15.0,    # 15% - Kualitas kamera
        "Ukuran_layar": 5.0,        # 5% - Ukuran layar
        "Rating_pengguna": 15.0     # 15% - Rating user
    }
    
    # Similarity Threshold
    SIMILARITY_THRESHOLD: float = 0.5  # Minimum similarity untuk rekomendasi
    TOP_K_RECOMMENDATIONS: int = 10    # Jumlah rekomendasi maksimum
    
    # Evaluation Settings
    TRAIN_TEST_SPLITS: list = [
        {"train": 70, "test": 30},
        {"train": 80, "test": 20}
    ]
    
    class Config:
        env_file = ".env"
        extra = "allow"

# Singleton instance
settings = Settings()

# Atribut numerik yang digunakan untuk perhitungan similarity
NUMERIC_ATTRIBUTES = [
    "Harga",
    "Ram", 
    "Memori_internal",
    "Ukuran_layar",
    "Kapasitas_baterai",
    "Rating_pengguna"
]

# Atribut kategorikal
CATEGORICAL_ATTRIBUTES = [
    "Brand",
    "Os",
    "Resolusi_kamera"
]

# Mapping resolusi kamera ke nilai numerik (MP)
CAMERA_RESOLUTION_MAP = {
    "8MP": 8,
    "12MP": 12,
    "16MP": 16,
    "24MP": 24,
    "32MP": 32,
    "48MP": 48,
    "64MP": 64,
    "108MP": 108,
    "200MP": 200
}
