# 更新日志 (CHANGELOG)

## v2.1.0 - 2026-07-06

### 新增功能

#### 语言切换功能
- 系统新增简体中文 / 繁体中文切换功能
- 在顶部导航栏添加语言选择下拉框
- 语言偏好自动保存至 localStorage，刷新页面后保持
- 移除英文支持，仅保留简体中文和繁体中文
- 所有页面文案均支持双语切换

#### 设计系统升级
- 引入 `ui-ux-pro-max` 设计系统，采用 Data-Dense Dashboard 风格
- 全系统统一配色方案：主色 #1E40AF、强调色 #D97706、背景 #F8FAFC
- 侧边栏改为深蓝渐变 (#1E3A8A → #1E40AF)
- 字体引入 Fira Sans（正文）+ Fira Code（数字），通过 Google Fonts 加载
- 所有卡片统一为圆角 12px、浅蓝边框 #DBEAFE、微阴影
- 悬停动效：translateY(-2px) + 阴影加深，过渡 200ms

#### 周次筛选器
- 总览、多仓对比、AI分析、告警管理页面均新增周次下拉筛选器
- 周次列表从后端 API `/trends/weeks/list` 动态获取
- 下拉标签格式："2026-W27 (06/29-07/04)"
- 默认选中最新周次

#### 仓库筛选器优化
- 所有页面的仓库下拉框统一显示仓库代码（code）
- 总览页支持单仓筛选查询
- 多仓对比页支持多选仓库（最多6个）

#### 图表说明区
- 总览页图表上方新增说明区，采用琥珀色边框 + 浅琥珀背景
- 包含用户指定的繁体中文定义说明
- Ps 备注行

### Bug 修复

#### Excel 解析器
- 修复 `range(1,9)` 应为 `range(0,8)` 的偏移错误
- 6/29（周一）数据此前被跳过，现已正确解析
- 总记录数从 90 条恢复为 108 条（6天 × 18仓库）

#### 图表显示
- 修复图表画布背景为黑色的问题（添加 `backgroundColor: "#ffffff"`）
- 修复 X 轴标签旋转 15° 导致文字重叠遮挡的问题
  - 改为两行显示格式：第一行日期 "06/29"，第二行星期 "星期一"
  - 去掉旋转（rotate: 0），增加底部边距
- 修复 X 轴日期星期错位问题（JavaScript `new Date("2026-06-29")` UTC 时区偏移）
  - 改为手动解析 `new Date(y, m-1, d)` 避免时区偏移
- 修复图表重复图例问题（隐藏 ECharts 内置 legend，保留自定义 HTML 图例）
- 修复图表标题重复（ECharts 标题 + HTML 标题）

#### 中文显示
- 修复 Vue 文件中文字符显示为 `\uXXXX` Unicode 转义序列的问题
- 重写所有前端组件使用实际 UTF-8 编码中文字符

#### SPA 路由
- 修复刷新 `/dashboard` 等子路由返回 404 的问题
- 添加 FastAPI catch-all 路由回退到 `index.html`

#### 数字格式
- 全系统统一数字格式：整数显示整数，非整数最多显示两位小数
- 去掉末尾零（如 38.50 → 38.5，38.00 → 38）
- 应用于图表数据标签、tooltip、KPI 统计卡片

#### AI 分析 401 错误
- 修复 AI 分析接口返回 401 Unauthorized 的问题
- 请求头添加 `Content-Type: application/json`
- 添加 API Key 未配置检查，提供清晰错误提示
- 401 错误专门提示"AI API Key 无效或已过期，请检查 backend/.env 中的 AI_API_KEY 配置"
- 添加 HTTPStatusError 和 RequestError 异常处理

#### 总览页统计卡片
- 选单仓时隐藏"仓库数量"统计卡，统计卡片从 4 列变为 3 列
- "周总出勤人数" 更正为 "周总出勤人次"

### 优化

#### 页面设计统一
- 多仓对比、数据上传、AI分析、告警管理页面统一为总览页的设计风格
- 所有页面采用顶部操作栏布局：左侧筛选器 + 右侧按钮
- 查询/分析按钮使用主色填充，导出按钮使用边框样式
- 表格样式统一：圆角、浅蓝边框、表头浅蓝背景

#### 数据清理
- 移除无数据的仓库（101I、1020）
- 剩余 18 个有效仓库
- 同步更新 `init_data.py` 防止重新初始化时加回

#### 满足率指标
- 从多仓对比和告警管理页面的指标选项中移除"满足率"

### 技术变更

#### 后端
- `backend/app/main.py`：添加 SPA 路由回退
- `backend/app/api/v1/trends.py`：新增 `/trends/weeks/list` 接口
- `backend/app/services/excel_parser.py`：修复 offset 偏移
- `backend/app/services/ai_analyzer.py`：增强错误处理
- `backend/app/config.py`：AI API 配置
- `backend/init_data.py`：更新仓库列表

#### 前端
- `frontend/src/i18n/`：新增 zh-CN.ts、zh-TW.ts，移除 en.ts
- `frontend/src/components/AppLayout.vue`：添加语言切换器
- `frontend/src/components/TrendChart.vue`：两行标签 + 白色背景
- `frontend/src/components/ComparisonChart.vue`：日期+星期 + 数据标签
- `frontend/src/views/DashboardView.vue`：动态统计卡片 + 数字格式
- `frontend/src/views/ComparisonView.vue`：统一设计 + 移除满足率
- `frontend/src/views/UploadView.vue`：统一设计
- `frontend/src/views/AIAnalysisView.vue`：统一设计 + 周次下拉
- `frontend/src/views/AlertsView.vue`：统一设计 + 周次下拉
- `frontend/src/assets/main.css`：全局设计 tokens + Google Fonts

### 安全
- 确保 `.env` 文件不被提交至 Git（已在 .gitignore 中）
- `.env.example` 中 API Key 使用占位符 `your-api-key-here`
- AI API Key 仅存在于本地 `.env` 文件中
