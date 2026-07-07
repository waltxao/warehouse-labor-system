import base64
import hashlib
import httpx
import io as _io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WebhookConfig, Warehouse, DailyRecord, ThreeMonthAverage
from app.core.exceptions import AppException


WEEKDAY_NAMES = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']


def _format_date_label(date_str: str) -> str:
    """格式化日期标签为 mm/dd 星期X"""
    try:
        parts = str(date_str).split('-')
        if len(parts) < 3:
            return str(date_str)
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(y, m, d)
        weekday = WEEKDAY_NAMES[dt.weekday() + 1] if dt.weekday() < 6 else WEEKDAY_NAMES[0]
        return f"{parts[1]}/{parts[2]} {weekday}"
    except Exception:
        return str(date_str)


def generate_chart_png(days: list, attendance: list, required: list, avg: list, warehouse_code: str, date_range: str) -> str:
    """用 matplotlib 生成趋势图表，返回 base64 字符串"""
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    x_labels = [_format_date_label(d) for d in days]
    x = range(len(days))

    # 出勤人数
    ax.plot(x, attendance, color='#2563EB', linewidth=2.5, marker='o', markersize=6, label='实际出勤人数', zorder=3)
    ax.fill_between(x, attendance, alpha=0.1, color='#2563EB')

    # 需求人力
    ax.plot(x, required, color='#3B82F6', linewidth=2, marker='s', markersize=5, label='实际需求人力', zorder=2)

    # 均值基线
    if avg and any(v > 0 for v in avg):
        ax.plot(x, avg, color='#6B7280', linewidth=1.5, linestyle='--', label='历史均值基线', zorder=1)

    ax.set_xlabel('', fontsize=11, color='#1D1D1F')
    ax.set_ylabel('人数', fontsize=11, color='#1D1D1F')
    ax.set_title(f'{warehouse_code}倉實際出勤人數與實際需求人力情況 ({date_range})', fontsize=13, color='#1D1D1F', fontweight='bold', pad=15)

    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels, fontsize=9, color='#6E6E73', rotation=0)

    ax.legend(loc='upper right', fontsize=9, framealpha=0.9, facecolor='#FFFFFF', edgecolor='#D2D2D7')
    ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#D2D2D7')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#D2D2D7')
    ax.spines['bottom'].set_color('#D2D2D7')

    # 数据标签
    for i, v in enumerate(attendance):
        if v is not None:
            ax.annotate(str(int(v)), (i, v), textcoords="offset points", xytext=(0, 8),
                       ha='center', fontsize=8, color='#2563EB')

    plt.tight_layout()
    buf = _io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


async def push_chart_to_wechat(
    db: AsyncSession,
    warehouse_code: str,
    iso_week: str,
    chart_base64: str,
) -> dict:
    """推送单个仓库的图表到企业微信"""
    wh_result = await db.execute(select(Warehouse).where(Warehouse.code == warehouse_code))
    warehouse = wh_result.scalar_one_or_none()
    if not warehouse:
        raise AppException(404, f"仓库 {warehouse_code} 不存在")

    cfg_result = await db.execute(
        select(WebhookConfig).where(WebhookConfig.warehouse_id == warehouse.id)
    )
    config = cfg_result.scalar_one_or_none()
    if not config:
        raise AppException(404, f"仓库 {warehouse_code} 未配置企业微信 Webhook")
    if not config.is_active:
        raise AppException(400, f"仓库 {warehouse_code} 的 Webhook 配置已禁用")

    records_result = await db.execute(
        select(DailyRecord)
        .where(DailyRecord.warehouse_id == warehouse.id, DailyRecord.iso_week == iso_week)
        .order_by(DailyRecord.date)
    )
    records = records_result.scalars().all()

    total_attendance = sum(r.actual_attendance or 0 for r in records)
    total_required = sum(r.required_headcount_so or 0 for r in records)
    if records:
        start_date = str(records[0].date)
        end_date = str(records[-1].date)
    else:
        start_date = end_date = iso_week

    nicknames = []
    if config.notify_users:
        nicknames = [n.strip() for n in config.notify_users.split(",") if n.strip()]
    mention_text = " ".join(f"@{n}" for n in nicknames)

    md_content = f"{warehouse_code}倉實際出勤人數與實際需求人力情況图表\n\n"
    md_content += f"**以上 {start_date}-{end_date} {warehouse_code}倉實際出勤人數與實際需求人力情況，请{mention_text} 留意**"

    if "base64," in chart_base64:
        chart_base64 = chart_base64.split("base64,")[1]

    md5_hash = hashlib.md5(base64.b64decode(chart_base64)).hexdigest()

    image_payload = {
        "msgtype": "image",
        "image": {"base64": chart_base64, "md5": md5_hash}
    }
    text_payload = {
        "msgtype": "markdown",
        "markdown": {"content": md_content}
    }

    results = []
    async with httpx.AsyncClient(timeout=30) as http_client:
        img_resp = await http_client.post(config.webhook_url, json=image_payload)
        img_data = img_resp.json()
        results.append({"type": "image", "status": img_resp.status_code, "data": img_data})
        if img_resp.status_code != 200 or img_data.get("errcode") != 0:
            raise AppException(500, f"图片消息发送失败: {img_data}")

        text_resp = await http_client.post(config.webhook_url, json=text_payload)
        text_data = text_resp.json()
        results.append({"type": "text", "status": text_resp.status_code, "data": text_data})
        if text_resp.status_code != 200 or text_data.get("errcode") != 0:
            raise AppException(500, f"文字消息发送失败: {text_data}")

    return {"success": True, "message": "推送成功", "details": results}


