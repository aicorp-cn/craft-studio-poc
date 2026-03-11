
基于提供的TinyLMClient代码，进行全面深入的架构分析，深入理解其功能设计、实现机制和扩展能力。

然后，基于继承TinyLMClient类设计和开发一个专门的业务功能客户端（TinyTaskClient），该客户端专注于文本处理和AI业务场景。具体要求如下：

**业务场景定义：**

1. **分类功能** - `classify`方法：
   - 方法签名：`async def classify(self, input: str, choices: List[str], model: str = "gpt-4") -> str`
   - 功能：根据输入文本内容，从给定的选项列表中选择最合适的标签
   - 示例：`await client.classify("This product sucks.", ["positive", "negative", "neutral"]) → "negative"`
   - 要求：支持多语言输入，确保分类结果的准确性和一致性

2. **摘要功能** - `summary`方法：
   - 方法签名：`async def summary(self, input: str, max_length: Optional[int] = None, model: str = "gpt-4") -> str`
   - 功能：理解输入内容并生成简洁准确的摘要
   - 支持指定最大长度参数，可选地控制摘要长度
   - 要求：保持原文核心信息和上下文语境，生成自然表述、流畅可读的摘要文本

3. **思维导图功能** - `mindmap`方法：
   - 方法签名：`async def mindmap(self, input: str, format_type: FormatType = FormatType.MARKDOWN, model: str = "gpt-4") -> str`
   - 功能：解析输入内容，提取关键信息，按照指定格式生成思维导图结构
   - FormatType枚举应包含：Mermaid(MARKDOWN)、XMind(XML),FreeMind(XML)、Web Mind Map(JSON)等格式选项
   - 要求：生成的思维导图结构清晰，层次分明，标准反映原文语义和上下文语境，符合指定格式规范
​
4. **内容理解功能** - `understandit`方法：
   - 方法签名：`async def understandit(self, input: Union[str, bytes, Dict], media_type: Optional[str] = None, model: str = "gpt-4-vision") -> str`
   - 功能：识别和理解给定的媒体内容（文本、图像、音频等），根据内容类型返回相应的理解结果
   - 支持多种输入格式：文本字符串、二进制数据、包含URL的字典等
   - 要求：能够自动检测内容类型或根据media_type参数处理，返回准确的理解结果，支持多模态内容识别

5. **标记关键内容** - `mark_key_content`方法：
   - 方法签名：`async def mark_key_content(self, input: str) -> str`
   - 功能：理解输入内容并通过在原文上添加特定标识标签`<key_content></key_content>`以标记出核心或关键语义的内容（如句子、段落等）。为后续内容可读性优化显示组件提供识别依据
   - 要求：准确识别核心语义内容，使用指定的XML标签格式进行标记，保持原文结构完整性

6. **翻译功能** - `translate`方法：
   - 方法签名：`async def translate(self, input: str, target_language: str, source_language: Optional[str] = None, model: str = "gpt-4") -> str`
   - 功能：理解输入内容并根据目标语言进行翻译，自动选择最佳翻译策略
   - 要求：支持多种语言翻译，保持原文语义准确性，处理专业术语和上下文语境

7. **情感识别功能** - `emotion_recog`方法：
   - 方法签名：`async def emotion_recog(self, input: str, model: str = "gpt-4") -> Dict[str, Any]`
   - 功能：分析输入内容的情感类型，识别情感偏向，并提供分析结论的依据
   - 返回值：包含情感类型、情感强度、分析依据等信息的字典
   - 要求：能够识别多种情感类型（积极、消极、中性等），提供量化的情感强度评估和分析依据


**设计要求：**

1. **继承设计**：TinyTaskClient必须继承TinyLMClient，复用其HTTP连接管理、认证、错误处理等基础设施
2. **异步支持**：所有业务方法必须支持异步操作，与TinyLMClient的异步架构保持一致
3. **错误处理**：集成TinyLMClient的错误处理机制，对业务逻辑进行适当的异常捕获和处理
4. **参数验证**：实现输入参数的验证，确保业务方法的健壮性
5. **类型安全**：使用适当的类型注解，确保代码的可维护性和IDE支持
6. **配置灵活性**：支持模型选择、超参数配置等灵活性配置选项

**交付要求：**

在开始具体编码实现之前，请提供完整、具体、详尽的设计与实现方案，包括但不限于：
- TinyTaskClient类的整体架构设计
- 各业务方法的详细实现逻辑和算法思路
- 与TinyLMClient的集成方式和扩展点说明
- 错误处理和异常情况的应对策略
- 性能考虑和优化建议
- 使用示例和测试用例设计
- FormatType枚举的具体定义和各格式的实现细节

必须等候我的评审通过后，才能执行具体编码工作。