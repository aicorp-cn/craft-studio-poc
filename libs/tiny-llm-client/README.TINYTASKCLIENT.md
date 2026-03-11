# TinyTaskClient

## 项目概述

TinyTaskClient是基于TinyLMClient开发的专门业务功能客户端，专注于文本处理和AI业务场景。
该客户端继承了TinyLMClient的基础设施，包括HTTP连接管理、认证、错误处理等，并提供了7个高级文本处理功能。

## 实现的功能

### 1. 分类功能 (`classify`)
- **方法签名**: `async def classify(self, input: str, choices: List[str], model: str = "gpt-4") -> str`
- **功能**: 根据输入文本内容，从给定的选项列表中选择最合适的标签
- **特点**: 支持多语言输入，确保分类结果的准确性和一致性
- **示例**: `await client.classify("This product sucks.", ["positive", "negative", "neutral"]) → "negative"`

### 2. 摘要功能 (`summary`)
- **方法签名**: `async def summary(self, input: str, max_length: Optional[int] = None, model: str = "gpt-4") -> str`
- **功能**: 理解输入内容并生成简洁准确的摘要
- **特点**: 支持指定最大长度参数，可选地控制摘要长度，保持原文核心信息和上下文语境
- **示例**: `await client.summary("Long article text...", max_length=100)`

### 3. 思维导图功能 (`mindmap`)
- **方法签名**: `async def mindmap(self, input: str, format_type: FormatType = FormatType.MARKDOWN, model: str = "gpt-4") -> str`
- **功能**: 解析输入内容，提取关键信息，按照指定格式生成思维导图结构
- **特点**: 支持多种格式（Mermaid、XMind、FreeMind、Web Mind Map），生成的思维导图结构清晰，层次分明
- **示例**: `await client.mindmap("AI concepts overview", format_type=FormatType.MARKDOWN)`

### 4. 内容理解功能 (`understandit`)
- **方法签名**: `async def understandit(self, input: Union[str, bytes, Dict], media_type: Optional[str] = None, model: str = "gpt-4-vision") -> str`
- **功能**: 识别和理解给定的媒体内容（文本、图像、音频等），根据内容类型返回相应的理解结果
- **特点**: 支持多种输入格式，能够自动检测内容类型或根据media_type参数处理，支持多模态内容识别
- **示例**: `await client.understandit(b"image_bytes_data", model="gpt-4-vision")`

### 5. 标记关键内容 (`mark_key_content`)
- **方法签名**: `async def mark_key_content(self, input: str) -> str`
- **功能**: 理解输入内容并通过在原文上标记关键或核心语义的内容（如句子、段落）上添加特定标识标签`<key_content></key_content>`
- **特点**: 准确识别核心语义内容，使用指定的XML标签格式进行标记，保持原文结构完整性
- **示例**: `await client.mark_key_content("In machine learning...")`

### 6. 翻译功能 (`translate`)
- **方法签名**: `async def translate(self, input: str, target_language: str, source_language: Optional[str] = None, model: str = "gpt-4") -> str`
- **功能**: 理解输入内容并根据目标语言进行翻译，自动选择最佳翻译策略
- **特点**: 支持多种语言翻译，保持原文语义准确性，处理专业术语和上下文语境
- **示例**: `await client.translate("Hello world", target_language="中文")`

### 7. 情感识别功能 (`emotion_recog`)
- **方法签名**: `async def emotion_recog(self, input: str, model: str = "gpt-4") -> Dict[str, Any]`
- **功能**: 分析输入内容的情感类型，识别情感偏向，并提供分析结论的依据
- **特点**: 能够识别多种情感类型（积极、消极、中性等），提供量化的情感强度评估和分析依据
- **示例**: `await client.emotion_recog("I love this product!")`

## 架构设计

### 继承设计
- TinyTaskClient继承自TinyLMClient，复用了其HTTP连接管理、认证、错误处理等基础设施
- 所有业务方法都支持异步操作，与TinyLMClient的异步架构保持一致

### 枚举类型
- 创建了`FormatType`枚举，支持四种思维导图格式：
  - `MARKDOWN`: Mermaid格式
  - `XMIND`: XMind XML格式
  - `FREEMIND`: FreeMind XML格式
  - `WEB_MIND_MAP`: Web Mind Map JSON格式

### 类型安全
- 使用适当的类型注解，确保代码的可维护性和IDE支持
- 所有参数和返回值都有明确的类型定义

## 设计特点

### 错误处理
- 集成TinyLMClient的错误处理机制
- 对业务逻辑进行适当的异常捕获和处理

### 参数验证
- 实现输入参数的验证，确保业务方法的健壮性

### 配置灵活性
- 支持模型选择、超参数配置等灵活性配置选项

### 性能优化
- 使用适当的温度设置以获得最佳结果
- 合理的token限制以控制成本和响应时间

## 使用示例

```python
import asyncio
from tiny_lm_client import TinyTaskClient, FormatType

async def main():
    async with TinyTaskClient(
        base_url="https://api.openai.com/v1",
        api_key="your-api-key",
        max_retries=3,
        timeout=60.0
    ) as client:
        
        # 文本分类
        result = await client.classify(
            input="This product is amazing!",
            choices=["positive", "negative", "neutral"],
            model="gpt-4"
        )
        
        # 摘要生成
        summary = await client.summary(
            input="Long article text here...",
            max_length=100,
            model="gpt-4"
        )
        
        # 思维导图
        mindmap = await client.mindmap(
            input="AI concepts overview",
            format_type=FormatType.MARKDOWN,
            model="gpt-4"
        )
        
        # 内容理解
        understanding = await client.understandit(
            input="Python is a programming language...",
            model="gpt-4"
        )
        
        # 标记关键内容
        marked = await client.mark_key_content(
            input="In machine learning, supervised learning is a method..."
        )
        
        # 翻译
        translated = await client.translate(
            input="Hello, how are you?",
            target_language="中文",
            model="gpt-4"
        )
        
        # 情感识别
        emotion = await client.emotion_recog(
            input="I love this product!",
            model="gpt-4"
        )

if __name__ == "__main__":
    asyncio.run(main())
```
