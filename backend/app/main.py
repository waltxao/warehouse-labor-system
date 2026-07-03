from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.exceptions import AppException, app_exception_handler
import os

app = FastAPI(title="仓库人力数据分析系统", version="1.0.0")

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/api/v1/health")
async def health():
    return {"code": 0, "message": "success", "data": {"status": "ok"}}


# 静态资源（部署时存在 dist 则挂载）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
