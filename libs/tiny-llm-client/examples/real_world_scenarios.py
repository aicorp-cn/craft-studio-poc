"""
TinyLMClient 实际应用场景示例

展示如何在实际项目中使用 TinyLMClient，包括：
- 代码助手
- 文本摘要
- 问答系统
- 翻译助手
前提：已安装 Ollama 并下载 deepseek-r1:1.5b 模型
"""

import asyncio
import json
from typing import List, Dict, Any
from tiny_lm_client import (
    TinyLMClient,
    ChatCompletionRequest,
    Message
)

from pathlib import Path
# 知识库文档
pj_knowledge_docs = Path("README.md").read_text(encoding="utf-8")

llm_model="deepseek-r1:1.5b"

async def code_assistant_example():
    """代码助手示例"""
    print("=" * 50)
    print("示例 1: 代码助手")
    print("=" * 50)

    code_questions = [
        "用 Python 写一个计算斐波那契数列的函数",
        "解释这段代码的作用：\n```\ndef quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)\n```"
    ]

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ) as client:

        for i, question in enumerate(code_questions, 1):
            print(f"\n问题 {i}: {question}\n")

            request = ChatCompletionRequest(
                model=llm_model,
                messages=[
                    Message(role="system", content="你是一个专业的编程助手，擅长代码编写和解释。"),
                    Message(role="user", content=question)
                ],
                temperature=0.3,
                max_tokens=300
            )

            response = await client.chat_completion(request)
            print(f"回答:\n{response.choices[0].message.content}\n")
            print("-" * 40)


async def text_summarization_example():
    """文本摘要示例"""
    print("\n" + "=" * 50)
    print("示例 2: 文本摘要")
    print("=" * 50)

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        timeout=120,
        max_retries=3
    ) as client:

        request = ChatCompletionRequest(
            model=llm_model,
            messages=[
                Message(
                    role="user",
                    content=f"请用100字左右总结以下文本的主要内容：\n\n{pj_knowledge_docs}"
                )
            ],
            temperature=0.4,
            max_tokens=150
        )

        response = await client.chat_completion(request)

        print(f"\n原文长度: {len(pj_knowledge_docs)} 字符")
        print(f"\n摘要:\n{response.choices[0].message.content}")


async def qa_system_example():
    """问答系统示例"""
    print("\n" + "=" * 50)
    print("示例 3: 问答系统")
    print("=" * 50)

    questions = [
        "TinyLMClient 基于什么库构建？",
        "TinyLMClient 支持哪些核心功能？",
        "TinyLMClient 有什么依赖？"
    ]

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ) as client:

        for question in questions:
            print(f"\n问题: {question}")

            request = ChatCompletionRequest(
                model=llm_model,
                messages=[
                    Message(
                        role="system",
                        content=f"你是一个问答助手，请根据以下知识库回答用户的问题：\n\n{pj_knowledge_docs}"
                    ),
                    Message(role="user", content=question)
                ],
                temperature=0.2,
                max_tokens=4096
            )

            response = await client.chat_completion(request)
            print(f"回答: {response.choices[0].message.content}\n")


async def translation_assistant_example():
    """翻译助手示例"""
    print("=" * 50)
    print("示例 4: 翻译助手")
    print("=" * 50)

    translations = [
        {"from": "英语", "to": "中文", "text": "Artificial intelligence is transforming the world."},
        {"from": "中文", "to": "英语", "text": "深度学习是机器学习的一个重要分支。"},
        {"from": "中文", "to": "日语", "text": "你好，世界！"}
    ]

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ) as client:

        for i, trans in enumerate(translations, 1):
            print(f"\n翻译任务 {i}:")
            print(f"从 {trans['from']} 翻译到 {trans['to']}")
            print(f"原文: {trans['text']}")

            request = ChatCompletionRequest(
                model=llm_model,
                messages=[
                    Message(
                        role="user",
                        content=f"请将以下文本从{trans['from']}翻译成{trans['to']}：\n\n{trans['text']}"
                    )
                ],
                temperature=0.3,
                max_tokens=100
            )

            response = await client.chat_completion(request)
            print(f"译文: {response.choices[0].message.content}")
            print("-" * 40)


