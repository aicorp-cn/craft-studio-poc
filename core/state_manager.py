"""
状态管理器模块 

采用状态机模式管理任务生命周期
"""

import streamlit as st
import time
from typing import Optional, Callable, Any

from .models import (
    TaskContext, TaskPhase, ProcessingMode, UserMode, UsageInfo,
    ProcessingState, VALID_TRANSITIONS
)


class StateTransitionError(Exception):
    """状态转换错误"""
    pass


class TaskStateMachine:
    """
    任务状态机
    
    负责管理 TaskContext 的状态转换，确保所有转换符合预定义的规则
    """
    
    @staticmethod
    def transition(ctx: TaskContext, target_phase: TaskPhase, **updates) -> TaskContext:
        """
        执行状态转换
        
        Args:
            ctx: 当前任务上下文
            target_phase: 目标阶段
            **updates: 需要同时更新的其他字段
            
        Returns:
            更新后的 TaskContext（新实例）
            
        Raises:
            StateTransitionError: 如果状态转换不合法
        """
        if not ctx.can_transition_to(target_phase):
            raise StateTransitionError(
                f"非法状态转换: {ctx.phase.value} -> {target_phase.value}。"
                f"允许的转换: {[p.value for p in VALID_TRANSITIONS.get(ctx.phase, [])]}"
            )
        
        # 创建新的上下文实例（不可变更新模式）
        new_data = ctx.to_dict()
        new_data['phase'] = target_phase.value
        new_data['updated_at'] = time.time()
        
        # 应用额外更新
        for key, value in updates.items():
            if key in new_data:
                if isinstance(value, UsageInfo):
                    new_data[key] = value.to_dict()
                elif hasattr(value, 'value'):  # Enum
                    new_data[key] = value.value
                else:
                    new_data[key] = value
        
        return TaskContext.from_dict(new_data)
    
    @staticmethod
    def start_task(ctx: TaskContext, user_input: str) -> TaskContext:
        """
        开始新任务
        
        Args:
            ctx: 当前上下文
            user_input: 用户输入
            
        Returns:
            更新后的上下文
        """
        return TaskStateMachine.transition(
            ctx, 
            TaskPhase.ANALYZING,
            user_input=user_input,
            progress_message="正在分析您的需求...",
            progress_percent=10
        )
    
    @staticmethod
    def start_crafting(ctx: TaskContext) -> TaskContext:
        """开始生成创作指导"""
        return TaskStateMachine.transition(
            ctx,
            TaskPhase.CRAFTING,
            progress_message="正在生成创作指导框架...",
            progress_percent=30
        )
    
    @staticmethod
    def complete_crafting(ctx: TaskContext, meta_prompt: str, usage: UsageInfo) -> TaskContext:
        """
        完成创作指导生成
        
        根据处理模式决定下一阶段
        """
        next_phase = (
            TaskPhase.REVIEWING 
            if ctx.mode == ProcessingMode.STEPWISE 
            else TaskPhase.GENERATING
        )
        
        progress_percent = 50 if ctx.mode == ProcessingMode.STEPWISE else 60
        progress_message = (
            "创作指导已生成，等待审核..." 
            if ctx.mode == ProcessingMode.STEPWISE 
            else "正在生成最终内容..."
        )
        
        return TaskStateMachine.transition(
            ctx,
            next_phase,
            meta_prompt=meta_prompt,
            meta_usage=usage,
            progress_message=progress_message,
            progress_percent=progress_percent
        )
    
    @staticmethod
    def start_generating(ctx: TaskContext) -> TaskContext:
        """开始生成最终内容"""
        return TaskStateMachine.transition(
            ctx,
            TaskPhase.GENERATING,
            progress_message="正在生成最终内容...",
            progress_percent=70
        )
    
    @staticmethod
    def complete_generating(ctx: TaskContext, final_output: str, usage: UsageInfo) -> TaskContext:
        """完成最终内容生成"""
        return TaskStateMachine.transition(
            ctx,
            TaskPhase.COMPLETED,
            final_output=final_output,
            final_usage=usage,
            progress_message="处理完成！",
            progress_percent=100
        )
    
    @staticmethod
    def fail(ctx: TaskContext, error_message: str) -> TaskContext:
        """任务失败"""
        return TaskStateMachine.transition(
            ctx,
            TaskPhase.FAILED,
            error_message=error_message,
            progress_message=f"处理失败: {error_message}",
            progress_percent=0
        )
    
    @staticmethod
    def reset(ctx: TaskContext) -> TaskContext:
        """重置任务"""
        # 重置不需要验证转换，直接创建新上下文
        return TaskContext(mode=ctx.mode)


