from enum import Enum


class FormatType(str, Enum):
    """思维导图格式类型枚举，支持多种导图格式输出"""
    
    MARKDOWN = "markdown"     # Mermaid格式的思维导图
    XMIND = "xmind"          # XMind XML格式
    FREEMIND = "freemind"    # FreeMind XML格式  
    WEB_MIND_MAP = "web_mind_map"  # Web Mind Map JSON格式