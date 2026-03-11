"""
核心模块

包含业务逻辑、数据模型和状态管理
"""

from .models import (
    # 新的状态模型
    TaskPhase,
    ProcessingMode,
    UserMode,
    TaskContext,
    UsageInfo,
    VALID_TRANSITIONS,
    # 向后兼容
    ProcessingState,
)

from .services import (
    LLMService,
    FileService,
)

from .state_manager import (
    StateManager,
    TaskStateMachine,
    StateTransitionError,
)

from .template_service import (
    Template,
    TemplateService,
    get_template_service,
)

__all__ = [
    # 新的状态模型
    "TaskPhase",
    "ProcessingMode",
    "UserMode",
    "TaskContext",
    "UsageInfo",
    "VALID_TRANSITIONS",
    # 状态管理
    "StateManager",
    "TaskStateMachine",
    "StateTransitionError",
    # 业务服务
    "LLMService",
    "FileService",
    # 模板服务
    "Template",
    "TemplateService",
    "get_template_service",
    # 向后兼容
    "ProcessingState",
]
