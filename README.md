<div align="center">

# arXiv-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

The skills for working with academic papers on arXiv.

</div>

- [arxiv-retriever](#arxiv-retriever): search and download **PDF**, **metadata**, and **BibTex** from arXiv using natural language.
- [pdf-parser](#pdf-parser): extract markdown and images from PDF using PaddleOCR.
- [Installation](#installation): support [skills.sh(https://skills.sh) and manual installations.

## arxiv-retriever

More details in [skills/arxiv-retriever/SKILL.md](skills/arxiv-retriever/SKILL.md).

![Demo](assets/demo.png)

### Examples

**Download latest papers on a topic:**
```
Download 10 latest papers about quantum machine learning
```

**Download specific papers by ID:**
```
Download papers 1706.03762 and 1810.04805
```

**Search by author and topic:**
```
Find papers about attention by author Vaswani
```

---

## pdf-parser

### Examples

**Convert downloaded papers:**
```
Convert these PDFs to markdown: arxiv/*/*.pdf
```

**Convert papers in a directory:**
```
Parse all PDFs in ./papers/ to markdown
```

---

## Installation

### Using `skills.sh` (Recommended)

```bash
# Install arxiv-retriever skill
npx skills add https://github.com/PKUfudawei/arxiv-skills --skill arxiv-retriever

# Install pdf-parser skill
npx  skills add https://github.com/PKUfudawei/arxiv-skills --skill pdf-parser

# Install both skills
npx skills add https://github.com/PKUfudawei/arxiv-skills
```

### Manual Installation

```bash
git clone https://github.com/PKUfudawei/arxiv-skills.git
cp -r arxiv-skills/skills/* ~/.claude/skills/
```

---

## Typical Workflow

```
1. Ask Claude to download papers from arXiv
2. Convert the PDFs to markdown for reading
```

---

## Acknowledgements

- [anthropics/skills](https://github.com/anthropics/skills)
- [arXiv API](https://info.arxiv.org/help/api/index.html)
- [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py)
- [nathangrigg/arxiv2bib](https://github.com/nathangrigg/arxiv2bib)
- [PaddlePaddle/PaddleOCR](https://github.com/PADDLEPADDLE/PADDLEOCR)
