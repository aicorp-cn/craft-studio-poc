"""
内容提取工具模块

负责从 LLM 响应中提取特定标签包裹的内容
"""

import re
from typing import Tuple, Optional


class ContentExtractor:
    """
    内容提取工具类
    
    专门负责从 LLM 响应中提取特定标签内容
    支持 <meta-prompt> 和 <final-output> 标签
    """
    
    # 支持的标签类型
    META_PROMPT_TAG = 'meta-prompt'
    FINAL_OUTPUT_TAG = 'final-output'
    
    @staticmethod
    def extract_meta_prompt_content(text: str) -> str:
        """
        提取元指令内容（向后兼容接口）
        
        Args:
            text: LLM 响应文本
            
        Returns:
            提取的内容，如果提取失败则返回原始文本
        """
        return ContentExtractor._extract_from_llm_output(text, ContentExtractor.META_PROMPT_TAG)
    
    @staticmethod
    def extract_final_output(text: str) -> str:
        """
        提取最终输出内容（向后兼容接口）
        
        Args:
            text: LLM 响应文本
            
        Returns:
            提取的内容，如果提取失败则返回原始文本
        """
        return ContentExtractor._extract_from_llm_output(text, ContentExtractor.FINAL_OUTPUT_TAG)
    
    @staticmethod
    def extract_meta_prompt_content_v2(text: str) -> Tuple[str, bool]:
        """
        提取元指令内容（新版 API）
        
        Args:
            text: LLM 响应文本
            
        Returns:
            (提取的内容, 是否成功提取) 元组
        """
        return ContentExtractor._extract_from_llm_output_v2(text, ContentExtractor.META_PROMPT_TAG)
    
    @staticmethod
    def extract_final_output_v2(text: str) -> Tuple[str, bool]:
        """
        提取最终输出内容（新版 API）
        
        Args:
            text: LLM 响应文本
            
        Returns:
            (提取的内容, 是否成功提取) 元组
        """
        return ContentExtractor._extract_from_llm_output_v2(text, ContentExtractor.FINAL_OUTPUT_TAG)
    
    @staticmethod
    def _extract_from_llm_output(text: str, pattern: str) -> str:
        """
        提取指定标签内容（向后兼容版本）
        
        Args:
            text: LLM 响应文本
            pattern: 标签名称
            
        Returns:
            提取的内容，如果提取失败则返回原始文本
        """
        content, _ = ContentExtractor._extract_from_llm_output_v2(text, pattern)
        return content
    
    @staticmethod
    def _extract_from_llm_output_v2(text: str, pattern: str) -> Tuple[str, bool]:
        """
        提取指定标签内容（新版本，返回提取状态）
        
        Args:
            text: LLM 响应文本
            pattern: 标签名称
            
        Returns:
            (提取的内容, 是否成功提取) 元组
        """
        if not text:
            return "", False
        
        try:
            # 尝试精确匹配标签
            regex_pattern = rf'<{pattern}>(.*?)</{pattern}>'
            matches = re.findall(regex_pattern, text, re.DOTALL)
            
            if matches:
                # 合并所有匹配内容（通常只有一个）
                content = '\n'.join(match.strip() for match in matches)
                return content, True
            
            # 尝试宽松匹配（处理 LLM 可能添加的空格或换行）
            regex_pattern_loose = rf'<\s*{pattern}\s*>(.*?)<\s*/\s*{pattern}\s*>'
            matches = re.findall(regex_pattern_loose, text, re.DOTALL)
            
            if matches:
                content = '\n'.join(match.strip() for match in matches)
                return content, True
            
            # 尝试匹配 Markdown 代码块包裹的标签
            # 例如: ```<meta-prompt>...</meta-prompt>```
            regex_pattern_code = rf'```[^\n]*\n?<{pattern}>(.*?)</{pattern}>\n?```'
            matches = re.findall(regex_pattern_code, text, re.DOTALL)
            
            if matches:
                content = '\n'.join(match.strip() for match in matches)
                return content, True
            
            # 提取失败，返回原始内容
            return text, False
            
        except re.error as e:
            # 正则表达式错误处理
            return text, False
        except Exception as e:
            # 其他错误
            return text, False
    
    @staticmethod
    def extract_with_fallback(
        text: str, 
        primary_tag: str, 
        fallback_tags: Optional[list] = None
    ) -> Tuple[str, str, bool]:
        """
        带降级策略的内容提取
        
        如果主标签提取失败，尝试使用备选标签
        
        Args:
            text: LLM 响应文本
            primary_tag: 主标签名称
            fallback_tags: 备选标签列表
            
        Returns:
            (提取的内容, 使用的标签, 是否成功提取) 元组
        """
        # 首先尝试主标签
        content, success = ContentExtractor._extract_from_llm_output_v2(text, primary_tag)
        if success:
            return content, primary_tag, True
        
        # 尝试备选标签
        if fallback_tags:
            for tag in fallback_tags:
                content, success = ContentExtractor._extract_from_llm_output_v2(text, tag)
                if success:
                    return content, tag, True
        
        # 所有标签都失败，返回原始内容
        return text, "", False
    
    @staticmethod
    def validate_tag_structure(text: str, tag: str) -> Tuple[bool, Optional[str]]:
        """
        验证标签结构是否完整
        
        Args:
            text: 待验证的文本
            tag: 标签名称
            
        Returns:
            (是否有效, 错误信息) 元组
        """
        open_tag = f'<{tag}>'
        close_tag = f'</{tag}>'
        
        open_count = text.count(open_tag)
        close_count = text.count(close_tag)
        
        if open_count == 0 and close_count == 0:
            return False, f"未找到 {tag} 标签"
        
        if open_count != close_count:
            return False, f"{tag} 标签不匹配：开标签 {open_count} 个，闭标签 {close_count} 个"
        
        # 检查标签顺序
        open_pos = text.find(open_tag)
        close_pos = text.find(close_tag)
        
        if close_pos < open_pos:
            return False, f"{tag} 闭标签出现在开标签之前"
        
        return True, None
    
    @staticmethod
    def clean_extracted_content(content: str) -> str:
        """
        清理提取的内容
        
        移除首尾空白、多余的换行符等
        
        Args:
            content: 提取的原始内容
            
        Returns:
            清理后的内容
        """
        if not content:
            return ""
        
        # 移除首尾空白
        content = content.strip()
        
        # 将连续的多个空行替换为单个空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    @staticmethod
    def extract_all_tags(text: str) -> dict:
        """
        提取文本中所有已知类型的标签内容
        
        Args:
            text: LLM 响应文本
            
        Returns:
            字典，键为标签名，值为提取的内容
        """
        result = {}
        
        for tag in [ContentExtractor.META_PROMPT_TAG, ContentExtractor.FINAL_OUTPUT_TAG]:
            content, success = ContentExtractor._extract_from_llm_output_v2(text, tag)
            if success:
                result[tag] = ContentExtractor.clean_extracted_content(content)
        
        return result
