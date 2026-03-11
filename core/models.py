"""
数据模型模块 

采用业务驱动的状态设计，而非 UI 驱动
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
import time
import uuid


class TaskPhase(Enum):
    """
    任务阶段枚举 - 表示业务流程的各个阶段
    
    状态转换图:
    IDLE -> ANALYZING -> CRAFTING -> REVIEWING -> GENERATING -> COMPLETED
                 |           |            |             |           |
                 v           v            v             v           v
               FAILED      FAILED      CRAFTING      FAILED       IDLE
                 |           |        (回退修改)        |
                 v           v                         v
               IDLE       IDLE                       IDLE
    """
    IDLE = "idle"                    # 空闲，等待用户输入
    ANALYZING = "analyzing"          # 分析需求中（准备阶段）
    CRAFTING = "crafting"            # 生成创作指导框架中
    REVIEWING = "reviewing"          # 等待用户审核框架（分步模式特有）
    GENERATING = "generating"        # 生成最终内容中
    COMPLETED = "completed"          # 任务完成
    FAILED = "failed"                # 任务失败


class ProcessingMode(Enum):
    """处理模式枚举"""
    CONTINUOUS = "continuous"        # 连续处理：一键完成
    STEPWISE = "stepwise"            # 分步处理：逐步执行


class UserMode(Enum):
    """
    用户模式枚举
    
    支持简洁模式和专业模式，适应不同用户群体
    """
    SIMPLE = "simple"               # 简洁模式：普通用户，简化配置和操作
    ADVANCED = "advanced"           # 专业模式：专业用户，完整配置和控制


# 定义合法的状态转换
VALID_TRANSITIONS: Dict[TaskPhase, List[TaskPhase]] = {
    TaskPhase.IDLE: [TaskPhase.ANALYZING],
    TaskPhase.ANALYZING: [TaskPhase.CRAFTING, TaskPhase.FAILED],
    TaskPhase.CRAFTING: [TaskPhase.REVIEWING, TaskPhase.GENERATING, TaskPhase.FAILED],
    TaskPhase.REVIEWING: [TaskPhase.GENERATING, TaskPhase.CRAFTING, TaskPhase.IDLE],  # 可回退修改或取消
    TaskPhase.GENERATING: [TaskPhase.COMPLETED, TaskPhase.FAILED],
    TaskPhase.COMPLETED: [TaskPhase.IDLE],  # 开始新任务
    TaskPhase.FAILED: [TaskPhase.IDLE, TaskPhase.ANALYZING],  # 可重试
}


@dataclass
class UsageInfo:
    """Token 使用信息"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageInfo':
        """从字典创建 UsageInfo 实例"""
        if not data:
            return cls()
        return cls(
            prompt_tokens=data.get('prompt_tokens', 0),
            completion_tokens=data.get('completion_tokens', 0),
            total_tokens=data.get('total_tokens', 0)
        )
    
    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens
        }


@dataclass
class TaskContext:
    """
    任务上下文 - 封装一次完整任务的所有状态
    
    设计原则：
    1. 业务驱动：状态表示业务流程，而非 UI 控件
    2. 单一数据源：所有任务相关数据集中管理
    3. 不可变性：通过方法更新状态，确保状态转换合法性
    """
    # 任务标识
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # 当前阶段
    phase: TaskPhase = TaskPhase.IDLE
    
    # 处理模式
    mode: ProcessingMode = ProcessingMode.CONTINUOUS
    
    # 用户输入
    user_input: str = ""
    uploaded_file_content: str = ""
    
    # 中间结果：创作指导框架
    meta_prompt: str = ""
    meta_usage: UsageInfo = field(default_factory=UsageInfo)
    
    # 最终结果
    final_output: str = ""
    final_usage: UsageInfo = field(default_factory=UsageInfo)
    
    # 错误信息
    error_message: str = ""
    
    # 进度信息（用于 UI 展示）
    progress_message: str = ""
    progress_percent: int = 0
    
    # 时间戳
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def can_transition_to(self, target_phase: TaskPhase) -> bool:
        """
        验证状态转换是否合法
        
        Args:
            target_phase: 目标阶段
            
        Returns:
            是否可以转换到目标阶段
        """
        return target_phase in VALID_TRANSITIONS.get(self.phase, [])
    
    def get_effective_input(self) -> str:
        """获取有效的用户输入（优先使用上传的文件内容）"""
        return self.uploaded_file_content if self.uploaded_file_content else self.user_input
    
    def has_meta_prompt(self) -> bool:
        """是否已生成创作指导框架"""
        return bool(self.meta_prompt)
    
    def has_final_output(self) -> bool:
        """是否已生成最终输出"""
        return bool(self.final_output)
    
    def is_processing(self) -> bool:
        """是否正在处理中"""
        return self.phase in [
            TaskPhase.ANALYZING,
            TaskPhase.CRAFTING,
            TaskPhase.GENERATING
        ]
    
    def is_idle(self) -> bool:
        """是否处于空闲状态"""
        return self.phase == TaskPhase.IDLE
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.phase == TaskPhase.COMPLETED
    
    def is_failed(self) -> bool:
        """是否失败"""
        return self.phase == TaskPhase.FAILED
    
    def is_reviewing(self) -> bool:
        """是否等待审核"""
        return self.phase == TaskPhase.REVIEWING
    
    def get_phase_display_name(self) -> str:
        """获取当前阶段的显示名称"""
        phase_names = {
            TaskPhase.IDLE: "等待输入",
            TaskPhase.ANALYZING: "分析需求中",
            TaskPhase.CRAFTING: "生成创作指导中",
            TaskPhase.REVIEWING: "等待审核",
            TaskPhase.GENERATING: "生成最终内容中",
            TaskPhase.COMPLETED: "已完成",
            TaskPhase.FAILED: "处理失败"
        }
        return phase_names.get(self.phase, "未知状态")
    
    def reset(self) -> 'TaskContext':
        """
        重置任务上下文为初始状态
        
        Returns:
            重置后的新实例
        """
        return TaskContext(
            task_id=str(uuid.uuid4())[:8],
            mode=self.mode  # 保留处理模式
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            'task_id': self.task_id,
            'phase': self.phase.value,
            'mode': self.mode.value,
            'user_input': self.user_input,
            'uploaded_file_content': self.uploaded_file_content,
            'meta_prompt': self.meta_prompt,
            'meta_usage': self.meta_usage.to_dict(),
            'final_output': self.final_output,
            'final_usage': self.final_usage.to_dict(),
            'error_message': self.error_message,
            'progress_message': self.progress_message,
            'progress_percent': self.progress_percent,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskContext':
        """从字典创建实例"""
        return cls(
            task_id=data.get('task_id', str(uuid.uuid4())[:8]),
            phase=TaskPhase(data.get('phase', 'idle')),
            mode=ProcessingMode(data.get('mode', 'continuous')),
            user_input=data.get('user_input', ''),
            uploaded_file_content=data.get('uploaded_file_content', ''),
            meta_prompt=data.get('meta_prompt', ''),
            meta_usage=UsageInfo.from_dict(data.get('meta_usage', {})),
            final_output=data.get('final_output', ''),
            final_usage=UsageInfo.from_dict(data.get('final_usage', {})),
            error_message=data.get('error_message', ''),
            progress_message=data.get('progress_message', ''),
            progress_percent=data.get('progress_percent', 0),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time())
        )


