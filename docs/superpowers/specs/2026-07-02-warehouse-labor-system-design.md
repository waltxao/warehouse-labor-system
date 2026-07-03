# 仓库人力数据分析系统 — 设计规格

## 目标

构建一套仓库人力数据分析系统。用户（admin）每周上传 Warehouse Daily Report Excel 文件，系统自动解析「关键数据汇总」Sheet 中各仓库的关键人力指标，为每个仓库生成独立趋势分析图，并提供多仓对比、异常告警、数据导出及 AI 智能分析能力。系统需在无管理员密码的 Windows 电脑上零安装部署。

## 技术栈

- **前端：** Vue 3 + Element Plus + ECharts + Pinia + Vue Router + Axios + Vite + vue-i18n（中/英）+ markdown-it
- **后端：** FastAPI（Python 3.11+）+ SQLAlchemy 2.0（异步）+ Alembic + openpyxl + python-jose/passlib + structlog + pydantic-settings + aiosqlite
- **数据层：** SQLite（单文件，零安装）+ 本地文件存储
- **AI 集成：** OpenAI 兼容 API（`https://llm.sjdistributor.com/`，模型 `metis-coder`，报告输出繁体中文）
- **部署：** Windows 用户态一键启动（venv + uvicorn），单进程托管 API + 静态资源

## 架构

### 部署架构

单进程运行：FastAPI 通过 StaticFiles 中间件同时托管 REST API 和 Vue 构建产物。SQLite 数据库文件存放在 `data/` 目录，备份只需复制整个 `data/` 文件夹。无需 Docker、Nginx、Redis、PostgreSQL 或管理员权限。

### 项目目录结构

```
warehouse-labor-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI 入口，挂载静态资源 + 路由
│   │   ├── config.py          # pydantic-settings（读取 .env）
│   │   ├── database.py        # SQLAlchemy 异步引擎 + session
│   │   ├── models/            # ORM 模型
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── api/v1/            # API 路由
│   │   ├── services/          # 业务逻辑层
│   │   ├── core/              # 安全、依赖注入、异常处理
│   │   └── static/            # Vue 构建产物
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example
│   └── init_data.py
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── stores/
│   │   ├── router/
│   │   ├── api/
│   │   ├── i18n/
│   │   └── assets/
│   ├── package.json
│   └── vite.config.ts
├── docs/superpowers/
│   ├── specs/
│   └── plans/
├── data/                       # SQLite + 上传文件存储
│   ├── warehouse.db
│   └── uploads/
├── start.bat
└── README.md
```

### 部署流程（start.bat）

1. 检查 Python 3.11+ 是否安装
2. 在 `backend/` 下创建 venv
3. `pip install -r requirements.txt`
4. `alembic upgrade head`（创建/迁移数据库）
5. `init_data.py`（插入初始仓库和管理员）
6. 检查 `frontend/dist/` 是否存在，不存在则提示先构建前端
7. 启动 `uvicorn app.main:app --host 0.0.0.0 --port 8000`
8. 浏览器自动打开 `http://localhost:8000`

## 全局约束

- YAGNI：不实现需求文档中未明确要求的功能
- DRY：公共逻辑提取到 services 层，不重复
- 所有日期使用 ISO 8601 格式（`YYYY-MM-DD`）
- 周次格式 `YYYY-Www`（如 `2026-W24`）
- API 基础路径 `/api/v1`，Bearer Token（JWT）认证
- Access Token 有效期 2 小时，Refresh Token 有效期 7 天
- 统一响应格式 `{code, message, data}`，错误码：0/400/401/403/404/409/500
- 分页参数 `?page&page_size`

## 数据库表结构

### users

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | |
| username | TEXT | UNIQUE NOT NULL | 用户名 |
| password_hash | TEXT | NOT NULL | bcrypt 哈希 |
| role | TEXT | NOT NULL | admin / global_viewer / viewer |
| is_active | BOOLEAN | DEFAULT TRUE | 账号状态 |
| created_at | DATETIME | DEFAULT NOW | |
| updated_at | DATETIME | DEFAULT NOW | |

### warehouses

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | |
| code | TEXT | UNIQUE NOT NULL | 仓库代码（如 101D、CA11） |
| name | TEXT | | 仓库名称（可选，默认用 code） |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | DATETIME | | |
| updated_at | DATETIME | | |

### user_warehouse_bindings

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| user_id | INTEGER | FK → users.id | |
| warehouse_id | INTEGER | FK → warehouses.id | |
| UNIQUE(user_id, warehouse_id) | | | 防重复绑定 |

