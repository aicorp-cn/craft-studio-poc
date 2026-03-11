from setuptools import setup, find_packages
import re

# 从__init__.py或项目文件中提取版本
try:
    with open("tiny_lm_client/__init__.py", "r", encoding="utf-8") as f:
        content = f.read()
        version_match = re.search(r"__version__\s+=\s+[\"']([^\"']*)[\"']", content)
        if version_match:
            version = version_match.group(1)
        else:
            version = "1.0.0"
except FileNotFoundError:
    version = "1.0.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tiny-lm-client",
    version=version,
    description="轻量级OpenAI兼容大模型客户端 - 提供类型安全、功能完整的AI模型访问接口",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI-Corp",
    author_email="our-aicorp@hotmail.com",
    url="https://github.com/aicorp-cn/tiny-lm-client",
    project_urls={
        "Bug Tracker": "https://github.com/aicorp-cn/tiny-lm-client/issues",
        "Documentation": "https://github.com/aicorp-cn/tiny-lm-client#readme",
        "Source Code": "https://github.com/aicorp-cn/tiny-lm-client",
        "Changelog": "https://github.com/aicorp-cn/tiny-lm-client/releases",
    },
    packages=find_packages(exclude=["test_env", "prompts", "examples", "docs"]),
    install_requires=[
        "httpx>=0.24.0,<1.0.0",
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    keywords=["openai", "llm", "client", "ai", "nlp", "gpt", "chatgpt", "async", "httpx", "api", "machine-learning", "artificial-intelligence"],
    license="Apache 2.0",
    license_files=("LICENSE",),
)