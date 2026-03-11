"""
Prompt Craft Studio - 智能提示词生成器

主程序入口，负责页面配置、UI 渲染和业务流程编排
采用异步处理模式，确保 UI 响应性

设计原则：
1. UI 与业务逻辑分离
2. 状态驱动的 UI 渲染
3. 异步处理不阻塞 UI
"""

import asyncio
import streamlit as st

from conf import AppConfig
from core import (
    LLMService, StateManager, TaskPhase, ProcessingMode, UserMode, UsageInfo
)
from ui import UIComponents, SettingsPanel


# ============ 页面配置 ============

st.set_page_config(
    page_title="Craft Studio - 智能提示词生成器",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============ 自定义 CSS 样式 ============

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
    }
    .main-header-text {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .sub-header {
        font-size: 0.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .main-content-section {
        margin-top: 1rem;
    }
    .input-section {
        margin-top: 1rem;
    }
    .results-section {
        margin-top: 1rem;
    }
    .status-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #1E88E5;
    }
    .token-info {
        background-color: #e8f5e9;
        padding: 0.5rem;
        border-radius: 4px;
        margin-top: 0.5rem;
    }
    .result-box {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }
    .step-container {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .highlight {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 3px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .sub-header {
            font-size: 1rem;
        }
        .st-emotion-cache-1v0mbdj {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============ 初始化 ============

# 初始化状态管理器
StateManager.initialize()

# 加载配置
config = AppConfig.from_env()


# ============ 回调函数 ============

def clear_all():
    """清空所有状态"""
    StateManager.reset()
    StateManager.update_user_input("")


def start_processing():
    """开始处理回调"""
    user_input = StateManager.get_user_input()
    
    if not user_input.strip():
        st.error("❌ 请输入您的需求")
        return
    
    # 验证配置
    is_valid, error_msg = config.validate()
    if not is_valid:
        st.error(f"❌ 配置错误: {error_msg}")
        return
    
    ctx = StateManager.get_context()
    
    # 防止重复处理
    if ctx.is_processing():
        st.warning("⚠️ 正在处理中，请稍候...")
        return
    
    # 如果已完成，先重置再开始
    if ctx.is_completed() or ctx.is_failed():
        StateManager.reset()
    
    # 开始任务
    StateManager.start_task(user_input)


# ============ 说明卡片 ============

with st.expander("ℹ️ 使用说明", expanded=False):
    st.markdown("""
    **Craft Studio** 用一句话描述您的需求，Craft Studio 将为您生成高质量内容：
    
    1. **AI 创作指导** - 读懂您的描述，自动生成内容创作指导框架
    2. **内容生成** - 基于创作指导生成最终内容
    
    **使用步骤：**
    - 在右侧输入您的需求
    - 配置侧边栏的参数（API 密钥、模型等）
    - 选择处理模式（连续处理或分步处理）
    - 点击开始按钮开始处理
    - 在左侧查看生成的创作指导和最终输出
    
    **处理模式说明：**
    - **连续处理**：自动完成全部流程，适合快速生成
    - **分步处理**：逐步执行，可在中间审核和修改创作指导
    """)


# ============ 侧边栏配置 ============

config = UIComponents.render_sidebar(config)


# ============ 获取当前状态 ============

ctx = StateManager.get_context()
state = StateManager.get_state()  # 向后兼容


# ============ 主内容布局 ============

# 动态调整列比例
if ctx.is_processing() or ctx.has_meta_prompt() or ctx.has_final_output():
    results_col, input_col = st.columns([2, 1])  # 处理中/有结果时放大左侧
else:
    results_col, input_col = st.columns([5, 2])  # 默认比例


# 左侧：结果展示区域
with results_col:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    UIComponents.render_results_area(state)
    st.markdown('</div>', unsafe_allow_html=True)


# 右侧：输入和控制区域
with input_col:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    with st.container():
        # 渲染输入区域
        user_input = UIComponents.render_input_area(state)[0]
        
        # 渲染操作工具栏
        UIComponents.render_action_toolbar(
            state,
            on_start_callback=start_processing,
            on_clear_callback=clear_all
        )
        
        # 渲染流程状态
        UIComponents.render_process_status(state)
    st.markdown('</div>', unsafe_allow_html=True)


# ============ 异步处理逻辑 ============

async def run_continuous_processing(llm_service: LLMService, user_input: str):
    """
    执行连续处理流程
    
    Args:
        llm_service: LLM 服务实例
        user_input: 用户输入
    """
    try:
        # 阶段1：生成创作指导
        # 注意：start_crafting 已在外层调用，这里直接执行
        meta_result, meta_usage, error = await llm_service.craft_meta_prompt(
            user_input, 
            config.craft_model, 
            config.craft_temperature, 
            config.sys_prompt_path
        )
        
        if error:
            StateManager.fail(error)
            return
        
        usage_info = UsageInfo.from_dict(meta_usage) if meta_usage else UsageInfo()
        StateManager.complete_crafting(meta_result, usage_info)
        
        # 阶段2：生成最终输出
        final_result, final_usage, error = await llm_service.gen_final_output(
            user_input, 
            meta_result, 
            config.generate_model, 
            config.generate_model_temperature
        )
        
        if error:
            StateManager.fail(error)
            return
        
        final_usage_info = UsageInfo.from_dict(final_usage) if final_usage else UsageInfo()
        StateManager.complete_generating(final_result, final_usage_info)
        
    except Exception as e:
        StateManager.fail(f"处理过程中发生错误: {str(e)}")


async def run_step1_processing(llm_service: LLMService, user_input: str):
    """
    执行分步处理的第一步（生成创作指导）
    
    Args:
        llm_service: LLM 服务实例
        user_input: 用户输入
    """
    try:
        # 注意：start_crafting 已在外层调用，这里直接执行
        meta_result, meta_usage, error = await llm_service.craft_meta_prompt(
            user_input, 
            config.craft_model, 
            config.craft_temperature, 
            config.sys_prompt_path
        )
        
        if error:
            StateManager.fail(error)
            return
        
        usage_info = UsageInfo.from_dict(meta_usage) if meta_usage else UsageInfo()
        StateManager.complete_crafting(meta_result, usage_info)
        
    except Exception as e:
        StateManager.fail(f"生成创作指导时发生错误: {str(e)}")


async def run_step2_processing(llm_service: LLMService, user_input: str, meta_prompt: str):
    """
    执行分步处理的第二步（生成最终内容）
    
    Args:
        llm_service: LLM 服务实例
        user_input: 用户输入
        meta_prompt: 创作指导框架
    """
    try:
        final_result, final_usage, error = await llm_service.gen_final_output(
            user_input, 
            meta_prompt, 
            config.generate_model, 
            config.generate_model_temperature
        )
        
        if error:
            StateManager.fail(error)
            return
        
        final_usage_info = UsageInfo.from_dict(final_usage) if final_usage else UsageInfo()
        StateManager.complete_generating(final_result, final_usage_info)
        
    except Exception as e:
        StateManager.fail(f"生成最终输出时发生错误: {str(e)}")


# 根据当前状态执行处理
if ctx.phase == TaskPhase.ANALYZING:
    # 分析阶段：先转换到 CRAFTING，然后执行处理
    llm_service = LLMService(config)
    user_input = StateManager.get_user_input()
    
    # 重要：必须先转换到 CRAFTING 状态
    StateManager.start_crafting()
    st.rerun()

elif ctx.phase == TaskPhase.CRAFTING:
    # CRAFTING 阶段：执行实际的生成逻辑
    llm_service = LLMService(config)
    user_input = StateManager.get_user_input()
    
    if ctx.mode == ProcessingMode.CONTINUOUS:
        # 连续处理模式
        with st.status("🚀 正在处理...", expanded=True) as status:
            st.write("📝 分析您的需求...")
            st.write("🎨 生成创作指导框架...")
            asyncio.run(run_continuous_processing(llm_service, user_input))
            
            status.update(label="✅ 处理完成！", state="complete")
        st.rerun()
    else:
        # 分步处理模式 - 只生成创作指导
        with st.status("🎨 正在生成创作指导...", expanded=True) as status:
            st.write("🔄 调用 AI 模型...")
            asyncio.run(run_step1_processing(llm_service, user_input))
            status.update(label="✅ 创作指导已生成！", state="complete")
        st.rerun()

elif ctx.phase == TaskPhase.GENERATING:
    # 分步模式的第二步
    llm_service = LLMService(config)
    user_input = StateManager.get_user_input()
    
    with st.status("🎯 正在生成最终内容...", expanded=True) as status:
        st.write("📋 使用创作指导框架...")
        st.write("🔄 调用 AI 模型...")
        asyncio.run(run_step2_processing(llm_service, user_input, ctx.meta_prompt))
        status.update(label="✅ 最终内容已生成！", state="complete")
    st.rerun()


# ============ 页脚 ============

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888;">🤖 Craft Studio - 轻创作伴侣</div>', 
    unsafe_allow_html=True
)
