# TinyLMClient 环境设置指南

## 环境要求

- Python >= 3.8
- pip 包管理器

## 环境安装步骤

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装包

```bash
# 开发模式安装（推荐用于开发）
pip install -e .

# 或者普通安装
pip install .
```

### 3. 安装开发依赖（可选）

```bash
pip install -e .[dev]
```

## 验证安装

```python
import tiny_lm_client
print(f"Version: {tiny_lm_client.__version__}")

from tiny_lm_client import TinyLMClient, TinyTaskClient
print("✓ 安装成功")
```

## 依赖说明

- **httpx** >= 0.24.0, < 1.0.0 - 异步HTTP客户端
- **Python** >= 3.8 - 语言版本要求

## 示例使用

```python
import asyncio
from tiny_lm_client import TinyLMClient, ChatCompletionRequest, Message
from tiny_lm_client.enums import Role

async def main():
    # 创建客户端
    client = TinyLMClient(
        base_url="https://api.openai.com/v1",
        api_key="your-api-key"
    )
    
    # 创建请求
    request = ChatCompletionRequest(
        model="gpt-4",
        messages=[Message(role=Role.USER, content="Hello, world!")]
    )
    
    # 使用客户端（注意：这会发送实际请求）
    # response = await client.chat_completion(request)

asyncio.run(main())
```

## 虚拟环境管理

```bash
# 激活环境
source venv/bin/activate

# 升级包（开发时）
pip install -e .

# 退出环境
deactivate
```