# 仓库人力数据分析系统

> v2.3.0 · 作者：Walt · © 2026

## 快速启动

### 环境要求
- Python 3.10+
- Node.js 18+（仅首次构建前端需要）

### 首次部署
1. 编辑 `backend/.env` 配置管理员账号和 AI API
2. 构建前端：`cd frontend && npm install && npm run build`
3. 双击 `start.bat` 启动
4. 浏览器访问 http://localhost:8000

### 日常使用
直接双击 `start.bat` 即可启动系统，无需重复构建前端。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLite + openpyxl + matplotlib + APScheduler |
| 前端 | Vue 3 + Element Plus + ECharts |
| 部署 | Windows 用户态，无需管理员权限 |

## 功能模块

### 数据管理
- **Excel 上传解析**：自动识别仓库代码列、解析每日数据，上传后自动重算历史均值
- **历史均值计算**：基于近3个月实际出勤人数计算平均值，CA12 仓库自动套用 1450 数据
- **数据导出**：Excel 和 PNG 格式

### 数据分析
- **趋势图表**：实际出勤人数（蓝色）、实际需求人力（绿色）、历史需求人数均值（灰色虚线）三曲线对比
- **多仓对比**：最多6个仓库横向对比，支持柱状图和折线图切换
- **KPI 卡片**：周总出勤人次、周总需求人力、周历史需求人数均值
- **告警引擎**：支持阈值和连续天数两种告警条件
- **AI 分析**：基于 metis-coder 模型生成繁体中文分析报告

### 企业微信推送
- **浮动推送按钮**：固定在所有页面右下角，随时可用
- **推送对话框**：选择周次和仓库（仅显示已配置且启用的），支持定时推送
- **三段式图表**：说明区 + 折线图（3色明显区分）+ KPI卡片，全部繁體中文
- **自定义文字模板**：每仓库可单独设置推送文字，支持变量：
  - `{warehouse}` 仓库代码
  - `{date_range}` 日期范围
  - `{notify_users}` 被提醒人（@昵称）
  - `{total_attendance}` 出勤人次
  - `{total_required}` 需求人力
- **定时推送**：设置每周几定时自动推送，APScheduler 每分钟检查
- **推送配置页**：管理 Webhook URL、通知人员昵称、文字模板

### 系统功能
- **用户管理**：管理员/全局查看者/查看者三种角色，仓库级别权限控制
- **语言切换**：简体中文 / 繁体中文
- **页面说明**：每个页面底部配有使用说明（PageIntro 组件）

## 设计系统

- **配色**：黑白灰 + 蓝色点缀（主色 #2563EB）
- **字体**：Segoe UI + PingFang SC（Windows 1080p 优化）
- **侧边栏**：深色 #1D1D1F，底部显示版本信息
- **动效**：spring 弹性曲线 cubic-bezier(0.34, 1.56, 0.64, 1)

## 数据备份

复制 `backend/data/` 目录即可完成完整备份。

## 默认账号
- 用户名：admin
- 密码：admin123
- 首次登录后请及时修改密码

## 目录结构

```
├── start.bat              # 一键启动脚本
├── CHANGELOG.md           # 更新日志
├── backend/               # 后端服务
│   ├── app/
│   │   ├── models/        # 数据模型（含 WebhookConfig）
│   │   ├── api/v1/        # API 路由（含 webhooks 推送接口）
│   │   ├── services/      # 业务逻辑（含 webhook_service 推送服务）
│   │   └── main.py        # FastAPI 入口（含 APScheduler 定时任务）
│   ├── data/              # SQLite 数据库 + 上传文件
│   ├── venv/              # Python 虚拟环境
│   └── requirements.txt
├── frontend/              # Vue 3 前端源码
│   ├── src/
│   │   ├── components/    # 组件（AppLayout, TrendChart, PageIntro 等）
│   │   ├── views/         # 页面视图
│   │   ├── api/           # API 客户端（含 webhook.ts）
│   │   └── assets/        # 样式资源
│   └── package.json
└── docs/                  # 设计文档
```

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### v2.3.0 主要变更
- 推送系统全面升级：浮动按钮 + 选择对话框 + 三段式图表 + 自定义模板 + 定时推送
- 历史均值重命名：近3月需求人力平均值 → 历史需求人数均值
- CA12 仓库均值套用 1450 数据
- 配色字体修正：黑白灰+蓝色点缀 + Segoe UI
