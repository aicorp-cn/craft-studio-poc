"""
模板服务模块

管理创作指导框架模板的保存、加载和管理
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class Template:
    """模板数据模型"""
    id: str
    name: str
    content: str
    category: str = "自定义"
    description: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    use_count: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        """从字典创建实例"""
        return cls(**data)


class TemplateService:
    """
    模板管理服务
    
    提供模板的 CRUD 操作和模板库管理
    """
    
    def __init__(self, template_dir: str = "templates"):
        """
        初始化模板服务
        
        Args:
            template_dir: 模板存储目录
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.template_dir / "index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """确保索引文件存在"""
        if not self._index_file.exists():
            self._save_index({"templates": [], "categories": []})
    
    def _load_index(self) -> Dict:
        """加载索引文件"""
        try:
            with open(self._index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"templates": [], "categories": []}
    
    def _save_index(self, index_data: Dict):
        """保存索引文件"""
        with open(self._index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def save_template(
        self,
        name: str,
        content: str,
        category: str = "自定义",
        description: str = ""
    ) -> Tuple[bool, Optional[str]]:
        """
        保存模板
        
        Args:
            name: 模板名称
            content: 模板内容
            category: 分类
            description: 描述
            
        Returns:
            (是否成功, 错误信息) 元组
        """
        try:
            # 生成唯一 ID
            template_id = f"{int(time.time())}_{name.replace(' ', '_')}"
            
            # 创建模板对象
            template = Template(
                id=template_id,
                name=name,
                content=content,
                category=category,
                description=description
            )
            
            # 保存模板内容到文件
            template_file = self.template_dir / f"{template_id}.md"
            template_file.write_text(content, encoding='utf-8')
            
            # 更新索引
            index = self._load_index()
            
            # 检查是否已存在同名模板
            existing = [t for t in index['templates'] if t['name'] == name]
            if existing:
                return False, f"已存在同名模板: {name}"
            
            index['templates'].append(template.to_dict())
            
            # 更新分类列表
            if category not in index['categories']:
                index['categories'].append(category)
            
            self._save_index(index)
            
            return True, None
            
        except Exception as e:
            return False, f"保存模板失败: {str(e)}"
    
    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """
        列出模板
        
        Args:
            category: 分类过滤，None 表示全部
            
        Returns:
            模板列表
        """
        try:
            index = self._load_index()
            templates = [Template.from_dict(t) for t in index['templates']]
            
            if category:
                templates = [t for t in templates if t.category == category]
            
            # 按使用次数和创建时间排序
            templates.sort(key=lambda t: (-t.use_count, -t.created_at))
            
            return templates
            
        except Exception:
            return []
    
    def load_template(self, template_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        加载模板内容
        
        Args:
            template_id: 模板 ID
            
        Returns:
            (模板内容, 错误信息) 元组
        """
        try:
            template_file = self.template_dir / f"{template_id}.md"
            if not template_file.exists():
                return None, f"模板不存在: {template_id}"
            
            content = template_file.read_text(encoding='utf-8')
            
            # 更新使用次数
            self._increment_use_count(template_id)
            
            return content, None
            
        except Exception as e:
            return None, f"加载模板失败: {str(e)}"
    
    def delete_template(self, template_id: str) -> Tuple[bool, Optional[str]]:
        """
        删除模板
        
        Args:
            template_id: 模板 ID
            
        Returns:
            (是否成功, 错误信息) 元组
        """
        try:
            # 删除模板文件
            template_file = self.template_dir / f"{template_id}.md"
            if template_file.exists():
                template_file.unlink()
            
            # 更新索引
            index = self._load_index()
            index['templates'] = [t for t in index['templates'] if t['id'] != template_id]
            self._save_index(index)
            
            return True, None
            
        except Exception as e:
            return False, f"删除模板失败: {str(e)}"
    
    def get_categories(self) -> List[str]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        try:
            index = self._load_index()
            return index.get('categories', [])
        except Exception:
            return []
    
    def _increment_use_count(self, template_id: str):
        """增加模板使用次数"""
        try:
            index = self._load_index()
            for template in index['templates']:
                if template['id'] == template_id:
                    template['use_count'] = template.get('use_count', 0) + 1
                    template['updated_at'] = time.time()
                    break
            self._save_index(index)
        except Exception:
            pass  # 失败不影响主流程
    
    def get_template_by_name(self, name: str) -> Optional[Template]:
        """
        根据名称获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            Template 实例或 None
        """
        templates = self.list_templates()
        for template in templates:
            if template.name == name:
                return template
        return None


# 全局单例
_template_service_instance: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    """
    获取全局模板服务实例（单例模式）
    
    Returns:
        TemplateService 实例
    """
    global _template_service_instance
    if _template_service_instance is None:
        _template_service_instance = TemplateService()
    return _template_service_instance