### weekly_reports

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| iso_week | TEXT | UNIQUE NOT NULL | 如 `2026-W24` |
| start_date | DATE | NOT NULL | 周一日期 |
| end_date | DATE | NOT NULL | 周六日期 |
| filename | TEXT | NOT NULL | 原始文件名 |
| uploaded_by | INTEGER | FK → users.id | |
| upload_log_id | INTEGER | FK → upload_logs.id | |
| created_at | DATETIME | | |

### daily_records

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| weekly_report_id | INTEGER | FK → weekly_reports.id | |
| warehouse_id | INTEGER | FK → warehouses.id | |
| date | DATE | NOT NULL | |
| day_of_week | INTEGER | NOT NULL | 1=周一 ~ 6=周六 |
| iso_week | TEXT | NOT NULL | |
| system_headcount | REAL | | 系统人数 |
| actual_attendance | REAL | | 实际出勤人数 |
| required_headcount_so | REAL | | 实际工作需求人数(SO) |
| labor_savings | REAL | | 节省人数 |
| work_fulfillment_rate | REAL | | 实际工作满足率(%) |
| UNIQUE(warehouse_id, date) | | | 覆盖时更新 |

### three_month_averages

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| warehouse_id | INTEGER | FK → warehouses.id | |
| iso_week | TEXT | NOT NULL | 当前周次 |
| day_of_week | INTEGER | NOT NULL | 1~6 |
| average_value | REAL | NOT NULL | 均值 |
| is_partial | BOOLEAN | DEFAULT FALSE | 历史不足3个月时 true |
| sample_count | INTEGER | | 参与计算的样本数 |
| computed_at | DATETIME | | |
| UNIQUE(warehouse_id, iso_week, day_of_week) | | | |

### alert_rules

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| name | TEXT | NOT NULL | 规则名称 |
| metric | TEXT | NOT NULL | attendance / savings / fulfillment_rate |
| condition_type | TEXT | NOT NULL | threshold / consecutive_days |
| operator | TEXT | NOT NULL | gt / lt / gte / lte / eq |
| threshold_value | REAL | | 阈值 |
| consecutive_days | INTEGER | | 连续天数 |
| scope | TEXT | NOT NULL | single / all |
| warehouse_id | INTEGER | FK NULL | scope=single 时指定 |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_by | INTEGER | FK → users.id | |
| created_at | DATETIME | | |

### alert_logs

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| alert_rule_id | INTEGER | FK → alert_rules.id | |
| warehouse_id | INTEGER | FK → warehouses.id | |
| trigger_date | DATE | | |
| trigger_value | REAL | | |
| status | TEXT | | active / acknowledged / resolved |
| created_at | DATETIME | | |

### upload_logs

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| filename | TEXT | | |
| file_size | INTEGER | | |
| status | TEXT | | pending / parsed / failed |
| error_message | TEXT | | |
| new_warehouses | TEXT (JSON) | | 新发现仓库列表 |
| missing_warehouses | TEXT (JSON) | | 缺失仓库列表 |
| uploaded_by | INTEGER | FK → users.id | |
| created_at | DATETIME | | |

### ai_analysis_logs

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| analysis_type | TEXT | | weekly_compare / multi_warehouse / monthly_trend / anomaly_detection |
| warehouse_ids | TEXT (JSON) | | |
| iso_week | TEXT | | |
| prompt_tokens | INTEGER | | |
| completion_tokens | INTEGER | | |
| report_content | TEXT | | Markdown 报告内容 |
| status | TEXT | | pending / completed / failed |
| created_by | INTEGER | FK → users.id | |
| created_at | DATETIME | | |

### audit_logs

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| user_id | INTEGER | FK → users.id | |
| action | TEXT | | login / upload / overwrite / export / ai_analysis / user_manage / alert_rule |
| resource_type | TEXT | | |
| resource_id | TEXT | | |
| detail | TEXT (JSON) | | |
| ip_address | TEXT | | |
| created_at | DATETIME | | |

## 用户角色与权限

| 角色 | 权限 |
|------|------|
| admin | 系统管理权限，可管理所有仓库、用户、告警规则，可上传数据 |
| global_viewer | 全局只读，可查看所有数据、多仓对比、AI 分析、导出，不可上传或管理 |
| viewer | 仅可查看绑定仓库数据、触发本仓 AI 分析、导出本仓数据 |

## Excel 解析引擎

### Excel 结构

仓库代码作为列标题（C~S 列），17 个仓库：`101D, 1800, 101G, 101I, 102H, 1200, 1050, 1020, 1400, 1450, 1600, 101A, 101B, 102B, 1070, CA11, GA11`。指标按行分组，每日数据行包含周一~周六共 6 行 + 周平均行。

### 解析流程

