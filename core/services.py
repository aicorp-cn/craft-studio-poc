"""
业务服务模块 

提供 LLM API 调用和文件操作服务
"""

from pathlib import Path
from typing import Tuple, Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass

from tiny_lm_client import TinyLMClient, ChatCompletionRequest, Message
from conf.config import AppConfig
from utils.extractor import ContentExtractor
from .models import UsageInfo


@dataclass
class CraftResult:
    """创作指导生成结果"""
    content: str
    usage: UsageInfo
    raw_response: Optional[str] = None  # 原始响应（调试用）
    extraction_success: bool = True     # 是否成功提取标签内容


@dataclass
class GenerateResult:
    """最终内容生成结果"""
    content: str
    usage: UsageInfo
    raw_response: Optional[str] = None
    extraction_success: bool = True


class FileService:
    """
    文件服务类
    
    负责文件系统操作，包括系统提示文件的加载和验证
    """
    
    @staticmethod
    async def load_sys_prompt(file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        加载系统提示文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            (内容, 错误信息) 元组，成功时错误信息为 None
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None, f"系统提示文件不存在: {file_path}"
            
            # 安全检查：确保文件在允许的目录内
            try:
                path.resolve().relative_to(Path.cwd())
            except ValueError:
                # 允许绝对路径，但需要确保文件存在
                pass
            
            content = path.read_text(encoding='utf-8')
            if not content.strip():
                return None, f"系统提示文件为空: {file_path}"
            
            return content, None
            
        except UnicodeDecodeError:
            return None, f"文件编码错误，请确保文件使用 UTF-8 编码: {file_path}"
        except PermissionError:
            return None, f"无权限访问文件: {file_path}"
        except Exception as e:
            return None, f"加载系统提示文件失败: {str(e)}"
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: list = None) -> Tuple[bool, str]:
        """
        验证文件路径的安全性
        
        Args:
            file_path: 文件路径
            allowed_extensions: 允许的文件扩展名列表
            
        Returns:
            (是否有效, 错误信息或规范化路径) 元组
        """
        if allowed_extensions is None:
            allowed_extensions = ['.md', '.txt']
        
        try:
            path = Path(file_path)
            
            # 检查扩展名
            if path.suffix.lower() not in allowed_extensions:
                return False, f"不支持的文件类型: {path.suffix}"
            
            # 规范化路径
            resolved_path = path.resolve()
            
            return True, str(resolved_path)
            
        except Exception as e:
            return False, f"路径验证失败: {str(e)}"


