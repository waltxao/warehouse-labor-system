import json
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import DailyRecord, Warehouse, AIAnalysisLog
from app.config import settings
from app.core.exceptions import AppException

PROMPT_TEMPLATE = {
    "weekly_compare": """你是一個倉庫人力資源分析專家。請用繁體中文撰寫分析報告。

以下是 {warehouse_code} 倉庫第 {iso_week} 週與上週的人力數據對比：

{data_table}

請分析：
1. 出勤與需求匹配度
2. 人力節省效率變化
3. 異常波動識別
4. 改善建議

輸出格式：Markdown""",
    "multi_warehouse": """你是一個倉庫人力資源分析專家。請用繁體中文撰寫多倉對比分析報告。

以下是 {warehouse_codes} 倉庫第 {iso_week} 週的人力數據矩陣：

{data_table}

請分析：
1. 各倉庫出勤與需求匹配度比較
2. 人力效率排名
3. 異常倉庫識別
4. 跨倉改善建議

輸出格式：Markdown""",
    "monthly_trend": """你是一個倉庫人力資源分析專家。請用繁體中文撰寫月趨勢分析報告。

以下是 {warehouse_code} 倉庫近 4 週的人力數據趨勢：

{data_table}

請分析：
1. 出勤趨勢變化
2. 需求波動分析
3. 人力配置效率趨勢
4. 未來預測與建議

輸出格式：Markdown""",
    "anomaly_detection": """你是一個倉庫人力資源分析專家。請用繁體中文撰寫異常檢測報告。

以下是 {warehouse_code} 倉庫第 {iso_week} 週的數據及統計摘要：

{data_table}

統計摘要：
{stat_summary}

請分析：
1. 異常數據點識別
2. 可能原因推測
3. 風險評估
4. 處理建議

輸出格式：Markdown""",
}


async def run_ai_analysis(
    db: AsyncSession,
    analysis_type: str,
    warehouse_codes: list[str],
    iso_week: str,
    user_id: int,
) -> str:
    # 查询数据构建 prompt
    prompt = await _build_prompt(db, analysis_type, warehouse_codes, iso_week)

    # 创建日志记录
    log = AIAnalysisLog(
        analysis_type=analysis_type,
        warehouse_ids=json.dumps(warehouse_codes),
        iso_week=iso_week,
        status="pending",
        created_by=user_id,
    )
    db.add(log)
    await db.flush()

    # 调用 AI API
    try:
        report_content, pt, ct = await _call_ai_api(prompt)
        log.report_content = report_content
        log.prompt_tokens = pt
        log.completion_tokens = ct
        log.status = "completed"
    except Exception as e:
        log.status = "failed"
        log.report_content = str(e)
        report_content = f"AI 分析失败: {e}"

    await db.commit()
    return report_content


async def _build_prompt(db: AsyncSession, analysis_type: str, warehouse_codes: list[str], iso_week: str) -> str:
    template = PROMPT_TEMPLATE.get(analysis_type, PROMPT_TEMPLATE["weekly_compare"])

    # 查询数据
    data_rows = []
    for code in warehouse_codes:
        wh = await db.execute(select(Warehouse).where(Warehouse.code == code))
        warehouse = wh.scalar_one_or_none()
        if not warehouse:
            continue
        records = await db.execute(
            select(DailyRecord)
            .where(DailyRecord.warehouse_id == warehouse.id, DailyRecord.iso_week == iso_week)
            .order_by(DailyRecord.date)
        )
        for r in records.scalars().all():
            data_rows.append(
                f"| {r.date} | {code} | {r.actual_attendance} | {r.required_headcount_so} | {r.labor_savings} | {r.work_fulfillment_rate} |"
            )

    data_table = "日期 | 仓库 | 出勤 | 需求SO | 节省 | 满足率\n" + "\n".join(data_rows)

    return template.format(
        warehouse_code=warehouse_codes[0] if warehouse_codes else "",
        warehouse_codes=", ".join(warehouse_codes),
        iso_week=iso_week,
        data_table=data_table,
        stat_summary=f"数据行数: {len(data_rows)}",
    )


async def _call_ai_api(prompt: str) -> tuple[str, int, int]:
    if not settings.AI_API_KEY:
        raise AppException("AI API Key 未配置，请在 backend/.env 文件中设置 AI_API_KEY")

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                f"{settings.AI_API_BASE_URL}v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL_ID,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AppException("AI API Key 无效或已过期，请检查 backend/.env 中的 AI_API_KEY 配置")
            raise AppException(f"AI API 请求失败: HTTP {e.response.status_code} - {e.response.text[:200]}")
        except httpx.RequestError as e:
            raise AppException(f"AI API 网络请求失败: {str(e)}")
