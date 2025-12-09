"""
Phone Models
============
Pydantic models untuk data handphone dan request/response API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum


class BrandEnum(str, Enum):
    """Enum untuk brand handphone yang tersedia."""
    APPLE = "Apple"
    SAMSUNG = "Samsung"
    XIAOMI = "Xiaomi"
    OPPO = "Oppo"
    VIVO = "Vivo"
    REALME = "Realme"
    HUAWEI = "Huawei"
    ASUS = "Asus"
    SONY = "Sony"
    ONEPLUS = "OnePlus"
    OTHER = "Other"


class OSEnum(str, Enum):
    """Enum untuk sistem operasi."""
    IOS = "iOS"
    ANDROID = "Android"


class Phone(BaseModel):
    """
    Model untuk data handphone dari database/dataset.
    Representasi lengkap dari satu kasus (case) dalam CBR.
    """
    id_hp: int = Field(..., description="ID unik handphone")
    nama_hp: str = Field(..., description="Nama model handphone")
    brand: str = Field(..., description="Merek handphone")
    harga: int = Field(..., ge=0, description="Harga dalam Rupiah")
    ram: int = Field(..., ge=1, description="Kapasitas RAM dalam GB")
    memori_internal: int = Field(..., ge=8, description="Storage internal dalam GB")
    ukuran_layar: float = Field(..., ge=4.0, le=10.0, description="Ukuran layar dalam inci")
    resolusi_kamera: str = Field(..., description="Resolusi kamera utama")
    kapasitas_baterai: int = Field(..., ge=1000, description="Kapasitas baterai dalam mAh")
    os: str = Field(..., description="Sistem operasi")
    rating_pengguna: float = Field(..., ge=0, le=5.0, description="Rating user 0-5")
    tahun_rilis: Optional[str] = Field(None, description="Tahun rilis")
    stok_tersedia: bool = Field(True, description="Ketersediaan stok")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_hp": 1,
                "nama_hp": "Samsung Galaxy S24 Ultra",
                "brand": "Samsung",
                "harga": 19999000,
                "ram": 12,
                "memori_internal": 256,
                "ukuran_layar": 6.8,
                "resolusi_kamera": "200MP",
                "kapasitas_baterai": 5000,
                "os": "Android",
                "rating_pengguna": 4.8,
                "tahun_rilis": "2024",
                "stok_tersedia": True
            }
        }


class PhoneInput(BaseModel):
    """
    Model untuk input spesifikasi HP yang diinginkan user.
    Semua field optional karena user bisa memilih kriteria yang diinginkan saja.
    """
    # Kriteria Utama
    min_harga: Optional[int] = Field(None, ge=0, description="Harga minimum")
    max_harga: Optional[int] = Field(None, ge=0, description="Harga maksimum (budget)")
    
    ram: Optional[int] = Field(None, ge=1, le=24, description="RAM yang diinginkan (GB)")
    memori_internal: Optional[int] = Field(None, ge=8, le=1024, description="Storage yang diinginkan (GB)")
    
    min_baterai: Optional[int] = Field(None, ge=1000, description="Kapasitas baterai minimum (mAh)")
    
    resolusi_kamera: Optional[str] = Field(None, description="Resolusi kamera yang diinginkan")
    
    ukuran_layar: Optional[float] = Field(None, ge=4.0, le=10.0, description="Ukuran layar yang diinginkan")
    
    min_rating: Optional[float] = Field(None, ge=0, le=5.0, description="Rating minimum")
    
    # Preferensi Tambahan (Wishlist)
    preferred_brands: Optional[List[str]] = Field(None, description="List brand yang disukai")
    preferred_os: Optional[str] = Field(None, description="OS yang diinginkan (iOS/Android)")
    
    # Prioritas Fitur (dalam persentase, total harus 100%)
    custom_weights: Optional[Dict[str, float]] = Field(
        None, 
        description="Bobot kustom untuk setiap atribut dalam persentase"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "min_harga": 3000000,
                "max_harga": 10000000,
                "ram": 8,
                "memori_internal": 128,
                "min_baterai": 4500,
                "resolusi_kamera": "48MP",
                "ukuran_layar": 6.5,
                "min_rating": 4.0,
                "preferred_brands": ["Samsung", "Xiaomi"],
                "preferred_os": "Android",
                "custom_weights": {
                    "Harga": 25.0,
                    "Ram": 20.0,
                    "Memori_internal": 10.0,
                    "Kapasitas_baterai": 15.0,
                    "Resolusi_kamera": 15.0,
                    "Ukuran_layar": 5.0,
                    "Rating_pengguna": 10.0
                }
            }
        }


class RecommendationRequest(BaseModel):
    """
    Request untuk mendapatkan rekomendasi HP.
    """
    input_specs: PhoneInput = Field(..., description="Spesifikasi yang diinginkan user")
    top_k: int = Field(10, ge=1, le=50, description="Jumlah rekomendasi yang diminta")
    min_similarity: float = Field(0.3, ge=0, le=1.0, description="Threshold similarity minimum")


class SimilarityExplanation(BaseModel):
    """
    Penjelasan mengapa HP direkomendasikan.
    """
    attribute: str = Field(..., description="Nama atribut")
    user_value: str = Field(..., description="Nilai yang diminta user")
    phone_value: str = Field(..., description="Nilai pada HP")
    match_score: float = Field(..., description="Skor kecocokan atribut ini")
    contribution: float = Field(..., description="Kontribusi terhadap total similarity")


class RecommendationResult(BaseModel):
    """
    Hasil rekomendasi untuk satu HP.
    """
    phone: Phone = Field(..., description="Data HP yang direkomendasikan")
    similarity_score: float = Field(..., ge=0, le=1.0, description="Skor kemiripan (0-1)")
    similarity_percentage: float = Field(..., description="Persentase kemiripan")
    rank: int = Field(..., ge=1, description="Peringkat rekomendasi")
    explanations: List[SimilarityExplanation] = Field(
        default=[], 
        description="Penjelasan alasan rekomendasi"
    )
    match_highlights: List[str] = Field(
        default=[], 
        description="Highlight fitur yang cocok"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone": {
                    "id_hp": 1,
                    "nama_hp": "Samsung Galaxy A54",
                    "brand": "Samsung",
                    "harga": 6499000,
                    "ram": 8,
                    "memori_internal": 128,
                    "ukuran_layar": 6.4,
                    "resolusi_kamera": "50MP",
                    "kapasitas_baterai": 5000,
                    "os": "Android",
                    "rating_pengguna": 4.5,
                    "tahun_rilis": "2023",
                    "stok_tersedia": True
                },
                "similarity_score": 0.89,
                "similarity_percentage": 89.0,
                "rank": 1,
                "explanations": [
                    {
                        "attribute": "Harga",
                        "user_value": "6.000.000 - 8.000.000",
                        "phone_value": "6.499.000",
                        "match_score": 0.95,
                        "contribution": 23.75
                    }
                ],
                "match_highlights": [
                    "✓ Harga sesuai budget",
                    "✓ RAM sesuai kebutuhan",
                    "✓ Baterai besar"
                ]
            }
        }


class RecommendationResponse(BaseModel):
    """
    Response lengkap dari endpoint rekomendasi.
    """
    success: bool = Field(True, description="Status keberhasilan")
    message: str = Field("Rekomendasi berhasil dihasilkan", description="Pesan status")
    total_results: int = Field(..., description="Jumlah HP yang direkomendasikan")
    query_summary: Dict = Field(..., description="Ringkasan query user")
    weights_used: Dict[str, float] = Field(..., description="Bobot yang digunakan")
    recommendations: List[RecommendationResult] = Field(..., description="List rekomendasi")
