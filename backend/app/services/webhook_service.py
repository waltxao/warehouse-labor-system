import base64
import hashlib
import httpx
import io as _io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WebhookConfig, Warehouse, DailyRecord, ThreeMonthAverage
from app.core.exceptions import AppException


TRAD_WEEKDAY_NAMES = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']


def _format_date_label(date_str: str) -> str:
    """格式化日期标签为 mm/dd 星期X"""
    try:
        parts = str(date_str).split('-')
        if len(parts) < 3:
            return str(date_str)
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(y, m, d)
        weekday = TRAD_WEEKDAY_NAMES[dt.weekday() + 1] if dt.weekday() < 6 else TRAD_WEEKDAY_NAMES[0]
        return f"{parts[1]}/{parts[2]} {weekday}"
    except Exception:
        return str(date_str)


def _parse_date_range_to_short(date_range: str) -> str:
    """将 2026-07-06~2026-07-11 转为 07/06-07/11"""
    try:
        parts = date_range.split('~')
        if len(parts) != 2:
            return date_range
        s = parts[0].strip().split('-')
        e = parts[1].strip().split('-')
        return f"{s[1]}/{s[2]}-{e[1]}/{e[2]}"
    except Exception:
        return date_range


def generate_chart_png(days, attendance, required, avg, warehouse_code, date_range, total_attendance, total_required, total_avg):
    """生成三段式图表：说明区+折线图+数据表格"""
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong', 'STSong'] + ['sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    short_range = _parse_date_range_to_short(date_range)
    fig_title = f"{short_range} {warehouse_code}倉實際出勤人數與實際需求人力情況"

    fig = plt.figure(figsize=(12, 11.5), dpi=150)
    fig.patch.set_facecolor('#FFFFFF')

    # 統一邊距
    fig.subplots_adjust(left=0.07, right=0.96, top=0.93, bottom=0.04, hspace=0.35)

    from matplotlib.gridspec import GridSpec
    gs = GridSpec(3, 1, height_ratios=[0.7, 2.5, 1.3])

    # === 標題：左對齊加粗，宋體 ===
    fig.text(0.07, 0.97, fig_title, fontsize=15, color='#1D1D1F',
             fontweight='bold', ha='left', va='top',
             fontproperties=font_manager.FontProperties(family='SimSun', weight='bold'))

    # === 第一段：說明區（圓點+統一灰色，緊湊排列） ===
    ax_desc = fig.add_subplot(gs[0])
    ax_desc.axis('off')
    desc_lines = [
        ('#2563EB', '實際出勤人數：當日實際出勤人數，（包含跟車、留倉、上門開客等人員）；'),
        ('#059669', '實際需求人力：按各工序效能係數預測的人力需求，其中：跟車、留倉計算：1人，上門開客、Partime計算：0.5人；'),
        ('#6B7280', '歷史需求人數均值：取近3個月實際出勤人數計算的平均值，用作標準線'),
    ]
    y_starts = [0.80, 0.50, 0.20]
    for color_dot, text_line, ypos in zip([d[0] for d in desc_lines], [d[1] for d in desc_lines], y_starts):
        # 畫圓點
        ax_desc.plot(0.015, ypos, 'o', markersize=6, color=color_dot,
                     transform=ax_desc.transAxes, clip_on=False)
        # 整行文字統一灰色
        ax_desc.text(0.04, ypos, text_line, fontsize=10, color='#6E6E73',
                     va='center', fontfamily='sans-serif',
                     transform=ax_desc.transAxes)

    # === 第二段：折線圖 ===
    ax = fig.add_subplot(gs[1])
    x_labels = [_format_date_label(d) for d in days]
    x = range(len(days))

    # 平滑曲線插值
    import numpy as np
    from scipy.interpolate import make_interp_spline

    def _smooth(x_vals, y_vals):
        x_arr = np.array(x_vals)
        y_arr = np.array([v if v is not None else 0 for v in y_vals], dtype=float)
        x_smooth = np.linspace(x_arr.min(), x_arr.max(), 100)
        spline = make_interp_spline(x_arr, y_arr, k=3)
        return x_smooth, spline(x_smooth)

    xs_att, ys_att = _smooth(x, attendance)
    xs_req, ys_req = _smooth(x, required)

    ax.plot(xs_att, ys_att, color='#2563EB', linewidth=2.5, label='實際出勤人數', zorder=3)
    ax.plot(x, attendance, 'o', color='#2563EB', markersize=7, zorder=4)
    ax.fill_between(xs_att, ys_att, alpha=0.08, color='#2563EB')

    ax.plot(xs_req, ys_req, color='#059669', linewidth=2, label='實際需求人力', zorder=2)
    ax.plot(x, required, 's', color='#059669', markersize=6, zorder=2)

    if avg and any(v > 0 for v in avg):
        xs_avg, ys_avg = _smooth(x, avg)
        ax.plot(xs_avg, ys_avg, color='#6B7280', linewidth=1.5, linestyle='--', label='歷史需求人數均值', zorder=1)

    ax.set_ylabel('人數', fontsize=11, color='#1D1D1F')
    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels, fontsize=9, color='#6E6E73')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#D2D2D7')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#D2D2D7')
    ax.spines['bottom'].set_color('#D2D2D7')

    for i, (a, r) in enumerate(zip(attendance, required)):
        if a is not None and a > 0:
            ax.annotate(str(int(a)), (i, a), textcoords="offset points", xytext=(0, 8),
                       ha='center', fontsize=8, color='#2563EB')
        if r is not None and r > 0:
            ax.annotate(f'{r:.1f}', (i, r), textcoords="offset points", xytext=(0, -12),
                       ha='center', fontsize=8, color='#059669')

    # === 第三段：數據表格 ===
    ax_table = fig.add_subplot(gs[2])
    ax_table.axis('off')

    def _fmt_num(v):
        if v is None or v == 0:
            return '0'
        if v == int(v):
            return str(int(v))
        return f'{v:.1f}'

    col_labels = ['指標'] + [_format_date_label(d) for d in days] + ['匯總']
    cell_text = [
        ['實際出勤人數'] + [_fmt_num(a) for a in attendance] + [_fmt_num(total_attendance)],
        ['實際需求人力'] + [_fmt_num(r) for r in required] + [_fmt_num(total_required)],
        ['歷史需求人數均值'] + [_fmt_num(a) for a in avg] + [_fmt_num(total_avg)],
    ]

    table = ax_table.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
        bbox=[0.0, 0.0, 1.0, 1.0],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    for j in range(len(col_labels)):
        cell = table[0, j]
        cell.set_facecolor('#1D1D1F')
        cell.set_text_props(color='white', fontweight='bold', fontsize=9)

    for i in range(1, 4):
        for j in range(len(col_labels)):
            cell = table[i, j]
            if i % 2 == 1:
                cell.set_facecolor('#F5F5F7')
            else:
                cell.set_facecolor('#FFFFFF')
            cell.set_text_props(fontsize=9)

    for i in range(1, 4):
        table[i, 0].set_text_props(fontweight='bold')

    for i in range(1, 4):
        table[i, len(col_labels) - 1].set_text_props(fontweight='bold', color='#2563EB')

    # === 淺灰分隔線 ===
    for gap_y in [0.780, 0.460]:
        fig.lines.append(plt.Line2D([0.07, 0.96], [gap_y, gap_y],
                                    transform=fig.transFigure, color='#E5E5EA',
                                    linewidth=0.8))

    buf = _io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='#FFFFFF')
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
    total_avg = 0
    if records:
        start_date = str(records[0].date)
        end_date = str(records[-1].date)
    else:
        start_date = end_date = iso_week

    nicknames = []
    if config.notify_users:
        nicknames = [n.strip() for n in config.notify_users.split(",") if n.strip()]
    mention_text = " ".join(f"@{n}" for n in nicknames)

    # 仅当配置了消息模板时才推送文字消息
    md_content = None
    if config.message_template:
        md_content = config.message_template.format(
            warehouse=warehouse_code,
            date_range=f"{start_date}-{end_date}",
            notify_users=mention_text,
            total_attendance=int(total_attendance),
            total_required=round(total_required, 1),
            total_avg=round(total_avg, 1) if total_avg else 0,
        )

    if "base64," in chart_base64:
        chart_base64 = chart_base64.split("base64,")[1]

    md5_hash = hashlib.md5(base64.b64decode(chart_base64)).hexdigest()

    image_payload = {
        "msgtype": "image",
        "image": {"base64": chart_base64, "md5": md5_hash}
    }

    results = []
    async with httpx.AsyncClient(timeout=30) as http_client:
        img_resp = await http_client.post(config.webhook_url, json=image_payload)
        img_data = img_resp.json()
        results.append({"type": "image", "status": img_resp.status_code, "data": img_data})
        if img_resp.status_code != 200 or img_data.get("errcode") != 0:
            raise AppException(500, f"图片消息发送失败: {img_data}")

        if md_content:
            text_payload = {
                "msgtype": "markdown",
                "markdown": {"content": md_content}
            }
            text_resp = await http_client.post(config.webhook_url, json=text_payload)
            text_data = text_resp.json()
            results.append({"type": "text", "status": text_resp.status_code, "data": text_data})
            if text_resp.status_code != 200 or text_data.get("errcode") != 0:
                raise AppException(500, f"文字消息发送失败: {text_data}")

    return {"success": True, "message": "推送成功", "details": results}


async def push_all_to_wechat(db: AsyncSession, iso_week: str, warehouse_codes: list[str]) -> dict:
    """遍历指定仓库列表（为空则遍历所有已配置 webhook 的仓库），为每个仓库生成专属图表并推送"""
    query = (
        select(WebhookConfig, Warehouse)
        .join(Warehouse, WebhookConfig.warehouse_id == Warehouse.id)
        .where(WebhookConfig.is_active == True)
    )
    if warehouse_codes:
        query = query.where(Warehouse.code.in_(warehouse_codes))
    result = await db.execute(query)
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

            # 计算周总值用于数据表格汇总列
            total_attendance = sum(attendance)
            total_required = sum(required)
            total_avg = sum(avg)

            date_range = f"{days[0]}~{days[-1]}" if days else iso_week

            # 生成三段式图表（传入周总数值用于数据表格汇总列）
            chart_base64 = generate_chart_png(
                days, attendance, required, avg, wh_code, date_range,
                total_attendance, total_required, total_avg
            )

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
