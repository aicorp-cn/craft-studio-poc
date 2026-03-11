import asyncio
import json
import base64
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse

from ..core.client import TinyLMClient
from ..entities.requests.chat_completion_request import ChatCompletionRequest
from ..entities.message import Message
from ..enums.role import Role
from ..enums.format_type import FormatType


class TinyTaskClient(TinyLMClient):
    """专门的业务功能客户端，继承TinyLMClient，专注于文本处理和AI业务场景
    
    提供一系列高级文本处理功能，包括分类、摘要、思维导图、内容理解等。
    继承TinyLMClient的HTTP连接管理、认证、错误处理等基础设施。
    
    主要功能包括：
    - classify: 文本分类 - 根据输入文本从选项中选择最合适的标签
    - summary: 摘要生成 - 生成保留核心信息的简洁摘要
    - mindmap: 思维导图 - 解析内容并按指定格式生成结构化思维导图
    - understandit: 内容理解 - 支持多模态输入的理解功能
    - mark_key_content: 标记关键内容 - 识别并标记核心语义内容
    - translate: 翻译 - 支持多种语言的翻译功能
    - emotion_recog: 情感识别 - 分析文本情感类型和强度
    """
    
    async def mindmap(self, input: str, format_type: FormatType = FormatType.MARKDOWN, model: str = "gpt-4") -> str:
        """解析输入内容，提取关键信息，按照指定格式生成思维导图结构
        
        Args:
            input: 输入的文本内容
            format_type: 输出格式类型，默认为MARKDOWN（Mermaid格式）
            model: 使用的AI模型，默认为gpt-4
            
        Returns:
            按照指定格式生成的思维导图字符串
        """
        # 根据格式类型生成相应的提示词
        if format_type == FormatType.MARKDOWN:
            prompt = f"""
            请将以下内容转换为Mermaid格式的思维导图。只需要返回Mermaid代码，不要包含其他解释。

            内容：{input}

            Mermaid格式示例：
            ```mermaid
            mindmap
              root((中心主题))
                分支1
                  子分支1
                  子分支2
                分支2
                  子分支3
                  子分支4
            ```
            """
        elif format_type == FormatType.XMIND:
            prompt = f"""
            请将以下内容转换为XMind兼容的XML格式思维导图。只需要返回XML代码，不要包含其他解释。

            内容：{input}

            XML格式示例：
            <?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/XLink" version="2.0">
              <sheet id="..." timestamp="...">
                <topic id="..." structure-class="...">
                  <title>中心主题</title>
                  <children>
                    <topics type="attached">
                      <topic id="...">
                        <title>分支1</title>
                      </topic>
                    </topics>
                  </children>
                </topic>
              </sheet>
            </xmap-content>
            """
        elif format_type == FormatType.FREEMIND:
            prompt = f"""
            请将以下内容转换为FreeMind兼容的XML格式思维导图。只需要返回XML代码，不要包含其他解释。

            内容：{input}

            XML格式示例：
            <map version="1.0.1">
              <node TEXT="中心主题">
                <node TEXT="分支1"/>
                <node TEXT="分支2"/>
              </node>
            </map>
            """
        elif format_type == FormatType.WEB_MIND_MAP:
            prompt = f"""
            请将以下内容转换为JSON格式的思维导图。只需要返回JSON代码，不要包含其他解释。

            内容：{input}

            JSON格式示例：
            {{
              "name": "中心主题",
              "children": [
                {{
                  "name": "分支1",
                  "children": [
                    {{"name": "子分支1"}},
                    {{"name": "子分支2"}}
                  ]
                }},
                {{
                  "name": "分支2",
                  "children": [
                    {{"name": "子分支3"}},
                    {{"name": "子分支4"}}
                  ]
                }}
              ]
            }}
            """
        else:
            # 默认使用MARKDOWN格式
            prompt = f"""
            请将以下内容转换为Mermaid格式的思维导图。只需要返回Mermaid代码，不要包含其他解释。

            内容：{input}

            Mermaid格式示例：
            ```mermaid
            mindmap
              root((中心主题))
                分支1
                  子分支1
                  子分支2
                分支2
                  子分支3
                  子分支4
            ```
            """
        
        # 构建聊天请求
        request = ChatCompletionRequest(
            model=model,
            messages=[Message(role=Role.USER, content=prompt)],
            temperature=0.3,  # 较低的温度以获得更一致的格式
            max_tokens=2000
        )
        
        # 发送请求并获取响应
        response = await self.chat_completion(request)
        return response.choices[0].message.content.strip()
    
    async def classify(self, input: str, choices: List[str], model: str = "gpt-4") -> str:
        """根据输入文本内容，从给定的选项列表中选择最合适的标签
        
        Args:
            input: 输入的文本内容
            choices: 可选的标签列表
            model: 使用的AI模型，默认为gpt-4
            
        Returns:
            从choices中选择的最匹配标签
        """
        # 创建分类提示词
        choices_str = '", "'.join(choices)
        prompt = f"""
        请根据以下文本内容，从提供的选项中选择最合适的标签：
        
        文本：{input}
        
        选项：["{choices_str}"]
        
        请只返回选择的标签，不要包含其他解释或文字。
        """
        
        # 构建聊天请求
        request = ChatCompletionRequest(
            model=model,
            messages=[Message(role=Role.USER, content=prompt)],
            temperature=0.1,  # 低温度以获得更一致的分类结果
            max_tokens=50
        )
        
        # 发送请求并获取响应
        response = await self.chat_completion(request)
        result = response.choices[0].message.content.strip()
        
        # 验证结果是否在选项中
        for choice in choices:
            if choice.lower() in result.lower() or result.lower() in choice.lower():
                return choice
        
        # 如果没有找到匹配项，返回原始结果
        return result
    
    async def summary(self, input: str, max_length: Optional[int] = None, model: str = "gpt-4") -> str:
        """理解输入内容并生成简洁准确的摘要
        
        Args:
            input: 输入的文本内容
            max_length: 摘要的最大长度（可选），用于控制摘要长度
            model: 使用的AI模型，默认为gpt-4
            
        Returns:
            生成的摘要文本
        """
        if max_length:
            prompt = f"""
            请为以下文本生成一个简洁准确的摘要，摘要长度不超过{max_length}个字符：
            
            文本：{input}
            
            请确保摘要保留原文的核心信息和上下文语境，使用自然表述、流畅可读的文本。
            """
        else:
            prompt = f"""
            请为以下文本生成一个简洁准确的摘要：
            
            文本：{input}
            
            请确保摘要保留原文的核心信息和上下文语境，使用自然表述、流畅可读的文本。
            """
        
        # 构建聊天请求
        request = ChatCompletionRequest(
            model=model,
            messages=[Message(role=Role.USER, content=prompt)],
            temperature=0.5,  # 适中的温度以保持准确性同时增加一些变化
            max_tokens=500 if not max_length else min(500, max_length * 2)  # 根据需要调整
        )
        
        # 发送请求并获取响应
        response = await self.chat_completion(request)
        return response.choices[0].message.content.strip()
    
    async def understandit(self, input: Union[str, bytes, Dict], media_type: Optional[str] = None, model: str = "gpt-4-vision") -> str:
        """识别和理解给定的媒体内容（文本、图像、音频等），根据内容类型返回相应的理解结果
        
        Args:
            input: 输入的媒体内容，支持文本、二进制数据、包含URL的字典
            media_type: 媒体类型，如果提供将用于处理决策
            model: 使用的AI模型，默认为gpt-4-vision（支持多模态）
            
        Returns:
            对媒体内容的理解结果
        """
        # 根据输入类型进行处理
        if isinstance(input, str):
            # 文本输入
            if media_type and media_type.startswith('image'):
                # 如果指定了图像类型，尝试解析为URL或base64
                return await self._process_image_content(input, media_type, model)
            else:
                # 纯文本处理
                prompt = f"请分析并理解以下文本内容：\n\n{input}\n\n请提供详细的理解和分析结果。"
                request = ChatCompletionRequest(
                    model=model,
                    messages=[Message(role=Role.USER, content=prompt)],
                    temperature=0.5,
                    max_tokens=1000
                )
                response = await self.chat_completion(request)
                return response.choices[0].message.content.strip()
        
        elif isinstance(input, bytes):
            # 二进制数据（如图像）
            base64_data = base64.b64encode(input).decode('utf-8')
            # 假设是图像，使用GPT-4 Vision进行处理
            prompt = "请分析并理解以下图像内容。请提供详细的描述和分析结果。"
            # 创建多模态消息，直接使用字典格式
            content_items = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
            ]
            
            request = ChatCompletionRequest(
                model=model,
                messages=[{"role": "user", "content": content_items}],
                temperature=0.5,
                max_tokens=1000
            )
            response = await self.chat_completion(request)
            return response.choices[0].message.content.strip()
        
        elif isinstance(input, dict):
            # 字典输入，可能包含URL或其他结构化数据
            if 'url' in input:
                url = input['url']
                parsed = urlparse(url)
                if parsed.scheme in ['http', 'https']:
                    # URL处理
                    if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        # 图像URL
                        prompt = "请分析并理解以下图像内容。请提供详细的描述和分析结果。"
                        content_items = [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": url}}
                        ]
                                            
                        request = ChatCompletionRequest(
                            model=model,
                            messages=[{"role": "user", "content": content_items}],
                            temperature=0.5,
                            max_tokens=1000
                        )
                        response = await self.chat_completion(request)
                        return response.choices[0].message.content.strip()
                    else:
                        # 其他URL，可能需要下载内容
                        import httpx
                        async with httpx.AsyncClient() as client:
                            resp = await client.get(url)
                            content = resp.text
                            prompt = f"请分析并理解以下URL内容：\n\n{content}\n\n请提供详细的理解和分析结果。"
                            
                            request = ChatCompletionRequest(
                                model=model,
                                messages=[Message(role=Role.USER, content=prompt)],
                                temperature=0.5,
                                max_tokens=1000
                            )
                            response = await self.chat_completion(request)
                            return response.choices[0].message.content.strip()
            elif 'text' in input:
                # 纯文本
                prompt = f"请分析并理解以下文本内容：\n\n{input['text']}\n\n请提供详细的理解和分析结果。"
                request = ChatCompletionRequest(
                    model=model,
                    messages=[Message(role=Role.USER, content=prompt)],
                    temperature=0.5,
                    max_tokens=1000
                )
                response = await self.chat_completion(request)
                return response.choices[0].message.content.strip()
            elif 'image' in input:
                # 图像数据
                image_data = input['image']
                if isinstance(image_data, str):
                    # 假设是base64编码的图像
                    prompt = "请分析并理解以下图像内容。请提供详细的描述和分析结果。"
                    content_items = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                    
                    request = ChatCompletionRequest(
                        model=model,
                        messages=[{"role": "user", "content": content_items}],
                        temperature=0.5,
                        max_tokens=1000
                    )
                    response = await self.chat_completion(request)
                    return response.choices[0].message.content.strip()
        
        # 默认情况，返回错误信息
        raise ValueError("不支持的输入类型或格式")
    
    async def _process_image_content(self, content: str, media_type: str, model: str) -> str:
        """处理图像内容的辅助方法"""
        prompt = "请分析并理解以下图像内容。请提供详细的描述和分析结果。"
        content_items = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": content}}
        ]
        
        request = ChatCompletionRequest(
            model=model,
            messages=[{"role": "user", "content": content_items}],
            temperature=0.5,
            max_tokens=1000
        )
        response = await self.chat_completion(request)
        return response.choices[0].message.content.strip()
    
    async def mark_key_content(self, input: str) -> str:
        """理解输入内容并通过在原文上标记关键或核心语义的内容（如句子、段落）上添加特定标识标签<key_content></key_content>
        
        Args:
            input: 输入的文本内容
            
        Returns:
            标记关键内容后的文本
        """
        prompt = f"""
        请分析以下文本内容，识别出其中的核心语义内容（如关键句子、重要段落、核心概念等），
        并在原文基础上使用XML标签<key_content></key_content>标记这些关键内容。
        请保持原文结构完整性，只添加标记标签。

        原文：{input}

        请返回标记后的文本。
        """
        
        request = ChatCompletionRequest(
            model="gpt-4",
            messages=[Message(role=Role.USER, content=prompt)],
            temperature=0.3,
            max_tokens=2000
        )
        
        response = await self.chat_completion(request)
        return response.choices[0].message.content.strip()
    
    async def translate(self, input: str, target_language: str, source_language: Optional[str] = None, model: str = "gpt-4") -> str:
        """理解输入内容并根据目标语言进行翻译，自动选择最佳翻译策略
        
        Args:
            input: 需要翻译的文本内容
            target_language: 目标语言
            source_language: 源语言（可选），如果不提供将自动检测
            model: 使用的AI模型，默认为gpt-4
            
        Returns:
            翻译后的文本
        """
        if source_language:
            prompt = f"请将以下{source_language}文本翻译为{target_language}：\n\n{input}\n\n请保持原文的语义准确性和上下文语境。"
        else:
            prompt = f"请检测以下文本的语言，并将其翻译为{target_language}：\n\n{input}\n\n请保持原文的语义准确性和上下文语境。"
        
        request = ChatCompletionRequest(
            model=model,
            messages=[Message(role=Role.USER, content=prompt)],
            temperature=0.3,  # 较低温度以保持翻译准确性
            max_tokens=2000
        )
        
        response = await self.chat_completion(request)
        return response.choices[0].message.content.strip()
    
    async def emotion_recog(self, input: str, model: str = "gpt-4") -> Dict[str, Any]:
        """分析输入内容的情感类型，识别情感偏向，并提供分析结论的依据
        
        Args:
            input: 需要分析情感的文本内容
            model: 使用的AI模型，默认为gpt-4
            
        Returns:
            包含情感类型、情感强度、分析依据等信息的字典
        """
        prompt = f"""
        请分析以下文本内容的情感特征：
        
        文本：{input}
        
        请按照以下JSON格式返回分析结果：
        {{
          "emotion_type": "情感类型（如：positive, negative, neutral等）",
          "emotion_intensity": "情感强度（0-1之间的数值，1表示最强）",
          "emotion_details": {{
            "primary_emotion": "主要情感",
            "secondary_emotions": ["次要情感列表"],
            "confidence": "置信度（0-1之间的数值）"
          }},
          "analysis_basis": "分析依据，指出文本中体现情感的关键词句",
          "summary": "情感分析的简要总结"
        }}
        """
        
        request = ChatCompletionRequest(
            model=model,
            messages=[Message(role=Role.USER, content=prompt)],
            temperature=0.2,  # 较低温度以获得更一致的情感分析结果
            max_tokens=1000,
            response_format={"type": "json_object"}  # 强制返回JSON格式
        )
        
        response = await self.chat_completion(request)
        result_str = response.choices[0].message.content.strip()
        
        # 解析JSON结果
        try:
            result = json.loads(result_str)
            return result
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回一个基本的字典结构
            return {
                "emotion_type": "unknown",
                "emotion_intensity": 0.0,
                "emotion_details": {
                    "primary_emotion": "unknown",
                    "secondary_emotions": [],
                    "confidence": 0.0
                },
                "analysis_basis": "无法解析AI返回的分析结果",
                "summary": "情感分析失败"
            }