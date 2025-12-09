"""
Health Check Routes
===================
Endpoint untuk health check dan status aplikasi.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check() -> Dict:
    """
    Basic health check endpoint.
    
    Returns:
        Status aplikasi
    """
    return {
        "status": "healthy",
        "message": "CBR Phone Recommendation API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict:
    """
    Readiness check - memastikan semua dependencies siap.
    
    Returns:
        Status readiness
    """
    from ..cbr import get_cbr_engine
    
    try:
        engine = get_cbr_engine()
        stats = engine.get_statistics()
        
        return {
            "status": "ready",
            "database_loaded": True,
            "total_phones": stats.get("total_phones", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/info")
async def app_info() -> Dict:
    """
    Informasi aplikasi.
    
    Returns:
        Info lengkap aplikasi
    """
    from ..config import settings
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Sistem Rekomendasi Handphone berbasis Case-Based Reasoning",
        "algorithm": "Weighted Euclidean Distance",
        "features": [
            "Phone recommendation based on user preferences",
            "Customizable attribute weights",
            "Model evaluation with multiple scenarios",
            "Admin dashboard for weight management"
        ],
        "documentation": "/docs",
        "timestamp": datetime.now().isoformat()
    }
