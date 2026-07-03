# API 配置说明

## 环境变量配置

复制 ackend/.env.example 为 ackend/.env，然后填写以下配置：

`ash
cp backend/.env.example backend/.env
`

### 必须修改的项

| 变量名 | 说明 | 示例 |
|--------|------|------|
| SECRET_KEY | JWT 签名密钥，务必改为随机长字符串 | my-super-secret-key-2024 |
| INITIAL_ADMIN_PASSWORD | 管理员初始密码 | your-secure-password |
| AI_API_KEY | AI 分析服务的 API Key | sk-xxxxxxxxxxxx |

### AI 服务配置

| 变量名 | 说明 |
|--------|------|
| AI_API_BASE_URL | AI 服务地址（OpenAI 兼容接口） |
| AI_API_KEY | AI 服务的 API Key |
| AI_MODEL_ID | 使用的模型 ID |

配置方式：
1. 在 ackend/.env 文件中填写 AI_API_KEY
2. 或通过环境变量设置：set AI_API_KEY=sk-xxxxx
3. 重启服务生效

### 安全建议

- 生产环境务必修改 SECRET_KEY
- 定期更换 AI_API_KEY
- ackend/.env 文件已被 .gitignore 排除，不会上传到 Git
- 切勿将真实 API Key 写入 .env.example 或任何代码文件