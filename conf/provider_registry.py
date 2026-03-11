"""
提供商注册表模块

管理所有预设的大模型提供商配置
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ModelInfo:
    """模型信息"""
    id: str
    name: str
    max_tokens: int = 4096
    description: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ModelInfo':
        return cls(
            id=data['id'],
            name=data['name'],
            max_tokens=data.get('max_tokens', 4096),
            description=data.get('description', '')
        )


@dataclass
class ProviderDefaults:
    """提供商默认配置"""
    max_retries: int = 3
    timeout: int = 120
    temperature: float = 0.1
    top_p: float = 0.7
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProviderDefaults':
        return cls(
            max_retries=data.get('max_retries', 3),
            timeout=data.get('timeout', 120),
            temperature=data.get('temperature', 0.1),
            top_p=data.get('top_p', 0.7)
        )


@dataclass
class ProviderConfig:
    """提供商预设配置"""
    id: str
    name: str
    base_url: str
    description: str
    models: List[ModelInfo]
    defaults: ProviderDefaults
    allow_custom_model: bool = False
    allow_custom_base_url: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProviderConfig':
        return cls(
            id=data['id'],
            name=data['name'],
            base_url=data['base_url'],
            description=data.get('description', ''),
            models=[ModelInfo.from_dict(m) for m in data.get('models', [])],
            defaults=ProviderDefaults.from_dict(data.get('defaults', {})),
            allow_custom_model=data.get('allow_custom_model', False),
            allow_custom_base_url=data.get('allow_custom_base_url', False)
        )
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """获取指定模型信息"""
        for model in self.models:
            if model.id == model_id:
                return model
        return None


class ProviderRegistry:
    """
    提供商注册表
    
    负责加载和管理所有预设的大模型提供商配置
    """
    
    def __init__(self, config_path: str = "conf/providers.json"):
        """
        初始化提供商注册表
        
        Args:
            config_path: 提供商配置文件路径
        """
        self._providers: Dict[str, ProviderConfig] = {}
        self._config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """加载提供商配置文件"""
        try:
            config_file = Path(self._config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"提供商配置文件不存在: {self._config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析所有提供商
            for provider_data in data.get('providers', []):
                provider = ProviderConfig.from_dict(provider_data)
                self._providers[provider.id] = provider
            
        except json.JSONDecodeError as e:
            raise ValueError(f"提供商配置文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载提供商配置失败: {e}")
    
    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        """
        获取指定提供商配置
        
        Args:
            provider_id: 提供商 ID
            
        Returns:
            提供商配置，如果不存在则返回 None
        """
        return self._providers.get(provider_id)
    
    def list_providers(self) -> List[ProviderConfig]:
        """
        列出所有提供商
        
        Returns:
            提供商配置列表
        """
        return list(self._providers.values())
    
    def get_provider_names(self) -> Dict[str, str]:
        """
        获取提供商 ID 到名称的映射
        
        Returns:
            {provider_id: provider_name} 字典
        """
        return {p.id: p.name for p in self._providers.values()}
    
    def get_models(self, provider_id: str) -> List[ModelInfo]:
        """
        获取指定提供商的模型列表
        
        Args:
            provider_id: 提供商 ID
            
        Returns:
            模型信息列表
        """
        provider = self._providers.get(provider_id)
        return provider.models if provider else []
    
    def get_model_names(self, provider_id: str) -> Dict[str, str]:
        """
        获取指定提供商的模型 ID 到名称的映射
        
        Args:
            provider_id: 提供商 ID
            
        Returns:
            {model_id: model_name} 字典
        """
        models = self.get_models(provider_id)
        return {m.id: m.name for m in models}
    
    def validate_provider_model(self, provider_id: str, model_id: str) -> bool:
        """
        验证提供商和模型组合是否有效
        
        Args:
            provider_id: 提供商 ID
            model_id: 模型 ID
            
        Returns:
            是否有效
        """
        provider = self.get_provider(provider_id)
        if not provider:
            return False
        
        # 如果允许自定义模型，总是返回 True
        if provider.allow_custom_model:
            return True
        
        # 检查模型是否在列表中
        return any(m.id == model_id for m in provider.models)
    
    def reload(self):
        """重新加载配置文件"""
        self._providers.clear()
        self._load_config()


# 全局单例
_registry_instance: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """
    获取全局提供商注册表实例（单例模式）
    
    Returns:
        ProviderRegistry 实例
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ProviderRegistry()
    return _registry_instance
