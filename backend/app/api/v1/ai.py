from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.services.ai_analyzer import run_ai_analysis
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.post("/analyze")
async def analyze(
    req: AIAnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await run_ai_analysis(db, req.type, req.warehouse_codes, req.iso_week, user.id)
    return ApiResponse[AIAnalysisResponse](data=AIAnalysisResponse(report=report, log_id=0))
