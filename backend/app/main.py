"""
CBR Phone Recommendation API - FastAPI application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .config import settings
from .routes import (
    recommendation_router,
    evaluation_router,
    admin_router,
    health_router
)
from .cbr import get_cbr_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup dan shutdown handler."""
    # Startup
    logger.info("Starting CBR Phone Recommendation API...")
    
    # Pre-load CBR engine dan case base
    try:
        engine = get_cbr_engine()
        logger.info(f"Case base loaded: {len(engine.case_base)} phones")
    except Exception as e:
        logger.error(f"Error loading case base: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CBR Phone Recommendation API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Sistem Rekomendasi Handphone dengan Case-Based Reasoning
    
    API ini menyediakan endpoint untuk:
    - 📱 **Rekomendasi HP** berdasarkan preferensi user
    - ⚖️ **Manajemen Bobot** untuk Weighted Euclidean Distance
    - 📊 **Evaluasi Model** dengan berbagai skenario training-testing
    - 🔧 **Admin Dashboard** untuk pengelolaan sistem
    
    ### Algoritma
    Sistem menggunakan **Weighted Euclidean Distance** dengan formula:
    
    ```
    d(x, y) = √(Σ wᵢ × (xᵢ - yᵢ)²)
    ```
    
    Di mana:
    - `x` = vektor fitur query (input user)
    - `y` = vektor fitur case (HP dalam database)
    - `wᵢ` = bobot untuk fitur ke-i (dalam persentase)
    
    ### CBR Cycle
    1. **RETRIEVE** - Mencari HP yang mirip dari database
    2. **REUSE** - Menggunakan HP tersebut sebagai rekomendasi
    3. **REVISE** - Menyesuaikan berdasarkan preferensi tambahan
    4. **RETAIN** - Menyimpan kasus baru (feedback)
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk development, konkretkan di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware untuk menambahkan waktu proses ke response header."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Register routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(recommendation_router, prefix=settings.API_PREFIX)
app.include_router(evaluation_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint dengan informasi API."""
    return {
        "message": "Welcome to CBR Phone Recommendation API",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """Informasi tentang API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": f"{settings.API_PREFIX}/health",
            "recommendations": f"{settings.API_PREFIX}/recommendations",
            "evaluation": f"{settings.API_PREFIX}/evaluation",
            "admin": f"{settings.API_PREFIX}/admin"
        },
        "algorithm": "Weighted Euclidean Distance",
        "cbr_phases": ["Retrieve", "Reuse", "Revise", "Retain"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
