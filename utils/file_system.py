import os
from pathlib import Path
from typing import Tuple

def safe_file_path(file_path: str, base_path: str = "prompts/") -> Tuple[bool, str]:
    """安全的文件路径验证"""
    try:
        # 规范化路径
        normalized_path = os.path.normpath(file_path)
        base_path_obj = Path(base_path).resolve()
        requested_path = Path(normalized_path).resolve()
        
        # 检查是否在允许的目录内
        requested_path.relative_to(base_path_obj)
        
        # 检查文件扩展名
        if requested_path.suffix.lower() not in ['.md', '.txt']:
            return False, "不支持的文件类型"
        
        return True, str(requested_path)
    except ValueError:
        return False, "路径超出允许范围"