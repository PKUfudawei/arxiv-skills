<div align="center">

# arXiv-skills

**面向 arXiv 学术论文的 Agent 技能集 —— 检索下载论文，再把 PDF 解析成 Markdown。**

[English](./README.en.md) · [中文](./README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-blue)](https://skills.sh)

</div>

## 目录

- [技能总览](#技能总览)
- [快速安装](#快速安装)
- [arxiv-retriever：检索并下载论文](#arxiv-retriever检索并下载论文)
- [pdf-parser：PDF 转 Markdown](#pdf-parserpdf-转-markdown)
- [典型工作流](#典型工作流)
- [环境与依赖](#环境与依赖)
- [致谢](#致谢)

## 技能总览

| 技能 | 作用 |
|------|------|
| [arxiv-retriever](#arxiv-retriever检索并下载论文) | 用自然语言检索并下载 arXiv 论文（PDF + 元数据 + BibTeX） |
| [pdf-parser](#pdf-parserpdf-转-markdown) | 通过 PaddleOCR API 把论文 PDF 转换为带图片的 Markdown |

## 快速安装

本仓库遵循 [Agent Skills](https://agentskills.io) 目录规范（`skills/<name>/SKILL.md`），兼容 [skills.sh](https://skills.sh)，可配合任意 coding agent 使用：

```bash
# 安装 arxiv-retriever 技能
npx skills@latest add PKUfudawei/arxiv-skills --skill arxiv-retriever

# 安装 pdf-parser 技能
npx skills@latest add PKUfudawei/arxiv-skills --skill pdf-parser

# 两个都装（安装器会询问你要哪些）
npx skills@latest add PKUfudawei/arxiv-skills
```

## arxiv-retriever：检索并下载论文

从自然语言请求中解析参数（论文 ID、关键词、作者、分类、日期范围），检索 arXiv 并下载。每篇论文保存为 `<arxiv_id>.pdf`，并附 `meta.json` 与 `<arxiv_id>.bib`。

**安装这个技能**

```bash
npx skills@latest add PKUfudawei/arxiv-skills --skill arxiv-retriever
```

**然后让 coding agent 执行：**

```
下载 10 篇最新的量子机器学习论文
下载论文 1706.03762 和 2305.12345
查找作者 Vaswani 写的关于 attention 的论文
```

![Demo](assets/demo.png)

参数提取规则、查询语法与脚本参数详见 [skills/arxiv-retriever/SKILL.md](skills/arxiv-retriever/SKILL.md)。

## pdf-parser：PDF 转 Markdown

把下载好的论文 PDF 转为 Markdown（保持阅读顺序的正文 + 抽取的图片），底层使用 PaddleOCR-VL 云端 API，需要配置 `PADDLE_TOKEN`，详见技能文档。

**安装这个技能**

```bash
npx skills@latest add PKUfudawei/arxiv-skills --skill pdf-parser
```

**然后让 coding agent 执行：**

```
把这些 PDF 转成 markdown：arxiv/*/*.pdf
把 ./papers/ 目录下的所有 PDF 解析为 markdown
```

API 配置、输出格式与错误处理详见 [skills/pdf-parser/SKILL.md](skills/pdf-parser/SKILL.md)。

## 典型工作流

```
1. 让 agent 从 arXiv 下载论文（arxiv-retriever）
2. 把下载的 PDF 转成 Markdown 以便阅读（pdf-parser）
```

## 环境与依赖

- Python 3.9+
- arxiv-retriever：`pip install arxiv arxiv2bib requests tqdm`
- pdf-parser：`pip install requests tqdm python-dotenv`，并准备 PaddleOCR AI Studio 的 API token

## 致谢

- [anthropics/skills](https://github.com/anthropics/skills)
- [arXiv API](https://info.arxiv.org/help/api/index.html)
- [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py)
- [nathangrigg/arxiv2bib](https://github.com/nathangrigg/arxiv2bib)
- [PaddlePaddle/PaddleOCR](https://github.com/PADDLEPADDLE/PADDLEOCR)