1. openpyxl 加载工作簿，模糊匹配定位「关键数据汇总」Sheet
2. 扫描表头行，正则识别仓库代码列：`re.compile(r'^(\d{3,4}[A-Z]?|[A-Z]{2}\d{2})$')`，记录 `{列索引: warehouse_code}` 映射
3. 新仓库自动创建记录；与数据库已有仓库对比，识别缺失仓库
4. 逐行扫描「项目」列文本，识别指标类别：
   - `每日節省人數` → labor_savings
   - `每日系統人數` → system_headcount
   - `實際出勤人數` → actual_attendance
   - `實際工作需求人數` → required_headcount_so（直接取值）
   - `實際工作滿足率` → work_fulfillment_rate
5. 在每个指标类别内逐行读取日期列，解析日期格式（`MM/DD` 或 `MM/DD/YYYY` 或 Excel 序列号），忽略周日，计算 ISO 周次
6. 返回解析报告：`{iso_week, start_date, end_date, warehouses_found, new_warehouses, missing_warehouses, records_parsed}`

### 覆盖机制（force_overwrite）

1. 首次上传检测到该 ISO 周已有数据 → 返回 409 Conflict + `{conflict: true, iso_week}`
2. 用户确认覆盖 → 带 `force_overwrite=true` 重新请求
3. 后端删除该周所有 `daily_records` + `weekly_reports` → 重新解析插入
4. 重新计算受影响的 `three_month_averages`

## 近3月需求人力平均值

### 计算规则

滚动窗口：以当前上传周为基准，往前推 3 个月，取同一星期几的「实际工作需求人数(SO)」求平均。

- 同仓库 + 同星期维度（如仓库 101D + 周三）
- 历史不足 3 个月时 `is_partial=true`，记录 `sample_count`
- 每次新周数据上传后自动重算（FastAPI BackgroundTasks 触发）
- 计算结果写入 `three_month_averages` 表，查询时零延迟

## API 设计

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录，返回 access_token + refresh_token |
| POST | `/api/v1/auth/refresh` | 刷新 access_token |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |

### 仓库管理

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/warehouses` | 全部角色 | 仓库列表（viewer 只返回绑定仓库） |
| POST | `/api/v1/warehouses` | admin | 新增仓库 |
| PATCH | `/api/v1/warehouses/{id}` | admin | 编辑仓库 |

### 数据上传

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/api/v1/upload` | admin | 上传 Excel，返回解析报告 |
| GET | `/api/v1/upload/logs` | 全部角色 | 上传历史（viewer 限本仓） |

上传请求支持 `force_overwrite` 参数（boolean），true 时覆盖同周已有数据。

### 趋势分析

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/trends/{warehouse_code}` | viewer+ | 单仓趋势数据（含3月均值） |
| GET | `/api/v1/trends/{warehouse_code}/chart` | viewer+ | 图表数据（三条曲线格式化） |

### 多仓对比

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/api/v1/comparison` | global_viewer+ | body: `{warehouse_codes: [...], iso_week}` |

### 告警

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/alerts/rules` | 全部角色 | 规则列表 |
| POST | `/api/v1/alerts/rules` | admin | 创建规则 |
| PATCH | `/api/v1/alerts/rules/{id}` | admin | 编辑规则 |
| GET | `/api/v1/alerts/logs` | 全部角色 | 告警日志（viewer 限本仓） |
| PATCH | `/api/v1/alerts/logs/{id}` | admin | 确认/解决告警 |

### AI 分析

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/api/v1/ai/analyze` | 全部角色 | body: `{type, warehouse_codes, iso_week}` |
| GET | `/api/v1/ai/logs` | 全部角色 | 分析历史（viewer 限本仓） |

### 导出

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/export/excel` | viewer+ | 参数：warehouse_code, iso_week |
| GET | `/api/v1/export/pdf` | viewer+ | 参数：warehouse_code, iso_week |

viewer 角色只能导出绑定仓库数据。

### 用户管理

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/v1/users` | admin | 用户列表 |
| POST | `/api/v1/users` | admin | 创建用户 |
| PATCH | `/api/v1/users/{id}` | admin | 编辑用户/绑定仓库 |

### 统一响应格式

```json
{ "code": 0, "message": "success", "data": {} }
```

错误码：0=成功, 400=参数错误, 401=未认证, 403=无权限, 404=不存在, 409=冲突, 500=服务器错误

## 前端架构

### 页面路由

