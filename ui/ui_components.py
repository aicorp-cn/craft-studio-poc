"""
UI 组件模块 

提供所有 UI 渲染组件，基于新的状态管理架构
"""

import streamlit as st
from typing import Tuple, Optional, Callable

from core.models import (
    TaskContext, TaskPhase, ProcessingMode, UserMode, UsageInfo,
    ProcessingState  # 向后兼容
)
from core.state_manager import StateManager
from .settings_panel import SettingsPanel


class UIComponents:
    """
    UI 组件集合
    
    提供统一的 UI 渲染接口，所有组件都是无状态的静态方法
    """
    
    @staticmethod
    def render_header():
        """渲染页面头部"""
        st.markdown(
            '<div class="main-header">🤖 Prompt Craft Studio</div>', 
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="sub-header">智能提示词生成器 - 一句描述，创建高质量内容</div>', 
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_sidebar(config):
        """
        渲染侧边栏配置面板（支持双模式）
        
        Args:
            config: AppConfig 配置对象
            
        Returns:
            更新后的配置对象
        """
        with st.sidebar:
            # 品牌标识
            st.markdown("""
                <div class="main-header">
                🤖 <br />
                <span class="main-header-text">Craft Studio</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("一句描述，创建高质量内容")
            
            st.divider()
            
            # 模式切换
            current_mode = SettingsPanel.render_mode_switch()
            
            st.divider()
            
            # 根据模式渲染不同的设置面板
            if current_mode == UserMode.SIMPLE:
                config = SettingsPanel.render_simple_mode_settings(config)
            else:
                config = SettingsPanel.render_advanced_mode_settings(config)
            
            st.divider()
            
            # 文件设置（两种模式都显示）
            with st.expander("📁 文件设置", expanded=False):
                config.sys_prompt_path = st.text_input(
                    "系统提示文件路径", 
                    config.sys_prompt_path,
                    help="包含系统提示的文件路径"
                )
        
        return config
    
    @staticmethod
    def render_input_area(state: ProcessingState) -> Tuple[str, Optional[str], Optional[str]]:
        """
        渲染输入区域
        
        Args:
            state: 处理状态（兼容旧接口）
            
        Returns:
            (用户输入, 文件内容, 占位符) 元组
        """
        tab1, tab2 = st.tabs(["📝 输入文本", "📁 上传文件"])
        
        with tab1:
            user_input = st.text_area(
                "请输入您的需求", 
                value=StateManager.get_user_input(),
                key="text_input_value",
                height=200,
                placeholder="例如：编写一篇关于人工智能在医疗领域应用的深度分析报告，要求包含技术原理、应用场景、发展趋势和挑战分析等内容...",
                help="一句话描述您需要生成的内容"
            )
            StateManager.update_user_input(user_input)
        
        with tab2:
            uploaded_file = st.file_uploader(
                "上传文本文件", 
                type=['txt', 'md'],
                help="上传包含您需求的文本文件"
            )
            if uploaded_file:
                try:
                    file_content = uploaded_file.read().decode('utf-8')
                    StateManager.update_user_input(file_content)
                    user_input = file_content
                    st.success(f"✅ 已加载文件: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ 文件读取失败: {str(e)}")
        
        return user_input, None, None
    
    @staticmethod
    def render_input_area_v2() -> str:
        """
        渲染输入区域（新版 API）
        
        Returns:
            用户输入文本
        """
        ctx = StateManager.get_context()
        
        tab1, tab2 = st.tabs(["📝 输入文本", "📁 上传文件"])
        
        with tab1:
            user_input = st.text_area(
                "请输入您的需求", 
                value=StateManager.get_user_input(),
                key="text_input_value",
                height=200,
                placeholder="例如：编写一篇关于人工智能在医疗领域应用的深度分析报告...",
                help="一句话描述您需要生成的内容",
                disabled=ctx.is_processing()  # 处理中禁用输入
            )
            StateManager.update_user_input(user_input)
        
        with tab2:
            uploaded_file = st.file_uploader(
                "上传文本文件", 
                type=['txt', 'md'],
                help="上传包含您需求的文本文件",
                disabled=ctx.is_processing()
            )
            if uploaded_file:
                try:
                    file_content = uploaded_file.read().decode('utf-8')
                    StateManager.update_user_input(file_content)
                    user_input = file_content
                    st.success(f"✅ 已加载文件: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ 文件读取失败: {str(e)}")
        
        return user_input
    
    @staticmethod
    def render_action_toolbar(
        state: ProcessingState, 
        on_start_callback: Callable, 
        on_clear_callback: Callable
    ) -> bool:
        """
        渲染操作工具栏
        
        Args:
            state: 处理状态
            on_start_callback: 开始处理的回调函数
            on_clear_callback: 清空的回调函数
            
        Returns:
            是否点击了处理按钮
        """
        ctx = StateManager.get_context()
        
        with st.container(border=True):
            # 处理模式选择
            mode_options = ["连续处理", "分步处理"]
            current_mode_index = 0 if ctx.mode == ProcessingMode.CONTINUOUS else 1
            
            processing_mode = st.selectbox(
                "处理模式", 
                mode_options,
                index=current_mode_index,
                help="连续处理：一键完成全流程；分步处理：逐步执行可审核修改",
                key="mode_selector_toolbar",
                disabled=ctx.is_processing()
            )
            
            # 更新处理模式
            new_mode = ProcessingMode.CONTINUOUS if processing_mode == "连续处理" else ProcessingMode.STEPWISE
            if new_mode != ctx.mode:
                StateManager.set_mode(new_mode)
            
            # 按钮行
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                # 根据状态显示不同的按钮文字
                if ctx.is_processing():
                    button_text = "⏳ 处理中..."
                elif ctx.is_completed():
                    button_text = "🔄 重新生成"
                else:
                    button_text = "🚀 开始"
                
                process_btn = st.button(
                    button_text, 
                    type="primary", 
                    use_container_width=True, 
                    on_click=on_start_callback,
                    disabled=ctx.is_processing()
                )
            
            with col_btn2:
                clear_btn = st.button(
                    "🗑️ 清空", 
                    use_container_width=True, 
                    on_click=on_clear_callback,
                    disabled=ctx.is_processing()
                )
        
        return process_btn
    
    @staticmethod
    def render_control_buttons(
        state: ProcessingState, 
        on_start_callback: Callable, 
        on_clear_callback: Callable
    ) -> bool:
        """渲染控制按钮（向后兼容）"""
        return UIComponents.render_action_toolbar(state, on_start_callback, on_clear_callback)
    
    @staticmethod
    def render_process_status(state: ProcessingState):
        """
        渲染流程状态指示器
        
        Args:
            state: 处理状态
        """
        ctx = StateManager.get_context()
        
        with st.container():
            # 确定每个步骤的状态类
            step1_class, step2_class, step3_class = UIComponents._get_step_classes(ctx)
            
            # 渲染三步流程指示器
            st.markdown(f'''
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin: 10px 0; border: 1px solid #e9ecef;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="text-align: center; flex: 1; padding: 8px;">
                        <div style="width: 30px; height: 30px; margin: 0 auto 5px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background-color: {UIComponents._get_step_color(step1_class)}; color: white; font-size: 0.9em; font-weight: bold;">1</div>
                        <div style="font-size: 0.8em; color: {UIComponents._get_text_color(step1_class)}; font-weight: {'bold' if step1_class != 'pending' else 'normal'};">输入需求</div>
                    </div>
                    <div style="font-size: 1.2em; color: #6c757d;">→</div>
                    <div style="text-align: center; flex: 1; padding: 8px;">
                        <div style="width: 30px; height: 30px; margin: 0 auto 5px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background-color: {UIComponents._get_step_color(step2_class)}; color: white; font-size: 0.9em; font-weight: bold;">2</div>
                        <div style="font-size: 0.8em; color: {UIComponents._get_text_color(step2_class)}; font-weight: {'bold' if step2_class != 'pending' else 'normal'};">处理中</div>
                    </div>
                    <div style="font-size: 1.2em; color: #6c757d;">→</div>
                    <div style="text-align: center; flex: 1; padding: 8px;">
                        <div style="width: 30px; height: 30px; margin: 0 auto 5px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background-color: {UIComponents._get_step_color(step3_class)}; color: white; font-size: 0.9em; font-weight: bold;">3</div>
                        <div style="font-size: 0.8em; color: {UIComponents._get_text_color(step3_class)}; font-weight: {'bold' if step3_class != 'pending' else 'normal'};">生成结果</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # 渲染当前状态信息
            UIComponents._render_status_details(ctx, state)
    
    @staticmethod
    def _get_step_classes(ctx: TaskContext) -> Tuple[str, str, str]:
        """根据当前阶段确定步骤状态类"""
        phase = ctx.phase
        
        if phase == TaskPhase.IDLE:
            return 'pending', 'pending', 'pending'
        elif phase == TaskPhase.ANALYZING:
            return 'active', 'pending', 'pending'
        elif phase == TaskPhase.CRAFTING:
            return 'completed', 'active', 'pending'
        elif phase == TaskPhase.REVIEWING:
            return 'completed', 'completed', 'pending'
        elif phase == TaskPhase.GENERATING:
            return 'completed', 'completed', 'active'
        elif phase == TaskPhase.COMPLETED:
            return 'completed', 'completed', 'completed'
        elif phase == TaskPhase.FAILED:
            return 'completed', 'failed', 'pending'
        else:
            return 'pending', 'pending', 'pending'
    
    @staticmethod
    def _get_step_color(step_class: str) -> str:
        """获取步骤指示器的颜色"""
        colors = {
            'pending': '#6c757d',
            'active': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545'
        }
        return colors.get(step_class, '#6c757d')
    
    @staticmethod
    def _get_text_color(step_class: str) -> str:
        """获取步骤文字的颜色"""
        colors = {
            'pending': '#6c757d',
            'active': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545'
        }
        return colors.get(step_class, '#6c757d')
    
    @staticmethod
    def _render_status_details(ctx: TaskContext, state: ProcessingState):
        """渲染详细状态信息"""
        phase = ctx.phase
        
        # 显示进度条（连续模式或处理中）
        if ctx.mode == ProcessingMode.CONTINUOUS or ctx.is_processing():
            if ctx.progress_message:
                st.markdown(
                    f'<div style="padding: 8px; margin: 5px 0; background-color: #f1f8e9; border-radius: 4px; color: #336600;">🔄 {ctx.progress_message}</div>', 
                    unsafe_allow_html=True
                )
            if ctx.progress_percent > 0:
                st.progress(ctx.progress_percent / 100)
        
        # 分步模式的步骤按钮
        if ctx.mode == ProcessingMode.STEPWISE and not ctx.is_processing():
            if phase == TaskPhase.REVIEWING:
                # 已完成创作指导，等待用户确认
                st.info("📋 创作指导已生成，请审核后继续")
                if st.button("🔄 执行步骤2：生成最终输出", key="step2_btn", use_container_width=True, type="secondary"):
                    UIComponents.start_final_generation()
            elif phase == TaskPhase.COMPLETED:
                st.markdown(
                    '<div style="padding: 10px; margin: 10px 0; background-color: #d4edda; color: #155724; border-radius: 4px; border: 1px solid #c3e6cb;">✅ 所有步骤已完成！</div>', 
                    unsafe_allow_html=True
                )
        
        # 错误状态
        if phase == TaskPhase.FAILED and ctx.error_message:
            st.error(f"❌ {ctx.error_message}")
            if st.button("🔄 重试", key="retry_btn"):
                StateManager.reset()
                st.rerun()
    
    @staticmethod
    def render_results_area(state: ProcessingState) -> Tuple[any, any]:
        """
        渲染结果展示区域
        
        Args:
            state: 处理状态
            
        Returns:
            (meta_container, final_container) 元组
        """
        ctx = StateManager.get_context()
        
        tab_meta, tab_final = st.tabs(["📋 创作指导框架", "🎯 最终输出"])
        
        with tab_meta:
            meta_container = st.container()
            with meta_container:
                if ctx.meta_prompt:
                    # 展示创作指导框架
                    # st.markdown("**创作指导框架：**")
                    
                    # 使用可编辑的文本区域（分步模式下允许编辑）
                    if ctx.mode == ProcessingMode.STEPWISE and ctx.phase == TaskPhase.REVIEWING:
                        edited_meta = st.text_area(
                            "编辑框架内容（可选）",
                            value=ctx.meta_prompt,
                            height=300,
                            key="meta_editor",
                            help="您可以修改创作指导框架后再生成最终内容"
                        )
                        if edited_meta != ctx.meta_prompt:
                            StateManager.update_context(meta_prompt=edited_meta)
                    else:
                        # 使用 Markdown 展示
                        # st.markdown(ctx.meta_prompt)
                        from streamlit_markmap import markmap
                        markmap(ctx.meta_prompt)
                    
                    # Token 使用信息
                    if ctx.meta_usage and ctx.meta_usage.total_tokens > 0:
                        usage = ctx.meta_usage
                        token_info = (
                            f"**创作指导生成 - Token 使用:** "
                            f"输入: `{usage.prompt_tokens}`, "
                            f"输出: `{usage.completion_tokens}`, "
                            f"总计: `{usage.total_tokens}`"
                        )
                        st.markdown(
                            f'<div class="token-info">{token_info}</div>', 
                            unsafe_allow_html=True
                        )
                    
                    # 操作按钮
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.download_button(
                            "📥 下载框架",
                            ctx.meta_prompt,
                            file_name="meta_prompt.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                else:
                    st.info("💡 创作指导框架将在处理后显示在这里")

        
        with tab_final:
            final_container = st.container()
            with final_container:
                if ctx.final_output:
                    # st.markdown("**最终输出结果：**")
                    st.markdown(ctx.final_output)
                    
                    # Token 使用信息
                    if ctx.final_usage and ctx.final_usage.total_tokens > 0:
                        usage = ctx.final_usage
                        token_info = (
                            f"**最终输出生成 - Token 使用:** "
                            f"输入: `{usage.prompt_tokens}`, "
                            f"输出: `{usage.completion_tokens}`, "
                            f"总计: `{usage.total_tokens}`"
                        )
                        st.markdown(
                            f'<div class="token-info">{token_info}</div>', 
                            unsafe_allow_html=True
                        )
                    
                    # 操作按钮
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.download_button(
                            "📥 下载结果",
                            ctx.final_output,
                            file_name="output.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                else:
                    st.info("💡 最终输出结果将在处理完成后显示在这里")
        
        return meta_container, final_container
    
    @staticmethod
    def start_meta_generation():
        """开始创作指导生成（分步模式）"""
        user_input = StateManager.get_user_input()
        
        if not user_input.strip():
            st.error("❌ 请输入您的需求")
            return
        
        ctx = StateManager.get_context()
        
        if ctx.is_processing():
            st.warning("⚠️ 正在处理中，请稍候...")
            return
        
        # 开始任务
        StateManager.start_task(user_input)
    
    @staticmethod
    def start_final_generation():
        """开始最终输出生成（分步模式）"""
        ctx = StateManager.get_context()
        
        if not ctx.meta_prompt:
            st.error("❌ 请先完成创作指导生成步骤")
            return
        
        if ctx.is_processing():
            st.warning("⚠️ 正在处理中，请稍候...")
            return
        
        # 开始生成最终内容
        StateManager.start_generating()
