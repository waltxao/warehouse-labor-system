from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.upload import router as upload_router
from app.api.v1.warehouses import router as wh_router
from app.api.v1.trends import router as trends_router
from app.api.v1.comparison import router as comp_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(upload_router)
api_router.include_router(wh_router)
api_router.include_router(trends_router)
api_router.include_router(comp_router)