class LLMService:
    """
    LLM 服务类
    
    封装与 LLM API 的所有交互，提供创作指导生成和最终内容生成功能
    
    设计原则：
    1. 异步优先：所有 API 调用都是异步的
    2. 结果封装：返回结构化的结果对象
    3. 缓存策略：系统提示文件使用缓存
    4. 错误处理：所有错误都被捕获并转换为用户友好的消息
    """
    
    def __init__(self, config: AppConfig):
        """
        初始化 LLM 服务
        
        Args:
            config: 应用配置
        """
        self.config = config
        self._sys_prompt_cache: Dict[str, str] = {}
    
    def _create_client(self) -> TinyLMClient:
        """创建 TinyLMClient 实例"""
        return TinyLMClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            max_retries=self.config.max_retries,
            timeout=self.config.timeout
        )
    
    async def _load_sys_prompt_cached(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        加载系统提示（带缓存）
        
        Args:
            file_path: 系统提示文件路径
            
        Returns:
            (是否成功, 错误信息) 元组
        """
        if file_path in self._sys_prompt_cache:
            return True, None
        
        content, error = await FileService.load_sys_prompt(file_path)
        if error:
            return False, error
        
        self._sys_prompt_cache[file_path] = content
        return True, None
    
    def get_cached_sys_prompt(self, file_path: str) -> Optional[str]:
        """获取缓存的系统提示"""
        return self._sys_prompt_cache.get(file_path)
    
    def clear_cache(self) -> None:
        """清除系统提示缓存"""
        self._sys_prompt_cache.clear()
    
    async def craft_meta_prompt(
        self,
        user_input: str,
        model: str,
        temperature: float,
        sys_prompt_path: str,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        生成创作指导框架（元指令）
        
        这是两阶段处理流程的第一阶段，将用户的模糊需求转化为结构化的创作指导框架
        
        Args:
            user_input: 用户输入的需求描述
            model: 使用的模型名称
            temperature: 温度参数
            sys_prompt_path: 系统提示文件路径
            max_tokens: 最大生成 token 数
            top_p: top_p 参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            
        Returns:
            (创作指导内容, 使用信息字典, 错误信息) 元组
        """
        result = await self.craft_meta_prompt_v2(
            user_input=user_input,
            model=model,
            temperature=temperature,
            sys_prompt_path=sys_prompt_path,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        if isinstance(result, str):
            # 返回错误信息
            return None, None, result
        
        return result.content, result.usage.to_dict(), None
    
    async def craft_meta_prompt_v2(
        self,
        user_input: str,
        model: str,
        temperature: float,
        sys_prompt_path: str,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None
    ) -> CraftResult | str:
        """
        生成创作指导框架（新版 API）
        
        Args:
            user_input: 用户输入的需求描述
            model: 使用的模型名称
            temperature: 温度参数
            sys_prompt_path: 系统提示文件路径
            max_tokens: 最大生成 token 数
            top_p: top_p 参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            
        Returns:
            CraftResult 对象或错误信息字符串
        """
        # 输入验证
        if not user_input or not user_input.strip():
            return "用户输入不能为空"
        
        # 加载系统提示
        success, error = await self._load_sys_prompt_cached(sys_prompt_path)
        if not success:
            return error
        
        sys_prompt = self._sys_prompt_cache[sys_prompt_path]
        
        try:
            async with self._create_client() as client:
                request = ChatCompletionRequest(
                    model=model,
                    messages=[
                        Message(role="system", content=sys_prompt),
                        Message(role="user", content=user_input)
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens or self.config.craft_max_tokens,
                    top_p=top_p or self.config.craft_top_p,
                    frequency_penalty=frequency_penalty or self.config.craft_frequency_penalty,
                    presence_penalty=presence_penalty or self.config.craft_presence_penalty
                )
                
                response = await client.chat_completion(request)
                
                raw_content = response.choices[0].message.content
                extracted_content, extraction_success = ContentExtractor.extract_meta_prompt_content_v2(raw_content)
                
                usage = UsageInfo.from_dict(
                    response.usage.__dict__ if response.usage else {}
                )
                
                return CraftResult(
                    content=extracted_content,
                    usage=usage,
                    raw_response=raw_content,
                    extraction_success=extraction_success
                )
                
        except Exception as e:
            error_msg = str(e)
            # 提供更友好的错误信息
            if "timeout" in error_msg.lower():
                return "请求超时，请检查网络连接或增加超时时间"
            elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "API 密钥无效，请检查您的 API Key 配置"
            elif "rate_limit" in error_msg.lower():
                return "API 请求频率超限，请稍后重试"
            else:
                return f"生成创作指导时出错: {error_msg}"
    
    async def gen_final_output(
        self,
        user_input: str,
        meta_prompt_content: str,
        model: str,
        temperature: float,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        生成最终输出内容
        
        这是两阶段处理流程的第二阶段，基于创作指导框架生成最终内容
        
        Args:
            user_input: 用户输入的需求描述
            meta_prompt_content: 第一阶段生成的创作指导框架
            model: 使用的模型名称
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            top_p: top_p 参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            
        Returns:
            (最终输出内容, 使用信息字典, 错误信息) 元组
        """
        result = await self.gen_final_output_v2(
            user_input=user_input,
            meta_prompt_content=meta_prompt_content,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        if isinstance(result, str):
            return None, None, result
        
        return result.content, result.usage.to_dict(), None
    
    async def gen_final_output_v2(
        self,
        user_input: str,
        meta_prompt_content: str,
        model: str,
        temperature: float,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None
    ) -> GenerateResult | str:
        """
        生成最终输出内容（新版 API）
        
        Args:
            user_input: 用户输入的需求描述
            meta_prompt_content: 第一阶段生成的创作指导框架
            model: 使用的模型名称
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            top_p: top_p 参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            
        Returns:
            GenerateResult 对象或错误信息字符串
        """
        # 输入验证
        if not user_input or not user_input.strip():
            return "用户输入不能为空"
        
        if not meta_prompt_content or not meta_prompt_content.strip():
            return "创作指导框架不能为空，请先完成第一阶段"
        
        try:
            async with self._create_client() as client:
                request = ChatCompletionRequest(
                    model=model,
                    messages=[
                        Message(role="system", content=meta_prompt_content),
                        Message(role="user", content=user_input)
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens or self.config.generate_model_max_tokens,
                    top_p=top_p or self.config.generate_model_top_p,
                    frequency_penalty=frequency_penalty or self.config.generate_model_frequency_penalty,
                    presence_penalty=presence_penalty or self.config.generate_model_presence_penalty
                )
                
                response = await client.chat_completion(request)
                
                raw_content = response.choices[0].message.content
                extracted_content, extraction_success = ContentExtractor.extract_final_output_v2(raw_content)
                
                usage = UsageInfo.from_dict(
                    response.usage.__dict__ if response.usage else {}
                )
                
                return GenerateResult(
                    content=extracted_content,
                    usage=usage,
                    raw_response=raw_content,
                    extraction_success=extraction_success
                )
                
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return "请求超时，请检查网络连接或增加超时时间"
            elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "API 密钥无效，请检查您的 API Key 配置"
            elif "rate_limit" in error_msg.lower():
                return "API 请求频率超限，请稍后重试"
            else:
                return f"生成最终输出时出错: {error_msg}"
    
    async def validate_api_connection(self) -> Tuple[bool, Optional[str]]:
        """
        验证 API 连接是否正常
        
        Returns:
            (是否成功, 错误信息) 元组
        """
        try:
            async with TinyLMClient(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                max_retries=1,
                timeout=min(self.config.timeout, 30)  # 验证连接使用较短的超时
            ) as client:
                # 发送一个简单的请求来验证连接
                request = ChatCompletionRequest(
                    model=self.config.craft_model,
                    messages=[
                        Message(role="user", content="Hi")
                    ],
                    max_tokens=5
                )
                await client.chat_completion(request)
                return True, None
                
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return False, "API 密钥无效"
            elif "timeout" in error_msg.lower():
                return False, "连接超时，请检查 Base URL 是否正确"
            else:
                return False, f"连接验证失败: {error_msg}"
    
    async def execute_full_pipeline(
        self,
        user_input: str,
        on_progress: Optional[callable] = None
    ) -> Tuple[Optional[CraftResult], Optional[GenerateResult], Optional[str]]:
        """
        执行完整的两阶段处理流程
        
        Args:
            user_input: 用户输入
            on_progress: 进度回调函数，接收 (阶段名称, 进度百分比) 参数
            
        Returns:
            (创作结果, 生成结果, 错误信息) 元组
        """
        # 阶段1：生成创作指导
        if on_progress:
            on_progress("crafting", 25)
        
        craft_result = await self.craft_meta_prompt_v2(
            user_input=user_input,
            model=self.config.craft_model,
            temperature=self.config.craft_temperature,
            sys_prompt_path=self.config.sys_prompt_path
        )
        
        if isinstance(craft_result, str):
            return None, None, craft_result
        
        # 阶段2：生成最终内容
        if on_progress:
            on_progress("generating", 75)
        
        generate_result = await self.gen_final_output_v2(
            user_input=user_input,
            meta_prompt_content=craft_result.content,
            model=self.config.generate_model,
            temperature=self.config.generate_model_temperature
        )
        
        if isinstance(generate_result, str):
            return craft_result, None, generate_result
        
        if on_progress:
            on_progress("completed", 100)
        
        return craft_result, generate_result, None
