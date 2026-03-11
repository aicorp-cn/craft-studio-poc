"""
应用配置模块

支持多提供商管理和独立的模型设置
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict
try:
    from dotenv import load_dotenv
    _dotenv_available = True
except ImportError:
    _dotenv_available = False
    import warnings
    warnings.warn(
        "python-dotenv not installed. Install it with 'pip install python-dotenv' "
        "to enable automatic loading of .env files.", 
        UserWarning
    )

from .provider_registry import get_provider_registry, ProviderConfig


def str_to_bool(value: str) -> bool:
    """将字符串转换为布尔值"""
    return value.lower() in ("true", "1", "yes", "on")


@dataclass
class ProviderSettings:
    """
    提供商运行时设置
    
    每个提供商有独立的 API Key 和高级配置
    """
    provider_id: str
    api_key: str = ""
    # None 表示使用提供商默认值
    max_retries: Optional[int] = None
    timeout: Optional[int] = None
    # 自定义设置（用于自定义提供商）
    custom_base_url: str = ""
    
    def get_effective_max_retries(self, provider_config: ProviderConfig) -> int:
        """获取有效的 max_retries 值（优先使用自定义值）"""
        return self.max_retries if self.max_retries is not None else provider_config.defaults.max_retries
    
    def get_effective_timeout(self, provider_config: ProviderConfig) -> int:
        """获取有效的 timeout 值（优先使用自定义值）"""
        return self.timeout if self.timeout is not None else provider_config.defaults.timeout
    
    def get_effective_base_url(self, provider_config: ProviderConfig) -> str:
        """获取有效的 base_url"""
        if provider_config.allow_custom_base_url and self.custom_base_url:
            return self.custom_base_url
        return provider_config.base_url


@dataclass
class ModelSettings:
    """
    模型设置
    
    创作指导和最终输出使用独立的模型设置
    """
    provider_id: str = "deepseek"
    model_id: str = "deepseek-chat"
    temperature: float = 0.1
    max_tokens: int = 4096
    top_p: float = 0.7
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    # 自定义模型名称（用于自定义提供商）
    custom_model_id: str = ""
    
    def get_effective_model_id(self, provider_config: ProviderConfig) -> str:
        """获取有效的模型 ID"""
        if provider_config.allow_custom_model and self.custom_model_id:
            return self.custom_model_id
        return self.model_id


@dataclass
class AppConfig:
    """
    应用配置类 
    
    设计原则：
    1. 支持多提供商管理
    2. 创作指导和最终输出使用独立的模型设置
    3. 向后兼容旧的配置方式
    """
    # 提供商设置（字典：provider_id -> ProviderSettings）
    provider_settings: Dict[str, ProviderSettings] = field(default_factory=dict)
    
    # 模型设置
    craft_model_settings: ModelSettings = field(default_factory=ModelSettings)
    generate_model_settings: ModelSettings = field(default_factory=ModelSettings)
    
    # 是否使用相同的模型设置
    use_same_model: bool = False
    
    # Prompt 设置
    sys_prompt_path: str = "prompts/sys/debug/Meta-Prompt-Architect.md"
    meta_prompt_path: str = "/tmp/prompt_craft/meta"
    
    # Memory 设置
    enable_memory: bool = False
    memory_path: str = "/tmp/prompt_craft/memory"
    
    def get_provider_setting(self, provider_id: str) -> ProviderSettings:
        """
        获取提供商设置
        
        Args:
            provider_id: 提供商 ID
            
        Returns:
            ProviderSettings 实例
        """
        if provider_id not in self.provider_settings:
            self.provider_settings[provider_id] = ProviderSettings(provider_id=provider_id)
        return self.provider_settings[provider_id]
    
    def set_provider_api_key(self, provider_id: str, api_key: str):
        """设置提供商 API Key"""
        setting = self.get_provider_setting(provider_id)
        setting.api_key = api_key
    
    def get_craft_provider_config(self) -> Optional[ProviderConfig]:
        """获取创作指导使用的提供商配置"""
        registry = get_provider_registry()
        return registry.get_provider(self.craft_model_settings.provider_id)
    
    def get_generate_provider_config(self) -> Optional[ProviderConfig]:
        """获取最终输出使用的提供商配置"""
        if self.use_same_model:
            return self.get_craft_provider_config()
        registry = get_provider_registry()
        return registry.get_provider(self.generate_model_settings.provider_id)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """从环境变量创建配置实例"""
        # 加载 .env 文件
        if _dotenv_available:
            load_dotenv(override=False)
        
        config = cls()
        
        # 加载提供商设置（支持多个提供商）
        # 格式：LLM_PROVIDER_{PROVIDER_ID}_API_KEY
        for provider_id in ['deepseek', 'openai', 'anthropic', 'custom']:
            api_key = os.getenv(f"LLM_PROVIDER_{provider_id.upper()}_API_KEY", "")
            if api_key:
                setting = ProviderSettings(
                    provider_id=provider_id,
                    api_key=api_key,
                    max_retries=_get_env_int(f"LLM_PROVIDER_{provider_id.upper()}_MAX_RETRIES"),
                    timeout=_get_env_int(f"LLM_PROVIDER_{provider_id.upper()}_TIMEOUT"),
                    custom_base_url=os.getenv(f"LLM_PROVIDER_{provider_id.upper()}_BASE_URL", "")
                )
                config.provider_settings[provider_id] = setting
        
        # 向后兼容：如果使用旧的 LLM_API_KEY，分配给 deepseek
        legacy_api_key = os.getenv("LLM_API_KEY", "")
        if legacy_api_key and 'deepseek' not in config.provider_settings:
            config.provider_settings['deepseek'] = ProviderSettings(
                provider_id='deepseek',
                api_key=legacy_api_key
            )
        
        # 加载创作指导模型设置
        config.craft_model_settings = ModelSettings(
            provider_id=os.getenv("LLM_CRAFT_PROVIDER", "deepseek"),
            model_id=os.getenv("LLM_CRAFT_MODEL", "deepseek-chat"),
            temperature=float(os.getenv("LLM_CRAFT_MODEL_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("LLM_CRAFT_MODEL_MAX_TOKENS", "4096")),
            top_p=float(os.getenv("LLM_CRAFT_MODEL_TOP_P", "0.7")),
            frequency_penalty=float(os.getenv("LLM_CRAFT_MODEL_FREQUENCY_PENALTY", "0.0")),
            presence_penalty=float(os.getenv("LLM_CRAFT_MODEL_PRESENCE_PENALTY", "0.0")),
            custom_model_id=os.getenv("LLM_CRAFT_CUSTOM_MODEL", "")
        )
        
        # 加载最终输出模型设置
        config.use_same_model = str_to_bool(os.getenv("LLM_USE_SAME_MODEL", "False"))
        
        if config.use_same_model:
            config.generate_model_settings = config.craft_model_settings
        else:
            config.generate_model_settings = ModelSettings(
                provider_id=os.getenv("LLM_GENERATE_PROVIDER", "deepseek"),
                model_id=os.getenv("LLM_GENERATE_MODEL", "deepseek-chat"),
                temperature=float(os.getenv("LLM_GENERATE_MODEL_TEMPERATURE", "0.3")),
                max_tokens=int(os.getenv("LLM_GENERATE_MODEL_MAX_TOKENS", "4096")),
                top_p=float(os.getenv("LLM_GENERATE_MODEL_TOP_P", "0.7")),
                frequency_penalty=float(os.getenv("LLM_GENERATE_MODEL_FREQUENCY_PENALTY", "0.0")),
                presence_penalty=float(os.getenv("LLM_GENERATE_MODEL_PRESENCE_PENALTY", "0.0")),
                custom_model_id=os.getenv("LLM_GENERATE_CUSTOM_MODEL", "")
            )
        
        # Prompt 设置
        config.sys_prompt_path = os.getenv("SYS_PROMPT_PATH", "prompts/Meta-Prompt-Generator.md")
        config.meta_prompt_path = os.getenv("META_PROMPT_PATH", "/tmp/prompt_craft/meta")
        
        # Memory 设置
        config.enable_memory = str_to_bool(os.getenv("ENABLE_MEMORY", "False"))
        config.memory_path = os.getenv("MEMORY_DIR", "/tmp/prompt_craft/memory")
        
        return config
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """验证配置的有效性"""
        registry = get_provider_registry()
        
        # 验证创作指导模型设置
        craft_provider = registry.get_provider(self.craft_model_settings.provider_id)
        if not craft_provider:
            return False, f"无效的提供商: {self.craft_model_settings.provider_id}"
        
        craft_setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        if not craft_setting.api_key:
            return False, f"提供商 {craft_provider.name} 缺少 API Key"
        
        # 验证模型
        if not registry.validate_provider_model(
            self.craft_model_settings.provider_id,
            self.craft_model_settings.get_effective_model_id(craft_provider)
        ):
            return False, f"无效的模型: {self.craft_model_settings.model_id}"
        
        # 验证最终输出模型设置（如果不使用相同模型）
        if not self.use_same_model:
            gen_provider = registry.get_provider(self.generate_model_settings.provider_id)
            if not gen_provider:
                return False, f"无效的提供商: {self.generate_model_settings.provider_id}"
            
            gen_setting = self.get_provider_setting(self.generate_model_settings.provider_id)
            if not gen_setting.api_key:
                return False, f"提供商 {gen_provider.name} 缺少 API Key"
            
            if not registry.validate_provider_model(
                self.generate_model_settings.provider_id,
                self.generate_model_settings.get_effective_model_id(gen_provider)
            ):
                return False, f"无效的模型: {self.generate_model_settings.model_id}"
        
        # 验证参数范围
        if not (0.0 <= self.craft_model_settings.temperature <= 1.0):
            return False, "创作指导模型 temperature 必须在 0.0 到 1.0 之间"
        
        if not (0.0 <= self.generate_model_settings.temperature <= 1.0):
            return False, "最终输出模型 temperature 必须在 0.0 到 1.0 之间"
        
        if not (0.0 <= self.craft_model_settings.top_p <= 1.0):
            return False, "创作指导模型 top_p 必须在 0.0 到 1.0 之间"
        
        if not (0.0 <= self.generate_model_settings.top_p <= 1.0):
            return False, "最终输出模型 top_p 必须在 0.0 到 1.0 之间"
        
        return True, None
    
    # ============ 向后兼容属性 ============
    
    @property
    def api_key(self) -> str:
        """向后兼容：获取主提供商的 API Key"""
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        return setting.api_key
    
    @api_key.setter
    def api_key(self, value: str):
        """向后兼容：设置主提供商的 API Key"""
        self.set_provider_api_key(self.craft_model_settings.provider_id, value)
    
    @property
    def base_url(self) -> str:
        """向后兼容：获取主提供商的 base_url"""
        provider = self.get_craft_provider_config()
        if not provider:
            return ""
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        return setting.get_effective_base_url(provider)
    
    @base_url.setter
    def base_url(self, value: str):
        """向后兼容：设置自定义 base_url"""
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        setting.custom_base_url = value
    
    @property
    def craft_model(self) -> str:
        """向后兼容：获取创作指导模型"""
        return self.craft_model_settings.model_id
    
    @craft_model.setter
    def craft_model(self, value: str):
        """向后兼容：设置创作指导模型"""
        self.craft_model_settings.model_id = value
    
    @property
    def craft_temperature(self) -> float:
        """向后兼容"""
        return self.craft_model_settings.temperature
    
    @craft_temperature.setter
    def craft_temperature(self, value: float):
        self.craft_model_settings.temperature = value
    
    @property
    def craft_max_tokens(self) -> int:
        return self.craft_model_settings.max_tokens
    
    @craft_max_tokens.setter
    def craft_max_tokens(self, value: int):
        self.craft_model_settings.max_tokens = value
    
    @property
    def craft_top_p(self) -> float:
        return self.craft_model_settings.top_p
    
    @property
    def craft_frequency_penalty(self) -> float:
        return self.craft_model_settings.frequency_penalty
    
    @property
    def craft_presence_penalty(self) -> float:
        return self.craft_model_settings.presence_penalty
    
    @property
    def generate_model(self) -> str:
        return self.generate_model_settings.model_id
    
    @generate_model.setter
    def generate_model(self, value: str):
        self.generate_model_settings.model_id = value
    
    @property
    def generate_model_temperature(self) -> float:
        return self.generate_model_settings.temperature
    
    @property
    def generate_model_max_tokens(self) -> int:
        return self.generate_model_settings.max_tokens
    
    @property
    def generate_model_top_p(self) -> float:
        return self.generate_model_settings.top_p
    
    @property
    def generate_model_frequency_penalty(self) -> float:
        return self.generate_model_settings.frequency_penalty
    
    @property
    def generate_model_presence_penalty(self) -> float:
        return self.generate_model_settings.presence_penalty
    
    @property
    def max_retries(self) -> int:
        """向后兼容：获取主提供商的 max_retries"""
        provider = self.get_craft_provider_config()
        if not provider:
            return 3
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        return setting.get_effective_max_retries(provider)
    
    @max_retries.setter
    def max_retries(self, value: int):
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        setting.max_retries = value
    
    @property
    def timeout(self) -> int:
        """向后兼容：获取主提供商的 timeout"""
        provider = self.get_craft_provider_config()
        if not provider:
            return 120
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        return setting.get_effective_timeout(provider)
    
    @timeout.setter
    def timeout(self, value: int):
        setting = self.get_provider_setting(self.craft_model_settings.provider_id)
        setting.timeout = value


def _get_env_int(key: str) -> Optional[int]:
    """从环境变量获取整数值"""
    value = os.getenv(key)
    if value:
        try:
            return int(value)
        except ValueError:
            pass
    return None
