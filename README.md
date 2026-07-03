# 仓库人力数据分析系统

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
| 后端 | FastAPI + SQLite + openpyxl |
| 前端 | Vue 3 + Element Plus + ECharts |
| 部署 | Windows 用户态，无需管理员权限 |

## 功能模块

- **Excel 上传解析**：自动识别仓库代码列、解析每日数据
- **趋势图表**：出勤/需求SO/3月均值三曲线对比
- **多仓对比**：最多6个仓库横向对比
- **告警引擎**：支持阈值和连续天数两种告警条件
- **AI 分析**：基于 metis-coder 模型生成繁体中文分析报告
- **数据导出**：Excel 和 PDF 格式
- **用户管理**：管理员/全局查看者/查看者三种角色

## 数据备份

复制 `backend/data/` 目录即可完成完整备份。

## 默认账号
- 用户名：admin
- 密码：admin123
- 首次登录后请及时修改密码

## 目录结构

```
├── start.bat          # 一键启动脚本
├── backend/           # 后端服务
│   ├── app/           # FastAPI 应用
│   ├── data/          # SQLite 数据库 + 上传文件
│   ├── venv/          # Python 虚拟环境
│   └── requirements.txt
├── frontend/          # Vue 3 前端源码
│   ├── src/           # 源代码
│   └── package.json
└── docs/              # 设计文档和实施计划
```
