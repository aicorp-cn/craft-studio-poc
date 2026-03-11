# Craft Studio - 智能提示词生成器

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

> 🤖 一句话描述需求，AI 为您生成高质量内容

## 📋 项目概述

**Craft Studio** 是一个智能提示词生成工具，旨在帮助用户将模糊的需求转化为高质量的内容输出。只需用一句话描述您的需求，Craft Studio 将自动：

1. **AI 创作指导** - 分析您的需求，自动生成内容创作指导框架
2. **内容生成** - 基于创作指导生成最终内容

### ✨ 核心特性

- **🎯 一句话启动** - 无需专业技能，简单描述即可开始创作
- **🔄 双模式处理** - 支持连续处理和分步处理两种模式
- **🧠 多模型支持** - 支持 DeepSeek、OpenAI、Anthropic 等多种 LLM 提供商
- **⚡ 流式输出** - 实时展示生成进度，优化用户体验
- **🎨 可视化思维导图** - 支持创作指导框架的 Markmap 可视化展示
- **⚙️ 灵活配置** - 支持独立配置创作指导和最终输出使用的模型

### 📚 应用场景

| 场景 | 描述 |
|------|------|
| **儿童绘本创作** | 一句话讲述常识，生成生动绘本系列 |
| **知识卡片制作** | 将知识点转化为生动交互卡片 |
| **技能教程编写** | 专业技能沉淀为沉浸式教学指南 |
| **音视频剧本** | 创意想法翻译为具象化脚本 |
| **内容摘要** | 长文内容快速生成精炼摘要 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 或 uv 包管理器

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/aicorp-cn/craft-studio-poc.git
cd craft-studio-poc

# 初始化子模块
git submodule update --init --recursive

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制环境变量模板（如需要）：
```bash
cp .env.example .env
```

2. 配置 API Key：
```bash
# 编辑 .env 文件，添加您的 API Key
LLM_PROVIDER_DEEPSEEK_API_KEY=your-api-key-here
```

或通过 Streamlit UI 侧边栏直接配置。

### 运行

```bash
streamlit run prompt_craft_studio.py
```

## 📖 使用说明

### 基本流程

1. **输入需求** - 在右侧输入框中用一句话描述您的需求
2. **配置参数** - 在侧边栏配置 API 密钥、模型等参数
3. **选择模式** - 选择"连续处理"或"分步处理"
4. **开始生成** - 点击开始按钮，等待 AI 生成内容

### 处理模式说明

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| **连续处理** | 自动完成全部流程 | 快速生成，无需干预 |
| **分步处理** | 逐步执行，可中间审核修改 | 需要控制内容方向 |

### 模型配置

Craft Studio 支持为创作指导和最终输出配置不同的模型：

- **创作指导模型** - 用于分析和生成创作框架，推荐使用推理能力强的模型
- **最终输出模型** - 用于生成最终内容，可根据内容类型选择合适模型

## 🏗️ 项目结构

```
craft_studio_poc/
├── prompt_craft_studio.py    # 主程序入口
├── requirements.txt           # 依赖配置
├── conf/                      # 配置模块
│   ├── config.py             # 应用配置类
│   ├── provider_registry.py  # 提供商注册表
│   └── providers.json        # 提供商配置
├── core/                      # 核心业务模块
│   ├── models.py             # 数据模型定义
│   ├── services.py           # LLM 服务封装
│   ├── state_manager.py      # 状态管理器
│   └── template_service.py   # 模板服务
├── ui/                        # UI 组件
│   ├── ui_components.py      # UI 组件实现
│   └── settings_panel.py     # 设置面板
├── utils/                     # 工具函数
├── prompts/                   # 提示词模板
│   ├── gen/                  # 生成流程提示词
│   └── sys/release/          # 正式版系统提示词
├── templates/                 # 内容模板
└── libs/                      # 依赖库
    └── tiny-llm-client/      # LLM 客户端子模块
```

## 🔧 高级配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_PROVIDER_DEEPSEEK_API_KEY` | DeepSeek API Key | - |
| `LLM_PROVIDER_OPENAI_API_KEY` | OpenAI API Key | - |
| `LLM_PROVIDER_ANTHROPIC_API_KEY` | Anthropic API Key | - |
| `LLM_CRAFT_PROVIDER` | 创作指导提供商 | `deepseek` |
| `LLM_CRAFT_MODEL` | 创作指导模型 | `deepseek-chat` |
| `LLM_GENERATE_PROVIDER` | 最终输出提供商 | `deepseek` |
| `LLM_GENERATE_MODEL` | 最终输出模型 | `deepseek-chat` |

### 自定义提供商

在 `conf/providers.json` 中可以添加自定义 LLM 提供商配置。

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/aicorp-cn/craft-studio-poc.git
cd craft-studio-poc

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写详细的 docstring

## 📄 许可证

本项目基于 [Apache 2.0 License](LICENSE) 开源。

## 📞 联系方式

- **维护者**: AICorp Team
- **邮箱**: our-aicorp@hotmail.com
- **问题反馈**: [GitHub Issues](https://github.com/aicorp-cn/craft-studio-poc/issues)

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - 优秀的 Python Web 应用框架
- [tiny-llm-client](https://github.com/aicorp-cn/tiny-llm-client) - 轻量级 LLM 客户端库
- 所有贡献者和用户

---

**Made with ❤️ by AICorp Team**