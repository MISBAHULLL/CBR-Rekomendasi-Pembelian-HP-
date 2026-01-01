"""
API endpoints untuk admin dashboard
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

from ..cbr import get_cbr_engine
from ..config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


class WeightUpdateRequest(BaseModel):
    """Request model untuk update bobot."""
    weights: Dict[str, float] = Field(
        ...,
        description="Bobot baru dalam persentase (total harus 100%)"
    )
    
    @validator('weights')
    def validate_weights(cls, v):
        total = sum(v.values())
        if not (99 <= total <= 101):  # Allow small tolerance
            raise ValueError(f"Total bobot harus 100%, saat ini: {total}%")
        
        # Check for zero weights
        zeros = [k for k, val in v.items() if val == 0]
        if zeros:
            raise ValueError(f"Bobot tidak boleh 0 untuk: {zeros}")
        
        return v


class NewPhoneRequest(BaseModel):
    """Request model untuk menambahkan HP baru."""
    nama_hp: str = Field(..., min_length=2, description="Nama HP")
    brand: str = Field(..., description="Merek HP")
    harga: int = Field(..., ge=0, description="Harga dalam Rupiah")
    ram: int = Field(..., ge=1, description="RAM dalam GB")
    memori_internal: int = Field(..., ge=8, description="Storage dalam GB")
    ukuran_layar: float = Field(..., ge=4.0, le=10.0, description="Ukuran layar (inch)")
    resolusi_kamera: str = Field(..., description="Resolusi kamera (contoh: 48MP)")
    kapasitas_baterai: int = Field(..., ge=1000, description="Kapasitas baterai (mAh)")
    os: str = Field(..., description="Sistem operasi")
    rating_pengguna: float = Field(4.0, ge=0, le=5.0, description="Rating awal")
    tahun_rilis: Optional[str] = Field(None, description="Tahun rilis")
    stok_tersedia: bool = Field(True, description="Ketersediaan stok")


@router.get("/weights", response_model=Dict)
async def get_current_weights() -> Dict:
    """
    Mendapatkan bobot saat ini.
    
    Bobot digunakan dalam perhitungan Weighted Euclidean Distance
    untuk menentukan seberapa penting setiap atribut.
    """
    try:
        engine = get_cbr_engine()
        weights = engine.get_weights()
        
        return {
            "success": True,
            "weights": weights,
            "total": sum(weights.values()),
            "description": {
                "Harga": "Bobot untuk harga HP",
                "Ram": "Bobot untuk kapasitas RAM",
                "Memori_internal": "Bobot untuk storage internal",
                "Kapasitas_baterai": "Bobot untuk kapasitas baterai",
                "Resolusi_kamera_num": "Bobot untuk resolusi kamera",
                "Ukuran_layar": "Bobot untuk ukuran layar",
                "Rating_pengguna": "Bobot untuk rating pengguna"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.put("/weights", response_model=Dict)
async def update_weights(request: WeightUpdateRequest) -> Dict:
    """
    Update bobot atribut.
    
    **Penting:**
    - Total bobot harus 100%
    - Tidak boleh ada bobot 0
    - Perubahan akan mempengaruhi hasil rekomendasi
    
    **Contoh bobot optimal untuk rekomendasi HP:**
    ```json
    {
        "Harga": 25,
        "Ram": 15,
        "Memori_internal": 10,
        "Kapasitas_baterai": 15,
        "Resolusi_kamera_num": 15,
        "Ukuran_layar": 5,
        "Rating_pengguna": 15
    }
    ```
    """
    try:
        engine = get_cbr_engine()
        
        old_weights = engine.get_weights()
        engine.set_weights(request.weights)
        
        return {
            "success": True,
            "message": "Bobot berhasil diperbarui",
            "old_weights": old_weights,
            "new_weights": request.weights,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.post("/weights/reset", response_model=Dict)
async def reset_weights() -> Dict:
    """
    Reset bobot ke nilai default.
    """
    try:
        engine = get_cbr_engine()
        
        old_weights = engine.get_weights()
        default_weights = settings.DEFAULT_WEIGHTS.copy()
        engine.set_weights(default_weights)
        
        return {
            "success": True,
            "message": "Bobot berhasil direset ke default",
            "old_weights": old_weights,
            "new_weights": default_weights
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/weight-presets", response_model=Dict)
async def get_weight_presets() -> Dict:
    """
    Mendapatkan preset bobot untuk berbagai skenario.
    
    Preset ini dapat digunakan sebagai panduan untuk
    mengatur bobot sesuai prioritas user.
    """
    presets = {
        "balanced": {
            "name": "Seimbang",
            "description": "Bobot seimbang untuk semua atribut",
            "weights": {
                "Harga": 15.0,
                "Ram": 15.0,
                "Memori_internal": 15.0,
                "Kapasitas_baterai": 15.0,
                "Resolusi_kamera_num": 15.0,
                "Ukuran_layar": 10.0,
                "Rating_pengguna": 15.0
            }
        },
        "budget_focused": {
            "name": "Fokus Budget",
            "description": "Prioritas utama adalah harga terjangkau",
            "weights": {
                "Harga": 40.0,
                "Ram": 15.0,
                "Memori_internal": 10.0,
                "Kapasitas_baterai": 10.0,
                "Resolusi_kamera_num": 10.0,
                "Ukuran_layar": 5.0,
                "Rating_pengguna": 10.0
            }
        },
        "performance": {
            "name": "Performa Tinggi",
            "description": "Prioritas RAM dan storage untuk gaming/multitasking",
            "weights": {
                "Harga": 10.0,
                "Ram": 30.0,
                "Memori_internal": 25.0,
                "Kapasitas_baterai": 15.0,
                "Resolusi_kamera_num": 5.0,
                "Ukuran_layar": 5.0,
                "Rating_pengguna": 10.0
            }
        },
        "photography": {
            "name": "Fotografi",
            "description": "Prioritas kamera untuk content creator",
            "weights": {
                "Harga": 15.0,
                "Ram": 10.0,
                "Memori_internal": 15.0,
                "Kapasitas_baterai": 15.0,
                "Resolusi_kamera_num": 35.0,
                "Ukuran_layar": 5.0,
                "Rating_pengguna": 5.0
            }
        },
        "battery_life": {
            "name": "Daya Tahan Baterai",
            "description": "Prioritas baterai untuk mobilitas tinggi",
            "weights": {
                "Harga": 15.0,
                "Ram": 10.0,
                "Memori_internal": 10.0,
                "Kapasitas_baterai": 35.0,
                "Resolusi_kamera_num": 10.0,
                "Ukuran_layar": 10.0,
                "Rating_pengguna": 10.0
            }
        }
    }
    
    return {
        "success": True,
        "presets": presets
    }


@router.post("/phones", response_model=Dict)
async def add_new_phone(phone: NewPhoneRequest) -> Dict:
    """
    Menambahkan HP baru ke database (RETAIN phase).
    
    HP baru akan ditambahkan ke case base dan dapat
    digunakan untuk rekomendasi selanjutnya.
    """
    try:
        engine = get_cbr_engine()
        
        phone_data = {
            "Nama_hp": phone.nama_hp,
            "Brand": phone.brand,
            "Harga": phone.harga,
            "Ram": phone.ram,
            "Memori_internal": phone.memori_internal,
            "Ukuran_layar": phone.ukuran_layar,
            "Resolusi_kamera": phone.resolusi_kamera,
            "Kapasitas_baterai": phone.kapasitas_baterai,
            "Os": phone.os,
            "Rating_pengguna": phone.rating_pengguna,
            "Tahun_rilis": phone.tahun_rilis or datetime.now().strftime("%Y"),
            "Stok_tersedia": phone.stok_tersedia
        }
        
        success = engine.retain(phone_data)
        
        if success:
            return {
                "success": True,
                "message": f"HP '{phone.nama_hp}' berhasil ditambahkan",
                "phone": phone_data
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Gagal menambahkan HP baru"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/dashboard", response_model=Dict)
async def get_dashboard_data() -> Dict:
    """
    Mendapatkan data untuk admin dashboard.
    """
    try:
        engine = get_cbr_engine()
        stats = engine.get_statistics()
        
        df = engine.case_base
        
        # Calculate distributions
        brand_dist = df['Brand'].value_counts().to_dict()
        os_dist = df['Os'].value_counts().to_dict()
        ram_dist = df['Ram'].value_counts().sort_index().to_dict()
        
        # Price segments
        def get_price_segment(price):
            if price < 2000000:
                return "< 2 Juta"
            elif price < 5000000:
                return "2-5 Juta"
            elif price < 10000000:
                return "5-10 Juta"
            elif price < 15000000:
                return "10-15 Juta"
            else:
                return "> 15 Juta"
        
        price_segments = df['Harga'].apply(get_price_segment).value_counts().to_dict()
        
        return {
            "success": True,
            "overview": {
                "total_phones": stats.get("total_phones", 0),
                "total_brands": stats.get("brands", 0),
                "price_range": stats.get("price_range", {}),
                "ram_options": stats.get("ram_options", [])
            },
            "distributions": {
                "by_brand": brand_dist,
                "by_os": os_dist,
                "by_ram": ram_dist,
                "by_price_segment": price_segments
            },
            "current_weights": engine.get_weights(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.delete("/phones/{phone_id}", response_model=Dict)
async def delete_phone(phone_id: int) -> Dict:
    """
    Menghapus HP dari database.
    
    **WARNING:** Operasi ini tidak dapat dibatalkan.
    """
    try:
        engine = get_cbr_engine()
        
        # Check if phone exists
        phone = engine.case_base[engine.case_base['Id_hp'] == phone_id]
        
        if phone.empty:
            raise HTTPException(
                status_code=404,
                detail=f"HP dengan ID {phone_id} tidak ditemukan"
            )
        
        # Remove from dataframe
        engine.case_base = engine.case_base[engine.case_base['Id_hp'] != phone_id]
        
        # Save to file
        if engine.data_loader:
            engine.data_loader.df = engine.case_base
            engine.data_loader.df.to_excel(
                engine.data_loader.file_path, 
                index=False, 
                engine='openpyxl'
            )
        
        return {
            "success": True,
            "message": f"HP dengan ID {phone_id} berhasil dihapus"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
