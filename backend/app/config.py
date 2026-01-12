"""
Konfigurasi aplikasi CBR
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Pydantic Settings untuk konfigurasi app."""
    
    # Application Settings
    APP_NAME: str = "CBR Phone Recommendation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # Dataset Path - Railway compatible
    DATASET_PATH: str = os.getenv("DATASET_PATH", str(BASE_DIR / "data.xlsx"))
    
    # CBR Settings
    # Bobot default dalam PERSENTASE (total harus 100%)
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "Harga": 20.0,              # 20% - Harga penting
        "Ram": 20.0,                # 20% - RAM untuk performa (Gaming)
        "Memori_internal": 10.0,    # 10% - Storage
        "Kapasitas_baterai": 15.0,  # 15% - Daya tahan baterai
        "Resolusi_kamera_num": 20.0,# 20% - Kualitas kamera (Photographer)
        "Ukuran_layar": 5.0,        # 5% - Ukuran layar
        "Rating_pengguna": 10.0     # 10% - Rating user
    }
    
    # Similarity Threshold
    SIMILARITY_THRESHOLD: float = 0.5  # Minimum similarity untuk rekomendasi
    TOP_K_RECOMMENDATIONS: int = 10    # Jumlah rekomendasi maksimum
    
    # Evaluation Settings - Hanya 70-30 split
    TRAIN_TEST_SPLITS: list = [
        {"train": 70, "test": 30}
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