async def creative_writing_example():
    """创意写作示例"""
    print("\n" + "=" * 50)
    print("示例 5: 创意写作")
    print("=" * 50)

    prompts = [
        "写一个关于机器人与人类友谊的短故事开头（100字左右）",
        "创作一首关于科技与人文的短诗（4行）",
        "为一个科幻电影写一段简介（50字左右）"
    ]

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ) as client:

        for i, prompt in enumerate(prompts, 1):
            print(f"\n创意任务 {i}: {prompt}\n")

            request = ChatCompletionRequest(
                model=llm_model,
                messages=[
                    Message(
                        role="system",
                        content="你是一个富有创造力的写作助手。"
                    ),
                    Message(role="user", content=prompt)
                ],
                temperature=0.9,  # 较高温度增加创造性
                max_tokens=150
            )

            response = await client.chat_completion(request)
            print(f"创作结果:\n{response.choices[0].message.content}\n")
            print("-" * 40)


async def conversational_bot_example():
    """对话机器人示例"""
    print("\n" + "=" * 50)
    print("示例 6: 对话机器人")
    print("=" * 50)

    system_prompt = "你是一个友好的对话助手，能够就各种话题进行自然对话。"

    conversation_history = [
        Message(role="system", content=system_prompt),
        Message(role="user", content="你好！我想聊聊天。")
    ]

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ) as client:

        # 模拟多轮对话
        user_inputs = [
            "你平时喜欢做什么？",
            "能给我讲个有趣的冷知识吗？",
            "那你对人工智能有什么看法？"
        ]

        print("\n对话开始...\n")

        for user_input in user_inputs:
            # 添加用户消息
            conversation_history.append(Message(role="user", content=user_input))

            # 发送请求
            request = ChatCompletionRequest(
                model=llm_model,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=150
            )

            response = await client.chat_completion(request)
            assistant_reply = response.choices[0].message.content

            print(f"用户: {user_input}")
            print(f"助手: {assistant_reply}\n")

            # 添加助手回复到对话历史
            conversation_history.append(
                Message(role="assistant", content=assistant_reply)
            )


async def data_formatting_example():
    """数据格式化示例"""
    print("\n" + "=" * 50)
    print("示例 7: 数据格式化")
    print("=" * 50)

    raw_data = """
    张三，30岁，软件工程师，喜欢编程和阅读
    李四，25岁，产品经理，喜欢旅行和摄影
    王五，28岁，数据分析师，喜欢音乐和运动
    """

    async with TinyLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ) as client:

        request = ChatCompletionRequest(
            model=llm_model,
            messages=[
                Message(
                    role="user",
                    content=f"请将以下文本转换为 JSON 格式，包含 name、age、job、hobbies 字段：\n\n{raw_data}"
                )
            ],
            temperature=0.3,
            max_tokens=200
        )

        response = await client.chat_completion(request)
        result_text = response.choices[0].message.content

        print(f"\n原始数据:\n{raw_data}")
        print(f"\n格式化结果:\n{result_text}")

        # 尝试解析 JSON
        try:
            json_data = json.loads(result_text)
            print(f"\n解析成功的 JSON:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\n（输出不是有效的 JSON 格式）")


async def main():
    """运行所有实际应用场景示例"""
    print("\nTinyLMClient 实际应用场景示例\n")
    print("请确保 Ollama 已运行并下载了 deepseek-r1:1.5b 模型\n")

    try:
        await code_assistant_example()
        await text_summarization_example()
        await qa_system_example()
        await translation_assistant_example()
        await creative_writing_example()
        await conversational_bot_example()
        await data_formatting_example()

        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
