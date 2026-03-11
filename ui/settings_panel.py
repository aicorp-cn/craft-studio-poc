"""
设置面板 UI 组件

提供简洁模式和专业模式的配置界面
"""

import streamlit as st
from typing import Optional

from conf import (
    AppConfig, ProviderSettings, ModelSettings,
    get_provider_registry, ProviderConfig
)
from core import StateManager, UserMode


class SettingsPanel:
    """设置面板组件集合"""
    
    @staticmethod
    def render_mode_switch() -> UserMode:
        """
        渲染用户模式切换开关
        
        Returns:
            当前选择的用户模式
        """
        current_mode = StateManager.get_user_mode()
        
        # 使用单选按钮切换模式
        mode_options = {
            "🎯 简洁模式": UserMode.SIMPLE,
            "⚙️ 专业模式": UserMode.ADVANCED
        }
        
        # 找到当前模式对应的显示文本
        current_option = "🎯 简洁模式" if current_mode == UserMode.SIMPLE else "⚙️ 专业模式"
        
        selected_option = st.radio(
            "使用模式",
            options=list(mode_options.keys()),
            index=list(mode_options.keys()).index(current_option),
            horizontal=True,
            help="简洁模式：快速配置，适合日常使用\n专业模式：完整配置，精细控制",
            key="user_mode_switch"
        )
        
        selected_mode = mode_options[selected_option]
        
        # 如果切换了模式，更新状态
        if selected_mode != current_mode:
            StateManager.set_user_mode(selected_mode)
        
        return selected_mode
    
    @staticmethod
    def render_simple_mode_settings(config: AppConfig) -> AppConfig:
        """
        渲染简洁模式设置面板
        
        Args:
            config: 应用配置
            
        Returns:
            更新后的配置
        """
        st.markdown("### 快速设置")
        
        registry = get_provider_registry()
        
        # 提供商选择
        provider_names = registry.get_provider_names()
        provider_options = list(provider_names.values())
        provider_ids = list(provider_names.keys())
        
        # 当前选择的提供商
        current_provider_idx = 0
        if config.craft_model_settings.provider_id in provider_ids:
            current_provider_idx = provider_ids.index(config.craft_model_settings.provider_id)
        
        selected_provider_name = st.selectbox(
            "服务商",
            provider_options,
            index=current_provider_idx,
            help="选择您使用的 AI 服务商"
        )
        
        selected_provider_id = provider_ids[provider_options.index(selected_provider_name)]
        
        # 更新提供商
        if selected_provider_id != config.craft_model_settings.provider_id:
            config.craft_model_settings.provider_id = selected_provider_id
            config.generate_model_settings.provider_id = selected_provider_id
        
        # API Key 输入
        provider_setting = config.get_provider_setting(selected_provider_id)
        api_key = st.text_input(
            "API Key",
            type="password",
            value=provider_setting.api_key,
            help="输入您的 API 密钥",
            key=f"simple_api_key_{selected_provider_id}"
        )
        provider_setting.api_key = api_key
        
        # 模型选择
        provider_config = registry.get_provider(selected_provider_id)
        if provider_config:
            models = registry.get_models(selected_provider_id)
            
            if models:
                model_options = [m.name for m in models]
                model_ids = [m.id for m in models]
                
                current_model_idx = 0
                if config.craft_model_settings.model_id in model_ids:
                    current_model_idx = model_ids.index(config.craft_model_settings.model_id)
                
                selected_model_name = st.selectbox(
                    "模型",
                    model_options,
                    index=current_model_idx,
                    help="选择使用的模型"
                )
                
                selected_model_id = model_ids[model_options.index(selected_model_name)]
                config.craft_model_settings.model_id = selected_model_id
                config.generate_model_settings.model_id = selected_model_id
            elif provider_config.allow_custom_model:
                custom_model = st.text_input(
                    "模型名称",
                    value=config.craft_model_settings.custom_model_id,
                    help="输入自定义模型名称"
                )
                config.craft_model_settings.custom_model_id = custom_model
                config.generate_model_settings.custom_model_id = custom_model
        
        return config
    
    @staticmethod
    def render_advanced_mode_settings(config: AppConfig) -> AppConfig:
        """
        渲染专业模式设置面板
        
        Args:
            config: 应用配置
            
        Returns:
            更新后的配置
        """
        registry = get_provider_registry()
        providers = registry.list_providers()
        
        # 提供商配置 Tab
        st.markdown("### 🔧 提供商配置")
        
        provider_tabs = st.tabs([p.name for p in providers])
        
        for tab, provider in zip(provider_tabs, providers):
            with tab:
                SettingsPanel._render_provider_config(config, provider)
        
        st.divider()
        
        # 模型设置区域
        st.markdown("### 📝 模型设置")
        
        # 是否使用相同模型
        use_same = st.checkbox(
            "创作指导和最终输出使用相同配置",
            value=config.use_same_model,
            help="勾选后，最终输出将使用与创作指导相同的模型配置"
        )
        config.use_same_model = use_same
        
        # 创作指导模型设置
        with st.expander("📋 创作指导模型设置", expanded=True):
            config.craft_model_settings = SettingsPanel._render_model_settings(
                config.craft_model_settings,
                "craft",
                registry
            )
        
        # 最终输出模型设置
        if not use_same:
            with st.expander("🎯 最终输出模型设置", expanded=True):
                config.generate_model_settings = SettingsPanel._render_model_settings(
                    config.generate_model_settings,
                    "generate",
                    registry
                )
        else:
            config.generate_model_settings = config.craft_model_settings
        
        return config
    
    @staticmethod
    def _render_provider_config(config: AppConfig, provider: ProviderConfig):
        """渲染单个提供商的配置"""
        provider_setting = config.get_provider_setting(provider.id)
        
        st.markdown(f"**{provider.description}**")
        
        # API Key
        api_key = st.text_input(
            "API Key",
            type="password",
            value=provider_setting.api_key,
            key=f"provider_{provider.id}_api_key",
            help=f"{provider.name} 的 API 密钥"
        )
        provider_setting.api_key = api_key
        
        # 自定义 Base URL（如果允许）
        if provider.allow_custom_base_url:
            custom_url = st.text_input(
                "Base URL（可选）",
                value=provider_setting.custom_base_url,
                placeholder=provider.base_url,
                key=f"provider_{provider.id}_base_url",
                help="留空使用默认 URL"
            )
            provider_setting.custom_base_url = custom_url
        else:
            st.text_input(
                "Base URL",
                value=provider.base_url,
                disabled=True,
                key=f"provider_{provider.id}_base_url_readonly"
            )
        
        # 高级选项
        with st.expander("⚙️ 高级选项"):
            col1, col2 = st.columns(2)
            
            with col1:
                max_retries = st.number_input(
                    "最大重试次数",
                    min_value=1,
                    max_value=10,
                    value=provider_setting.max_retries if provider_setting.max_retries is not None else provider.defaults.max_retries,
                    key=f"provider_{provider.id}_max_retries"
                )
                provider_setting.max_retries = max_retries
            
            with col2:
                timeout = st.number_input(
                    "超时时间（秒）",
                    min_value=10,
                    max_value=300,
                    value=provider_setting.timeout if provider_setting.timeout is not None else provider.defaults.timeout,
                    key=f"provider_{provider.id}_timeout"
                )
                provider_setting.timeout = timeout
    
    @staticmethod
    def _render_model_settings(
        model_settings: ModelSettings,
        prefix: str,
        registry
    ) -> ModelSettings:
        """渲染模型设置"""
        
        # 提供商选择
        provider_names = registry.get_provider_names()
        provider_options = list(provider_names.values())
        provider_ids = list(provider_names.keys())
        
        current_provider_idx = 0
        if model_settings.provider_id in provider_ids:
            current_provider_idx = provider_ids.index(model_settings.provider_id)
        
        selected_provider_name = st.selectbox(
            "提供商",
            provider_options,
            index=current_provider_idx,
            key=f"{prefix}_provider_select"
        )
        
        selected_provider_id = provider_ids[provider_options.index(selected_provider_name)]
        model_settings.provider_id = selected_provider_id
        
        # 模型选择（根据提供商联动）
        provider_config = registry.get_provider(selected_provider_id)
        if provider_config:
            models = registry.get_models(selected_provider_id)
            
            if models:
                model_options = [f"{m.name} (max: {m.max_tokens})" for m in models]
                model_ids = [m.id for m in models]
                
                current_model_idx = 0
                if model_settings.model_id in model_ids:
                    current_model_idx = model_ids.index(model_settings.model_id)
                
                selected_model_option = st.selectbox(
                    "模型",
                    model_options,
                    index=current_model_idx,
                    key=f"{prefix}_model_select"
                )
                
                selected_model_idx = model_options.index(selected_model_option)
                model_settings.model_id = model_ids[selected_model_idx]
                
                # 更新 max_tokens 默认值
                selected_model = models[selected_model_idx]
                if model_settings.max_tokens > selected_model.max_tokens:
                    model_settings.max_tokens = selected_model.max_tokens
            
            elif provider_config.allow_custom_model:
                custom_model = st.text_input(
                    "自定义模型名称",
                    value=model_settings.custom_model_id,
                    key=f"{prefix}_custom_model"
                )
                model_settings.custom_model_id = custom_model
        
        # 参数调整
        with st.expander("🎛️ 高级参数"):
            # Temperature
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=model_settings.temperature,
                step=0.1,
                key=f"{prefix}_temperature",
                help="控制输出随机性，越高越随机"
            )
            model_settings.temperature = temperature
            
            # Top P
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=model_settings.top_p,
                step=0.1,
                key=f"{prefix}_top_p",
                help="核采样参数"
            )
            model_settings.top_p = top_p
            
            # Max Tokens
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=8192,
                value=model_settings.max_tokens,
                step=100,
                key=f"{prefix}_max_tokens",
                help="最大生成令牌数"
            )
            model_settings.max_tokens = max_tokens
            
            # Frequency Penalty
            frequency_penalty = st.slider(
                "Frequency Penalty",
                min_value=0.0,
                max_value=2.0,
                value=model_settings.frequency_penalty,
                step=0.1,
                key=f"{prefix}_frequency_penalty",
                help="频率惩罚"
            )
            model_settings.frequency_penalty = frequency_penalty
        
        return model_settings
