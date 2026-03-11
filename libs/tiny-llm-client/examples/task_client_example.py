"""
TinyTaskClient 使用示例

展示如何使用 TinyTaskClient 的各种业务功能
"""

import asyncio
from tiny_lm_client import TinyTaskClient, FormatType


async def main():
    # 初始化 TinyTaskClient
    async with TinyTaskClient(
        base_url="https://api.openai.com/v1",
        api_key="your-api-key",  # 替换为你的API密钥
        max_retries=3,
        timeout=60.0
    ) as client:
        
        print("=== TinyTaskClient 功能演示 ===\n")
        
        # 1. 分类功能
        print("1. 分类功能:")
        classify_input = "This product is amazing and works perfectly!"
        classify_result = await client.classify(
            input=classify_input,
            choices=["positive", "negative", "neutral"],
            model="gpt-4"
        )
        print(f"输入: {classify_input}")
        print(f"分类结果: {classify_result}")
        print("\n" + "="*50 + "\n")
        
        # 2. 摘要功能
        print("2. 摘要功能:")
        summary_input = "Artificial intelligence is transforming the world in unprecedented ways. It encompasses various technologies including machine learning, deep learning, natural language processing, and computer vision. These technologies are being applied across multiple industries such as healthcare, finance, transportation, and entertainment to solve complex problems and automate tasks."
        summary_result = await client.summary(
            input=summary_input,
            max_length=50,
            model="gpt-4"
        )
        print(f"原文: {summary_input}")
        print(f"摘要: {summary_result}")
        print("\n" + "="*50 + "\n")
        
        # 3. 思维导图功能
        print("3. 思维导图功能 (Mermaid格式):")
        mindmap_input = "人工智能是计算机科学的一个分支，它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。"
        mindmap_result = await client.mindmap(
            input=mindmap_input,
            format_type=FormatType.MARKDOWN,
            model="gpt-4"
        )
        print(mindmap_result)
        print("\n" + "="*50 + "\n")
        
        # 2. 内容理解功能
        print("2. 内容理解功能:")
        understand_input = "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。它广泛应用于Web开发、数据科学、人工智能等领域。"
        understand_result = await client.understandit(
            input=understand_input,
            model="gpt-4"
        )
        print(understand_result)
        print("\n" + "="*50 + "\n")
        
        # 3. 标记关键内容
        print("3. 标记关键内容:")
        mark_input = "在机器学习中，监督学习是一种训练方法，其中模型从标记的训练数据中学习。无监督学习则处理未标记的数据，试图从数据中发现隐藏的结构。强化学习涉及智能体与环境的交互，通过奖励和惩罚机制进行学习。"
        marked_result = await client.mark_key_content(input=mark_input)
        print(marked_result)
        print("\n" + "="*50 + "\n")
        
        # 4. 翻译功能
        print("4. 翻译功能:")
        translate_input = "Artificial intelligence is transforming the world in unprecedented ways."
        translated_result = await client.translate(
            input=translate_input,
            target_language="中文",
            model="gpt-4"
        )
        print(f"原文: {translate_input}")
        print(f"翻译: {translated_result}")
        print("\n" + "="*50 + "\n")
        
        # 5. 情感识别功能
        print("5. 情感识别功能:")
        emotion_input = "I absolutely love this new product! It has exceeded all my expectations and made my life so much easier."
        emotion_result = await client.emotion_recog(input=emotion_input, model="gpt-4")
        print(f"输入: {emotion_input}")
        print(f"情感分析结果: {emotion_result}")


if __name__ == "__main__":
    asyncio.run(main())