# ============ 向后兼容：保留旧的 ProcessingState 类 ============
# 这是一个适配器，将旧的接口映射到新的 TaskContext

@dataclass
class ProcessingState:
    """
    处理状态数据模型（向后兼容包装器）
    
    注意：此类已废弃，仅用于向后兼容
    新代码请使用 TaskContext
    """
    processing: bool = False
    current_step: str = ""
    progress_value: int = 0
    meta_result: str = ""
    final_result: str = ""
    meta_usage: Dict[str, Any] = field(default_factory=dict)
    final_usage: Dict[str, Any] = field(default_factory=dict)
    processing_mode: str = "连续处理"
    current_processing_step: int = 0
    meta_generation_complete: bool = False
    final_generation_complete: bool = False
    step1_processing: bool = False
    step2_processing: bool = False
    user_input: str = ""
    uploaded_file_content: str = ""
    
    @classmethod
    def from_task_context(cls, ctx: TaskContext) -> 'ProcessingState':
        """从 TaskContext 创建 ProcessingState（向后兼容）"""
        # 映射处理模式
        processing_mode = "连续处理" if ctx.mode == ProcessingMode.CONTINUOUS else "分步处理"
        
        # 映射处理步骤
        step_mapping = {
            TaskPhase.IDLE: 0,
            TaskPhase.ANALYZING: 1,
            TaskPhase.CRAFTING: 1,
            TaskPhase.REVIEWING: 1,
            TaskPhase.GENERATING: 2,
            TaskPhase.COMPLETED: 3,
            TaskPhase.FAILED: 0
        }
        current_processing_step = step_mapping.get(ctx.phase, 0)
        
        return cls(
            processing=ctx.is_processing(),
            current_step=ctx.progress_message or ctx.get_phase_display_name(),
            progress_value=ctx.progress_percent,
            meta_result=ctx.meta_prompt,
            final_result=ctx.final_output,
            meta_usage=ctx.meta_usage.to_dict(),
            final_usage=ctx.final_usage.to_dict(),
            processing_mode=processing_mode,
            current_processing_step=current_processing_step,
            meta_generation_complete=ctx.has_meta_prompt(),
            final_generation_complete=ctx.has_final_output(),
            step1_processing=ctx.phase in [TaskPhase.ANALYZING, TaskPhase.CRAFTING],
            step2_processing=ctx.phase == TaskPhase.GENERATING,
            user_input=ctx.user_input,
            uploaded_file_content=ctx.uploaded_file_content
        )
    
    def reset(self):
        """重置状态为初始值"""
        self.processing = False
        self.current_step = ""
        self.progress_value = 0
        self.meta_result = ""
        self.final_result = ""
        self.meta_usage = {}
        self.final_usage = {}
        self.current_processing_step = 0
        self.meta_generation_complete = False
        self.final_generation_complete = False
        self.step1_processing = False
        self.step2_processing = False
        self.user_input = ""
        self.uploaded_file_content = ""
