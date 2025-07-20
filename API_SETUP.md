# API 密钥配置指南

## 🔑 快速设置

### 1. 复制环境配置文件
```bash
cp .env.example .env
```

### 2. 获取 API 密钥

选择以下任一提供商：

#### DeepSeek (推荐)
- 访问：https://platform.deepseek.com/api_keys
- 注册账户并创建 API 密钥
- 复制密钥（格式：`sk-xxxxxxxxxxxxxxxx`）

**官方 API 文档**: https://api-docs.deepseek.com/
**Base URL**: `https://api.deepseek.com` (或 `https://api.deepseek.com/v1`)
**模型**: `deepseek-chat` (指向 DeepSeek-V3-0324)

#### OpenAI
- 访问：https://platform.openai.com/api-keys
- 登录并创建新的 API 密钥
- 复制密钥（格式：`sk-xxxxxxxxxxxxxxxx`）

#### Azure OpenAI
- 访问：https://portal.azure.com/
- 创建 Azure OpenAI 资源
- 获取 API 密钥和端点

### 3. 配置 .env 文件

编辑 `.env` 文件，替换占位符：

```bash
# DeepSeek 配置（推荐）
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key-here

# 或者使用 OpenAI
# OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# 或者使用 Azure OpenAI
# AZURE_OPENAI_API_KEY=your-azure-api-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### 4. 验证配置

运行验证脚本：
```bash
python setup_api_keys.py
```

### 5. 启动应用

```bash
chainlit run interfaces/chainlit_app.py
```

## 🚨 常见问题

### 问题：Authentication Fails, Your api key is invalid

**原因：**
- API 密钥无效或过期
- 使用了示例占位符密钥
- API 密钥格式错误

**解决方案：**
1. 检查 `.env` 文件中的 API 密钥
2. 确保密钥是真实有效的
3. 验证密钥格式正确（通常以 `sk-` 开头）
4. 检查账户余额和配额

### 问题：No valid API keys found

**原因：**
- 没有配置任何 API 密钥
- `.env` 文件不存在
- 环境变量未正确加载

**解决方案：**
1. 创建 `.env` 文件
2. 添加至少一个有效的 API 密钥
3. 重启应用

### 问题：HTTP 401 Unauthorized

**原因：**
- API 密钥无效
- 账户余额不足
- API 密钥权限不足

**解决方案：**
1. 验证 API 密钥有效性
2. 检查账户余额
3. 确认 API 密钥权限

## 💡 提示

- **DeepSeek** 通常提供更好的性价比
- **OpenAI** 提供最稳定的服务
- **Azure OpenAI** 适合企业用户
- 定期检查 API 使用量和余额
- 不要在代码中硬编码 API 密钥
- 将 `.env` 文件添加到 `.gitignore`

## 🔧 高级配置

### 自定义模型参数

在 `model_config.yaml` 中调整：

```yaml
config:
  model: deepseek-chat
  temperature: 0.7
  max_tokens: 4000
  top_p: 1.0
```

### 多提供商配置

可以同时配置多个 API 密钥，系统会自动选择可用的：

```bash
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
AZURE_OPENAI_API_KEY=your-azure-key
```

## 📞 获取帮助

如果仍有问题：
1. 运行 `python setup_api_keys.py` 进行诊断
2. 检查应用日志
3. 查看提供商的 API 文档
4. 联系技术支持