| 路由 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录页 | 公开 |
| `/dashboard` | 总览仪表盘（所有仓库概览卡片） | viewer+ |
| `/trends/:warehouseCode` | 单仓趋势分析（核心图表页） | viewer+ |
| `/comparison` | 多仓对比页 | global_viewer+ |
| `/upload` | 数据上传页 | admin |
| `/alerts` | 告警管理页 | viewer+ |
| `/ai-analysis` | AI 分析页 | viewer+ |
| `/users` | 用户管理页 | admin |
| `/settings` | 系统设置 | admin |

### Pinia Stores

| Store | 职责 |
|-------|------|
| authStore | token 管理、用户信息、权限判断 |
| warehouseStore | 仓库列表、当前选中仓库 |
| trendStore | 趋势数据缓存 |
| alertStore | 告警规则与日志 |
| uiStore | 语言切换、侧边栏状态 |

### 核心图表

**TrendChart.vue — 单仓趋势图：**
- ECharts 折线图，X 轴周一~周六
- 三条曲线：实际出勤人数（绿色实线 `#16a34a`）、实际工作需求人数 SO（蓝色实线 `#2563eb`）、近3月需求均值（橙色虚线 `#f59e0b`）
- 支持 Tooltip 悬停、图例点击切换、dataZoom 缩放
- 导出按钮 → 生成 PNG 下载

**ComparisonChart.vue — 多仓对比：**
- 支持柱状图/折线图切换
- 最多 6 仓同时对比
- 指标选择器（出勤/需求/节省/满足率）

### i18n

中/英双语切换。AI 报告固定输出繁体中文。UI 语言跟随用户选择，默认中文。

## 告警引擎

### 数据完整性告警（自动）

每次上传后自动检查：数据库中有记录的仓库 vs Excel 中出现的仓库。缺失仓库 → 生成 alert_log（status=active），在仪表盘和上传报告中标记。

### 规则引擎告警（可配置）

| 条件类型 | 说明 | 示例 |
|----------|------|------|
| threshold | 单次值越界 | 出勤人数 < 50 |
| consecutive_days | 连续 N 天越界 | 满足率 < 80% 连续 3 天 |

每次新数据上传后，遍历所有 active 规则，对受影响仓库的 daily_records 执行检测。触发则写入 alert_logs。

规则作用域：`single`（仅监控指定仓库）、`all`（监控所有仓库，每个仓库独立判断）。

## AI 分析

### 四种分析类型

| 类型 | 说明 | Prompt 构建 |
|------|------|-------------|
| weekly_compare | 周对比：本周 vs 上周 | 注入两周数据表格 |
| multi_warehouse | 多仓对比：选定仓库横向对比 | 注入多仓数据矩阵 |
| monthly_trend | 月趋势：近 4 周趋势分析 | 注入 4 周 daily_records |
| anomaly_detection | 异常检测：识别异常波动 | 注入数据 + 统计摘要 |

### 调用流程

1. 前端提交分析请求（类型 + 仓库 + 周次）
2. 后端查询数据，构建结构化 Prompt（繁体中文指令）
3. 调用 `https://llm.sjdistributor.com/` 的 `metis-coder` 模型
4. 返回 Markdown 格式报告（繁体中文）
5. 记录到 ai_analysis_logs（含 token 用量）

### AI 配置

- Base URL: `https://llm.sjdistributor.com/`
- API Key: 通过环境变量 `AI_API_KEY` 配置
- Model: `metis-coder`
- 报告语言：繁体中文

## 导出

| 格式 | 实现 | 内容 |
|------|------|------|
| Excel | openpyxl 生成 | 原始数据 + 汇总行 |
| PDF | reportlab 生成 | 图表截图 + 数据表格 |
| PNG | 前端 ECharts getDataURL | 图表直接导出 |

viewer 角色只能导出绑定仓库数据。

## 审计日志

通过 FastAPI 中间件自动记录以下操作：
- 登录成功/失败
- 数据上传/覆盖
- 导出操作
- AI 分析请求
- 用户管理操作
- 告警规则变更

每条记录包含：user_id, action, resource_type, resource_id, detail(JSON), ip_address, timestamp。

## 环境变量配置（.env）

```ini
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/warehouse.db

# JWT
SECRET_KEY=<随机生成>
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# 初始管理员
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=<部署时设置>

# AI 配置
AI_API_BASE_URL=https://llm.sjdistributor.com/
AI_API_KEY=your-api-key-here
AI_MODEL_ID=metis-coder

# 文件存储
UPLOAD_DIR=./data/uploads

# 日志
LOG_LEVEL=INFO
```

## 初始数据

`init_data.py` 脚本插入：
- 17 个仓库：`101D, 1800, 101G, 101I, 102H, 1200, 1050, 1020, 1400, 1450, 1600, 101A, 101B, 102B, 1070, CA11, GA11`
- 1 个管理员账号（从环境变量读取用户名和密码）
