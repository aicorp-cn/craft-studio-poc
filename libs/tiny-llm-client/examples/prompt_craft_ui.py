import asyncio
import re
from pathlib import Path
from tiny_lm_client import TinyLMClient, ChatCompletionRequest, Message

file_path = Path("prompts/Meta-Prompt-Generator.md")
# 检查文件是否存在
if not file_path.exists():
    print(f"文件不存在: {file_path}")
print(f"文件内容: {file_path.resolve()}")

sys_prompt= file_path.read_text(encoding='utf-8')
llm_model="deepseek-chat"    

async def craft_meta_prompt(input:str)->str:
    """理解接收到的用户输入内容，生成元指令框架"""
    print("\n" + "=" * 50)
    print("元指令框架生成")
    print("=" * 50)
    
    async with TinyLMClient(
        base_url="https://api.deepseek.com",
        api_key="sk-c2cc9388b3674d86bfd0eb4cd9452121",
        max_retries=3,
        timeout=120
    ) as client:
        # 
        request = ChatCompletionRequest(
            model=llm_model,
            messages=[
                Message(role="system",content=sys_prompt),
                Message(role="user", content=input)
            ],
            temperature=0.1
        )
        response = await client.chat_completion(request)
        meta_prompt_content = extract_meta_prompt_content(response.choices[0].message.content)
        if response.usage:
            print("\n" + "=" * 50)
            print("元指令框架:")
            print(f"  {meta_prompt_content}")
            print()
            print("Token 使用:")
            print(f"  输入: {response.usage.prompt_tokens}")
            print(f"  输出: {response.usage.completion_tokens}")
            print(f"  总计: {response.usage.total_tokens}")
            print("=" * 50)
            print()
        return meta_prompt_content
        
async def gen_final_output(input:str, meta_prompt_content:str)->str:
    """理解接收到的用户输入内容，根据元指令生成最终输出结果"""
    print("\n" + "=" * 50)
    print("元指令框架生成")
    print("=" * 50)
    
    async with TinyLMClient(
        base_url="https://api.deepseek.com",
        api_key="sk-c2cc9388b3674d86bfd0eb4cd9452121",
        max_retries=3,
        timeout=120
    ) as client:
            
        request = ChatCompletionRequest(
            model=llm_model,
            messages=[
                Message(role="system",content=meta_prompt_content),
                Message(role="user", content=input)
            ],
            temperature=0.1
        )
        response = await client.chat_completion(request)
        result_content = extract_final_output(response.choices[0].message.content)
        if response.usage:
            print("\n" + "=" * 50)
            print("最终结果")
            print(f"{result_content}")
            print()
            print("Token 使用:")
            print(f"  输入: {response.usage.prompt_tokens}")
            print(f"  输出: {response.usage.completion_tokens}")
            print(f"  总计: {response.usage.total_tokens}")
            print("=" * 50)
            print()
        return result_content
    
def extract_meta_prompt_content(text: str) -> str:
    """
    提取文本中被 <meta-prompt></meta-prompt> 标签包裹的全部内容，并以原始格式返回
    
    Args:
        text: 包含 <meta-prompt> 标签的输入文本
        
    Returns:
        str: 提取的内容，多个匹配项用换行符分隔
    """
    return  extract_from_llm_output(text, 'meta-prompt')

def extract_final_output(text: str) -> str:
    """
    提取文本中被 <final-output></final-output> 标签包裹的全部内容，并以原始格式返回
    
    Args:
        text: 包含 <final-output> 标签的输入文本
        
    Returns:
        str: 提取的内容，多个匹配项用换行符分隔
    """
    return extract_from_llm_output(text, 'final-output')

def extract_from_llm_output(text: str,pattern:str) -> str:
    """
    提取文本中被 <pattern></pattern> 标签包裹的全部内容，并以原始格式返回
    
    Args:
        text: 包含 <pattern> 标签的输入文本
        
    Returns:
        str: 提取的内容，多个匹配项用换行符分隔
    """
    pattern = r'<'+pattern+'>(.*?)</'+pattern+'>'
    matches = re.findall(pattern, text, re.DOTALL)
    return '\n'.join(matches) if matches else ''

if __name__ == "__main__":
    try:
        # asyncio.run(craft_prompt_framework("编写一篇移动端大语言模型应用发展趋势和展望的报告"))
        # asyncio.run(craft_meta_prompt("编写一篇移动端大语言模型应用发展趋势和展望的报告"))
        # Step 1: 生成元指令
        meta_prompt_content = asyncio.run(craft_meta_prompt("编写一篇移动端大语言模型应用发展趋势和展望的报告"))
        # Step 2: 生成最终结果
        final_output = asyncio.run(gen_final_output("编写一篇移动端大语言模型应用发展趋势和展望的报告", meta_prompt_content))

    except KeyboardInterrupt:
        print("\n\n已中断测试")
        import sys
        sys.exit(0)