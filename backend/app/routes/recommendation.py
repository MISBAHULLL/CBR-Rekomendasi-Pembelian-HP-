"""
Recommendation Routes
=====================
API endpoints untuk sistem rekomendasi handphone.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..cbr import get_cbr_engine
from ..models.phone import (
    PhoneInput, 
    RecommendationRequest,
    RecommendationResponse
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class QuickRecommendRequest(BaseModel):
    """Request model untuk rekomendasi cepat."""
    max_harga: Optional[int] = Field(None, ge=0, description="Budget maksimum")
    ram: Optional[int] = Field(None, ge=1, description="RAM yang diinginkan (GB)")
    memori_internal: Optional[int] = Field(None, description="Storage yang diinginkan (GB)")
    min_baterai: Optional[int] = Field(None, description="Kapasitas baterai minimum (mAh)")
    preferred_brand: Optional[str] = Field(None, description="Brand yang disukai")
    preferred_os: Optional[str] = Field(None, description="OS yang diinginkan")
    top_k: int = Field(10, ge=1, le=50, description="Jumlah rekomendasi")
    

@router.post("/", response_model=Dict)
async def get_recommendations(request: RecommendationRequest) -> Dict:
    """
    Mendapatkan rekomendasi HP berdasarkan preferensi user.
    
    Sistem akan menggunakan CBR dengan Weighted Euclidean Distance
    untuk mencari HP yang paling sesuai dengan kebutuhan user.
    
    **Input:**
    - Spesifikasi yang diinginkan (RAM, Storage, Budget, dll)
    - Preferensi brand dan OS (opsional)
    - Custom weights (opsional)
    
    **Output:**
    - List HP yang direkomendasikan dengan similarity score
    - Penjelasan mengapa HP tersebut direkomendasikan
    """
    try:
        engine = get_cbr_engine()
        
        # Convert PhoneInput to dict
        user_input = {
            'min_harga': request.input_specs.min_harga,
            'max_harga': request.input_specs.max_harga,
            'ram': request.input_specs.ram,
            'memori_internal': request.input_specs.memori_internal,
            'min_baterai': request.input_specs.min_baterai,
            'resolusi_kamera': request.input_specs.resolusi_kamera,
            'ukuran_layar': request.input_specs.ukuran_layar,
            'min_rating': request.input_specs.min_rating,
            'preferred_brands': request.input_specs.preferred_brands,
            'preferred_os': request.input_specs.preferred_os
        }
        
        # Apply custom weights if provided
        if request.input_specs.custom_weights:
            engine.set_weights(request.input_specs.custom_weights)
        
        # Get recommendations
        result = engine.recommend(
            user_input=user_input,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/quick", response_model=Dict)
async def quick_recommendation(request: QuickRecommendRequest) -> Dict:
    """
    Rekomendasi cepat dengan parameter minimal.
    
    Endpoint ini lebih sederhana untuk penggunaan langsung.
    """
    try:
        engine = get_cbr_engine()
        
        user_input = {
            'max_harga': request.max_harga,
            'ram': request.ram,
            'memori_internal': request.memori_internal,
            'min_baterai': request.min_baterai,
            'preferred_brands': [request.preferred_brand] if request.preferred_brand else None,
            'preferred_os': request.preferred_os
        }
        
        result = engine.recommend(
            user_input=user_input,
            top_k=request.top_k,
            min_similarity=0.2
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/phones", response_model=Dict)
async def list_all_phones(
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah per halaman"),
    brand: Optional[str] = Query(None, description="Filter brand"),
    min_price: Optional[int] = Query(None, description="Harga minimum"),
    max_price: Optional[int] = Query(None, description="Harga maksimum"),
    min_ram: Optional[int] = Query(None, description="RAM minimum"),
    sort_by: Optional[str] = Query("Harga", description="Kolom untuk sorting"),
    sort_order: Optional[str] = Query("asc", description="asc atau desc")
) -> Dict:
    """
    Mendapatkan daftar semua HP dengan filter dan pagination.
    """
    try:
        engine = get_cbr_engine()
        df = engine.case_base.copy()
        
        # Apply filters
        if brand:
            df = df[df['Brand'].str.lower() == brand.lower()]
        if min_price:
            df = df[df['Harga'] >= min_price]
        if max_price:
            df = df[df['Harga'] <= max_price]
        if min_ram:
            df = df[df['Ram'] >= min_ram]
        
        # Sorting
        if sort_by in df.columns:
            ascending = sort_order.lower() == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Pagination
        total = len(df)
        start = (page - 1) * limit
        end = start + limit
        
        phones = df.iloc[start:end].to_dict('records')
        
        return {
            "success": True,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "phones": phones
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/phones/{phone_id}", response_model=Dict)
async def get_phone_detail(phone_id: int) -> Dict:
    """
    Mendapatkan detail satu HP berdasarkan ID.
    """
    try:
        engine = get_cbr_engine()
        
        phone = engine.case_base[engine.case_base['Id_hp'] == phone_id]
        
        if phone.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Phone with ID {phone_id} not found"
            )
        
        phone_data = phone.iloc[0].to_dict()
        
        # Get similar phones
        query = {
            'harga': phone_data.get('Harga'),
            'ram': phone_data.get('Ram'),
            'memori_internal': phone_data.get('Memori_internal')
        }
        
        similar = engine.retrieve(query, top_k=5, min_similarity=0.5)
        similar_phones = [
            {
                'phone': case,
                'similarity': round(sim * 100, 2)
            }
            for idx, case, sim in similar
            if case.get('Id_hp') != phone_id
        ][:4]
        
        return {
            "success": True,
            "phone": phone_data,
            "similar_phones": similar_phones
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/statistics", response_model=Dict)
async def get_statistics() -> Dict:
    """
    Mendapatkan statistik dataset.
    """
    try:
        engine = get_cbr_engine()
        stats = engine.get_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/brands", response_model=Dict)
async def get_brands() -> Dict:
    """
    Mendapatkan daftar brand yang tersedia.
    """
    try:
        engine = get_cbr_engine()
        brands = engine.case_base['Brand'].unique().tolist()
        
        brand_counts = engine.case_base['Brand'].value_counts().to_dict()
        
        return {
            "success": True,
            "brands": sorted(brands),
            "brand_counts": brand_counts
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/price-ranges", response_model=Dict)
async def get_price_ranges() -> Dict:
    """
    Mendapatkan range harga untuk filter.
    """
    try:
        engine = get_cbr_engine()
        prices = engine.case_base['Harga']
        
        return {
            "success": True,
            "min_price": int(prices.min()),
            "max_price": int(prices.max()),
            "avg_price": int(prices.mean()),
            "ranges": [
                {"label": "< 2 Juta", "min": 0, "max": 2000000},
                {"label": "2 - 5 Juta", "min": 2000000, "max": 5000000},
                {"label": "5 - 10 Juta", "min": 5000000, "max": 10000000},
                {"label": "10 - 15 Juta", "min": 10000000, "max": 15000000},
                {"label": "> 15 Juta", "min": 15000000, "max": None}
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
