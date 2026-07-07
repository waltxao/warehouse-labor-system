# 更新日志 (CHANGELOG)

## v2.3.0 - 2026-07-07

### 新增功能

#### 推送系统全面升级
- 浮动推送按钮固定在所有页面右下角（z-index:9999），作为独立功能
- 推送对话框：选择周次 + 仓库多选（仅显示已配置且启用的 webhook）+ 定时推送设置
- 三段式图表：说明区 + 折线图（3色明显区分）+ KPI卡片
  - 实际出勤人数：蓝色 #2563EB 实线 + 圆点
  - 实际需求人力：绿色 #059669 实线 + 方块
  - 历史需求人数均值：灰色 #6B7280 虚线
- 图表全部使用繁體中文，字体优先 Microsoft JhengHei
- 说明文字使用用户指定内容（含跟车/留仓=1人、Partime=0.5人计算说明）
- WebhookConfig 新增 message_template 字段，每仓库可单独设置推送文字模板
- 模板支持变量：{warehouse} {date_range} {notify_users} {total_attendance} {total_required}
- 变量标签可点击插入到文本框光标位置
- 定时推送：APScheduler 每分钟检查，按 schedule_day + schedule_time 自动执行
- 推送配置页移除定时推送设置（保留在推送按钮对话框中）

#### 历史均值重命名
- 所有"近3月需求人力平均值"改为"历史需求人数均值"
- KPI卡片"周总均值基线"改为"周历史需求人数均值"

#### CA12 仓库均值套用
- 新增 CA12 仓库
- CA12 在当前周次之前直接套用 1450 的历史均值数据
- 当前周次及之后 CA12 正常参与均值计算

### Bug 修复