async def push_all_to_wechat(db: AsyncSession, iso_week: str) -> dict:
    """遍历所有已配置 webhook 的仓库，为每个仓库生成专属图表并推送"""
    # 获取所有启用的 webhook 配置
    result = await db.execute(
        select(WebhookConfig, Warehouse)
        .join(Warehouse, WebhookConfig.warehouse_id == Warehouse.id)
        .where(WebhookConfig.is_active == True)
    )
    rows = result.all()

    if not rows:
        raise AppException(404, "没有已配置且启用的推送仓库")

    push_results = []
    success_count = 0
    fail_count = 0

    for config, warehouse in rows:
        wh_code = warehouse.code
        try:
            # 查询该仓库该周的数据
            records_result = await db.execute(
                select(DailyRecord)
                .where(DailyRecord.warehouse_id == warehouse.id, DailyRecord.iso_week == iso_week)
                .order_by(DailyRecord.date)
            )
            records = records_result.scalars().all()

            if not records:
                push_results.append({
                    "code": wh_code,
                    "success": False,
                    "message": f"仓库 {wh_code} 在 {iso_week} 无数据"
                })
                fail_count += 1
                continue

            days = [str(r.date) for r in records]
            attendance = [r.actual_attendance or 0 for r in records]
            required = [r.required_headcount_so or 0 for r in records]

            # 从 ThreeMonthAverage 表查询历史均值
            dow_list = [r.day_of_week for r in records]
            avg_map = {}
            if dow_list:
                avg_result = await db.execute(
                    select(ThreeMonthAverage).where(
                        ThreeMonthAverage.warehouse_id == warehouse.id,
                        ThreeMonthAverage.iso_week == iso_week,
                        ThreeMonthAverage.day_of_week.in_(dow_list)
                    )
                )
                for a in avg_result.scalars().all():
                    avg_map[a.day_of_week] = a.average_value
            avg = [avg_map.get(dow, 0) for dow in dow_list]

            date_range = f"{days[0]}~{days[-1]}" if days else iso_week

            # 生成图表
            chart_base64 = generate_chart_png(days, attendance, required, avg, wh_code, date_range)

            # 推送
            push_result = await push_chart_to_wechat(db, wh_code, iso_week, chart_base64)
            push_results.append({
                "code": wh_code,
                "success": True,
                "message": "推送成功"
            })
            success_count += 1

        except Exception as e:
            push_results.append({
                "code": wh_code,
                "success": False,
                "message": str(e) if "AppException" not in str(type(e)) else e.detail if hasattr(e, 'detail') else str(e)
            })
            fail_count += 1

    return {
        "success": True,
        "message": f"推送完成: {success_count} 成功, {fail_count} 失败",
        "total": len(rows),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": push_results
    }
