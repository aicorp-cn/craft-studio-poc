"""
配置模块

提供应用配置、提供商管理和模型设置
"""

from .config import (
    AppConfig,
    ProviderSettings,
    ModelSettings,
    str_to_bool
)

from .provider_registry import (
    ModelInfo,
    ProviderDefaults,
    ProviderConfig,
    ProviderRegistry,
    get_provider_registry
)

__all__ = [
    # 配置类
    "AppConfig",
    "ProviderSettings",
    "ModelSettings",
    "str_to_bool",
    # 提供商管理
    "ModelInfo",
    "ProviderDefaults",
    "ProviderConfig",
    "ProviderRegistry",
    "get_provider_registry",
]
