from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.core.exceptions import AppException, app_exception_handler
from app.database import engine, Base
import app.models  # noqa: F401  确保所有模型被导入以注册到 Base.metadata
from app.api.v1 import api_router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动创建缺失的表（SQLite，create_all 是幂等的）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="仓库人力数据分析系统", version="1.0.0", lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/api/v1/health")
async def health():
    return {"code": 0, "message": "success", "data": {"status": "ok"}}


app.include_router(api_router)

# 静态资源目录
static_dir = os.path.join(os.path.dirname(__file__), "static")

# SPA 回退：非 API 路径一律返回 index.html，由前端路由处理
if os.path.isdir(static_dir):
    # 先挂载静态资源（JS/CSS/图片等）
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(request: Request, full_path: str):
        """所有非 API 路径回退到 index.html，支持前端 SPA 路由"""
        # API 路径直接 404
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # 尝试匹配静态文件
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # 其他路径返回 index.html（SPA 路由）
        index_path = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

        return JSONResponse({"detail": "Not Found"}, status_code=404)
