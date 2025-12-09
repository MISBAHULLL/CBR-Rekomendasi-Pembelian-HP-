# Routes Package
from .recommendation import router as recommendation_router
from .evaluation import router as evaluation_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    "recommendation_router",
    "evaluation_router", 
    "admin_router",
    "health_router"
]
