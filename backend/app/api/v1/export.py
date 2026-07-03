import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.services.export_service import export_excel, export_pdf

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/excel")
async def export_xls(
    warehouse_code: str = Query(...),
    iso_week: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await export_excel(db, warehouse_code, iso_week)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={warehouse_code}_{iso_week}.xlsx"},
    )


@router.get("/pdf")
async def export_pdf_file(
    warehouse_code: str = Query(...),
    iso_week: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await export_pdf(db, warehouse_code, iso_week)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={warehouse_code}_{iso_week}.pdf"},
    )