class StateManager:
    """
    状态管理器
    
    负责将 TaskContext 持久化到 Streamlit session_state
    提供统一的状态访问和更新接口
    """
    
    # Session state 中的键名
    CONTEXT_KEY = "pc_task_context"
    USER_INPUT_KEY = "pc_user_input"
    USER_MODE_KEY = "pc_user_mode"
    
    @staticmethod
    def initialize() -> None:
        """
        初始化状态管理器
        
        如果 session_state 中没有 TaskContext，则创建一个新的
        """
        if StateManager.CONTEXT_KEY not in st.session_state:
            st.session_state[StateManager.CONTEXT_KEY] = TaskContext()
        
        if StateManager.USER_INPUT_KEY not in st.session_state:
            st.session_state[StateManager.USER_INPUT_KEY] = ""
        
        if StateManager.USER_MODE_KEY not in st.session_state:
            st.session_state[StateManager.USER_MODE_KEY] = UserMode.SIMPLE
    
    @staticmethod
    def get_context() -> TaskContext:
        """
        获取当前任务上下文
        
        Returns:
            当前的 TaskContext 实例
        """
        StateManager.initialize()
        return st.session_state[StateManager.CONTEXT_KEY]
    
    @staticmethod
    def set_context(ctx: TaskContext) -> None:
        """
        设置任务上下文
        
        Args:
            ctx: 新的 TaskContext 实例
        """
        st.session_state[StateManager.CONTEXT_KEY] = ctx
    
    @staticmethod
    def update_context(**updates) -> TaskContext:
        """
        更新任务上下文（不改变阶段）
        
        Args:
            **updates: 要更新的字段
            
        Returns:
            更新后的上下文
        """
        ctx = StateManager.get_context()
        data = ctx.to_dict()
        
        for key, value in updates.items():
            if key in data:
                if isinstance(value, UsageInfo):
                    data[key] = value.to_dict()
                elif hasattr(value, 'value'):  # Enum
                    data[key] = value.value
                else:
                    data[key] = value
        
        data['updated_at'] = time.time()
        new_ctx = TaskContext.from_dict(data)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def transition_to(target_phase: TaskPhase, **updates) -> TaskContext:
        """
        执行状态转换并持久化
        
        Args:
            target_phase: 目标阶段
            **updates: 同时更新的其他字段
            
        Returns:
            转换后的上下文
        """
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.transition(ctx, target_phase, **updates)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def start_task(user_input: str) -> TaskContext:
        """开始新任务"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.start_task(ctx, user_input)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def start_crafting() -> TaskContext:
        """开始生成创作指导"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.start_crafting(ctx)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def complete_crafting(meta_prompt: str, usage: UsageInfo) -> TaskContext:
        """完成创作指导生成"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.complete_crafting(ctx, meta_prompt, usage)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def start_generating() -> TaskContext:
        """开始生成最终内容"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.start_generating(ctx)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def complete_generating(final_output: str, usage: UsageInfo) -> TaskContext:
        """完成最终内容生成"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.complete_generating(ctx, final_output, usage)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def fail(error_message: str) -> TaskContext:
        """任务失败"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.fail(ctx, error_message)
        StateManager.set_context(new_ctx)
        return new_ctx
    
    @staticmethod
    def reset() -> TaskContext:
        """重置任务"""
        ctx = StateManager.get_context()
        new_ctx = TaskStateMachine.reset(ctx)
        StateManager.set_context(new_ctx)
        StateManager.update_user_input("")
        return new_ctx
    
    @staticmethod
    def set_mode(mode: ProcessingMode) -> TaskContext:
        """设置处理模式"""
        return StateManager.update_context(mode=mode)
    
    @staticmethod
    def get_user_input() -> str:
        """获取用户输入"""
        StateManager.initialize()
        return st.session_state.get(StateManager.USER_INPUT_KEY, "")
    
    @staticmethod
    def update_user_input(value: str) -> None:
        """更新用户输入"""
        st.session_state[StateManager.USER_INPUT_KEY] = value
    
    @staticmethod
    def get_user_mode() -> UserMode:
        """获取当前用户模式"""
        StateManager.initialize()
        return st.session_state.get(StateManager.USER_MODE_KEY, UserMode.SIMPLE)
    
    @staticmethod
    def set_user_mode(mode: UserMode) -> None:
        """设置用户模式"""
        st.session_state[StateManager.USER_MODE_KEY] = mode
    
    @staticmethod
    def is_simple_mode() -> bool:
        """是否为简洁模式"""
        return StateManager.get_user_mode() == UserMode.SIMPLE
    
    @staticmethod
    def is_advanced_mode() -> bool:
        """是否为专业模式"""
        return StateManager.get_user_mode() == UserMode.ADVANCED
    
    # ============ 向后兼容接口 ============
    
    @staticmethod
    def initialize_states() -> None:
        """
        初始化所有状态变量（向后兼容）
        
        注意：此方法已废弃，请使用 initialize()
        """
        StateManager.initialize()
    
    @staticmethod
    def get_state() -> ProcessingState:
        """
        获取当前状态（向后兼容）
        
        返回一个 ProcessingState 实例，从 TaskContext 转换而来
        
        注意：此方法已废弃，请使用 get_context()
        """
        ctx = StateManager.get_context()
        return ProcessingState.from_task_context(ctx)
    
    @staticmethod
    def update_state(**kwargs) -> None:
        """
        更新状态（向后兼容）
        
        将旧的字段名映射到新的 TaskContext 字段
        
        注意：此方法已废弃，请使用 update_context() 或 transition_to()
        """
        ctx = StateManager.get_context()
        data = ctx.to_dict()
        
        # 字段映射：旧名称 -> 新名称
        field_mapping = {
            'meta_result': 'meta_prompt',
            'final_result': 'final_output',
            'current_step': 'progress_message',
            'progress_value': 'progress_percent',
        }
        
        # 处理模式映射
        if 'processing_mode' in kwargs:
            mode_value = kwargs.pop('processing_mode')
            if mode_value == "连续处理":
                data['mode'] = ProcessingMode.CONTINUOUS.value
            else:
                data['mode'] = ProcessingMode.STEPWISE.value
        
        # 处理阶段相关的状态转换
        if 'processing' in kwargs:
            processing = kwargs.pop('processing')
            if not processing and ctx.is_processing():
                # 停止处理 - 需要判断是完成还是失败
                pass  # 由其他字段决定
        
        # 处理步骤相关
        step_changes = {}
        for key in ['step1_processing', 'step2_processing', 'current_processing_step',
                    'meta_generation_complete', 'final_generation_complete']:
            if key in kwargs:
                step_changes[key] = kwargs.pop(key)
        
        # 如果有阶段相关的变化，尝试推断目标阶段
        if step_changes:
            target_phase = StateManager._infer_phase_from_step_changes(ctx, step_changes)
            if target_phase and ctx.can_transition_to(target_phase):
                data['phase'] = target_phase.value
        
        # 应用字段映射
        for old_key, new_key in field_mapping.items():
            if old_key in kwargs:
                data[new_key] = kwargs.pop(old_key)
        
        # 处理 usage 字段
        if 'meta_usage' in kwargs:
            usage = kwargs.pop('meta_usage')
            if isinstance(usage, dict):
                data['meta_usage'] = usage
            elif isinstance(usage, UsageInfo):
                data['meta_usage'] = usage.to_dict()
        
        if 'final_usage' in kwargs:
            usage = kwargs.pop('final_usage')
            if isinstance(usage, dict):
                data['final_usage'] = usage
            elif isinstance(usage, UsageInfo):
                data['final_usage'] = usage.to_dict()
        
        # 应用其他更新
        for key, value in kwargs.items():
            if key in data:
                data[key] = value
        
        data['updated_at'] = time.time()
        new_ctx = TaskContext.from_dict(data)
        StateManager.set_context(new_ctx)
    
    @staticmethod
    def _infer_phase_from_step_changes(ctx: TaskContext, changes: dict) -> Optional[TaskPhase]:
        """
        从旧的步骤变化推断目标阶段
        
        这是为了向后兼容旧代码的状态更新逻辑
        """
        if changes.get('step1_processing') == True:
            return TaskPhase.CRAFTING
        
        if changes.get('step2_processing') == True:
            return TaskPhase.GENERATING
        
        if changes.get('meta_generation_complete') == True and not changes.get('step1_processing'):
            if ctx.mode == ProcessingMode.STEPWISE:
                return TaskPhase.REVIEWING
        
        if changes.get('final_generation_complete') == True and not changes.get('step2_processing'):
            return TaskPhase.COMPLETED
        
        current_step = changes.get('current_processing_step')
        if current_step == 3:
            return TaskPhase.COMPLETED
        elif current_step == 0 and not changes.get('step1_processing'):
            return TaskPhase.IDLE
        
        return None
    
    @staticmethod
    def reset_states() -> None:
        """
        重置所有状态（向后兼容）
        
        注意：此方法已废弃，请使用 reset()
        """
        StateManager.reset()
