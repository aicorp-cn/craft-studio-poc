# 贡献指南

感谢您对 Craft Studio 项目的关注！我们欢迎所有形式的贡献。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)

## 行为准则

请尊重所有参与者，保持友好和建设性的交流。

## 如何贡献

### 报告问题

如果您发现了 Bug 或有功能建议，请通过 [GitHub Issues](https://github.com/aicorp-cn/craft-studio-poc/issues) 提交。

提交 Issue 时请包含：

1. **问题描述** - 清晰描述遇到的问题
2. **复现步骤** - 如何复现该问题
3. **预期行为** - 您期望发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息** - Python 版本、操作系统等

### 提交代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开发环境设置

### 前置要求

- Python 3.8+
- Git
- pip 或 uv 包管理器

### 设置步骤

```bash
# 克隆您的 Fork
git clone https://github.com/YOUR_USERNAME/craft-studio-poc.git
cd craft-studio-poc

# 添加上游仓库
git remote add upstream https://github.com/aicorp-cn/craft-studio-poc.git

# 初始化子模块
git submodule update --init --recursive

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 同步上游更新

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://pep8.org/) 代码风格
- 使用 4 空格缩进
- 最大行长度 120 字符
- 使用类型注解

### 文档规范

- 所有公共模块、类、函数都应有 docstring
- 使用 Google 风格的 docstring 格式

```python
def example_function(param1: str, param2: int) -> bool:
    """函数简短描述。
    
    详细描述（可选）。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
        
    Returns:
        返回值描述
        
    Raises:
        ValueError: 异常描述
    """
    return True
```

### 导入规范

```python
# 标准库
import os
import sys

# 第三方库
import streamlit as st

# 本地模块
from conf import config
```

## 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (type)

| 类型 | 描述 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具相关 |

### 示例

```
feat(ui): add dark mode support

- Add theme toggle in settings panel
- Update CSS styles for dark theme
- Persist theme preference in session state

Closes #123
```

## Pull Request 流程

### 提交前检查

- [ ] 代码通过所有测试
- [ ] 代码符合项目代码规范
- [ ] 更新相关文档
- [ ] 提交信息符合规范

### PR 标题

使用与提交信息相同的格式：`<type>(<scope>): <subject>`

### PR 描述

请包含以下内容：

1. **更改内容** - 简要描述本次更改
2. **相关 Issue** - 关联的 Issue 编号
3. **测试情况** - 如何测试这些更改
4. **截图** - 如适用，添加截图

### 代码审查

所有 PR 都需要至少一位维护者的审查才能合并。请在审查期间：

- 及时响应审查意见
- 保持讨论的专业和友好

## 联系方式

如有任何问题，请通过以下方式联系我们：

- **邮箱**: our-aicorp@hotmail.com
- **GitHub Issues**: [提交问题](https://github.com/aicorp-cn/craft-studio-poc/issues)

---

再次感谢您的贡献！ 🎉