#### 配色字体修正
- 配色从 Apple 蓝橙(#007AFF/#FF9500)调整为黑白灰+蓝色点缀(#2563EB)
- 字体从 SF Pro 改为 Segoe UI（Windows 1080p 渲染流畅）
- 系统信息从页面底部移至侧边栏左下角

#### 推送功能修复
- 修复模板与 script 函数不匹配导致推送按钮无响应
- 修复 DailyRecord 无 three_month_avg 属性报错（改为从 ThreeMonthAverage 表查询）
- 修复 PageIntro 位置错误（NotificationConfigView/UsersView/SettingsView）

### 技术变更

#### 后端
- `webhook_service.py`：重写 generate_chart_png 为三段式布局（GridSpec）
- `webhook_service.py`：push_all_to_wechat 接收仓库列表参数
- `webhook.py`：新增 message_template/schedule_enabled/schedule_day/schedule_time 字段
- `webhooks.py`：新增 PUT /{id}/schedule 接口
- `main.py`：集成 APScheduler 定时任务
- `main.py`：SQLite 自动 ALTER TABLE 补列
- `average_calculator.py`：CA12 套用 1450 均值逻辑
- 新增依赖：matplotlib、apscheduler

#### 前端
- `AppLayout.vue`：浮动推送按钮 + 推送对话框 + 结果对话框
- `DashboardView.vue`：移除推送按钮（改为全局浮动）
- `NotificationConfigView.vue`：模板变量标签 + 移除定时推送字段
- `TrendChart.vue`：需求人力线改为绿色 #059669
- `webhook.ts`：pushAll 接收 warehouse_codes 数组

---

## v2.2.0 - 2026-07-06

### 新增功能

#### Apple HIG 设计系统全量重写
- 全系统配色从深蓝(#1E40AF)切换为 Apple System Colors（主色 #007AFF、强调色 #FF9500）
- 字体从 Fira Sans/Code 改为 SF Pro 系统字体栈（-apple-system）
- 卡片圆角增大至 16px，按钮 12px，弹窗 20px
- 阴影从蓝色调改为中性柔和阴影
- 过渡动画改用 spring 弹性曲线 cubic-bezier(0.34, 1.56, 0.64, 1)
- 卡片 hover 增加 scale(1.02) 微缩放效果
- 侧边栏从深蓝渐变改为 Apple Dark (#1C1C1E) 纯色
- ECharts 图表配色更新为 Apple System Colors 色板
- 移除 Google Fonts 外部依赖

#### 页面使用说明 (PageIntro)
- 新增可复用 PageIntro 组件，放置于每个页面最底部
- 每个页面配有专属使用说明（使用方法 + 图表查看方式）
- 始终可见，浅灰背景 #F2F2F7，圆角 16px
- AppLayout 侧边栏左下角显示系统版本信息

#### 企业微信推送功能
- 新增 WebhookConfig 数据模型（每仓库一条配置）
- 新增推送配置页面（/notifications），仅管理员可访问
- 配置内容：企业微信 Webhook URL + 通知人员昵称（逗号分隔）
- 推送消息包含：图表截图（PNG base64）+ markdown 富文本 + @昵称
- 后端推送服务支持企业微信群机器人 image + markdown 双消息发送

### 技术变更

#### 后端新增
- `backend/app/models/webhook.py`：WebhookConfig 模型
- `backend/app/schemas/webhook.py`：Pydantic schemas
- `backend/app/services/webhook_service.py`：企业微信推送服务
- `backend/app/api/v1/webhooks.py`：CRUD + push API（管理员权限）
- `backend/app/main.py`：添加 lifespan 自动建表

#### 前端新增
- `frontend/src/components/PageIntro.vue`：页面说明组件
- `frontend/src/views/NotificationConfigView.vue`：推送配置页面
- `frontend/src/api/webhook.ts`：推送 API 客户端
- `frontend/src/router/index.ts`：新增 /notifications 路由
- `frontend/src/components/AppLayout.vue`：侧边栏新增推送配置菜单 + 版本信息
- `frontend/src/i18n/zh-CN.ts` / `zh-TW.ts`：新增推送配置翻译

#### 设计系统文件
- `frontend/src/assets/main.css`：CSS 变量全面替换为 Apple HIG
- 全部 9 个 Vue 视图 + 3 个组件：scoped 样式更新
- `frontend/src/components/TrendChart.vue`：ECharts 配色更新
- `frontend/src/components/ComparisonChart.vue`：配色 + 字体更新

### 文档
- 新增设计文档 `docs/superpowers/specs/2026-07-06-v2.2.0-apple-hig-webhook-design.md`

---

## v2.1.0 - 2026-07-06

### 新增功能

#### 语言切换功能
- 系统新增简体中文 / 繁体中文切换功能
- 在顶部导航栏添加语言选择下拉框
- 语言偏好自动保存至 localStorage，刷新页面后保持
- 移除英文支持，仅保留简体中文和繁体中文

#### 设计系统升级
- 引入 Data-Dense Dashboard 风格（后已被 v2.2.0 Apple HIG 取代）
- 侧边栏深蓝渐变，字体 Fira Sans + Fira Code（后已被 v2.2.0 SF Pro 取代）

#### 周次筛选器
- 总览、多仓对比、AI分析、告警管理页面均新增周次下拉筛选器
- 周次列表从后端 API 动态获取

#### 仓库筛选器优化
- 所有页面的仓库下拉框统一显示仓库代码

#### 图表说明区
- 总览页图表上方新增说明区

### Bug 修复

#### Excel 解析器
- 修复 offset 偏移错误，6/29 周一数据缺失问题

#### 图表显示
- 修复图表画布背景黑色问题
- 修复 X 轴标签旋转导致文字重叠（改为两行显示）
- 修复 X 轴日期星期错位（UTC 时区偏移）
- 修复图表重复图例

#### 中文显示
- 修复 Vue 文件中文显示为 Unicode 转义序列

#### SPA 路由
- 修复刷新子路由返回 404

#### 数字格式
- 全系统统一：整数显示整数，非整数最多两位小数

#### AI 分析 401 错误
- 请求头添加 Content-Type
- 添加 API Key 检查和详细错误提示

#### 总览页
- 选单仓时隐藏仓库数量卡片
- "周总出勤人数" 更正为 "周总出勤人次"

### 优化
- 多仓对比、数据上传、AI分析、告警管理页面设计统一
- 移除无数据仓库（101I、1020）
- 移除满足率指标
