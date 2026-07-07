# 更新日志 (CHANGELOG)

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
- AppLayout 底部全局显示：系统版本 v2.2.0 · 作者：Walt · © 2026

#### 企业微信推送功能
- 新增 WebhookConfig 数据模型（每仓库一条配置）
- 新增推送配置页面（/notifications），仅管理员可访问
- 配置内容：企业微信 Webhook URL + 通知人员手机号（逗号分隔）
- 总览页选单仓时显示"推送到企业微信"按钮
- 推送消息包含：图表截图（PNG base64）+ 数据摘要文字 + @通知人员
- 文字格式："以上{start}-{end} {warehouse}倉實際出勤人數與實際需求人力情況，請留意"
- 后端推送服务支持企业微信群机器人 image + text 双消息发送

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
- `frontend/src/components/AppLayout.vue`：侧边栏新增推送配置菜单 + 底部版本信息
- `frontend/src/views/DashboardView.vue`：新增推送按钮
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
