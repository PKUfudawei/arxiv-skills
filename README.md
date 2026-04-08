<div align="center">
  
# arxiv-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

</div>

Two skills for working with academic papers:

1. **[arxiv-retriever](skills/arxiv-retriever/)** - Search and download arXiv papers from natural language requests
2. **[pdf-parser](skills/pdf-parser/)** - Convert PDF papers to markdown using PaddleOCR API

---

## Installation

### Option 1: Using `skills.sh` (Recommended)

Install individual skills directly from this repository:

```bash
# Install arxiv-retriever skill
npx -y skills add https://github.com/PKUfudawei/arxiv-skills --skill arxiv-retriever

# Install pdf-parser skill
npx -y skills add https://github.com/PKUfudawei/arxiv-skills --skill pdf-parser

# Install both skills
npx -y skills add https://github.com/PKUfudawei/arxiv-skills
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/PKUfudawei/arxiv-skills.git

# Copy skills to Claude skills directory
cp -r arxiv-skills/skills/* ~/.claude/skills/

# Restart Claude Code to load the skills
```

---

## arxiv-retriever

Search and download papers from arXiv by extracting parameters from natural language requests.

### Usage

Simply tell Claude what papers you need:

```
Download 10 latest papers about quantum machine learning
Download papers 1706.03762 and 1810.04805
Find papers about attention by author Vaswani
```

Claude will extract the parameters, show you the command, and ask for confirmation before executing.

### Query Syntax

| Prefix | Field | Example |
|--------|-------|-------------|
| `ti` | title | `ti:transformer` |
| `au` | author | `au:shaw` |
| `abs` | abstract | `abs:attention mechanism` |
| `co` | comment | `co:machine learning` |
| `jr` | journal reference | `jr:Neural Networks` |
| `cat` | subject category | `cat:cs.LG` (primary category) |
| `rn` | report number | `rn:CERN-TH-2023-001` |
| `id` | id | `id:2509.06855` (use `id_list` instead) |
| `all` | all fields | same as `al` |
| `` (empty) | all fields | same as `al` |

**Boolean operators:** `AND`, `OR`, `ANDNOT`, `NOT`, `()`

**Date filtering:** `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]`

### Examples

```bash
# Keyword search
python scripts/arxiv_retriever.py --query "quantum machine learning" --max_results 10

# By author and title
python scripts/arxiv_retriever.py --query "au:vaswani AND ti:transformer"

# Direct arXiv IDs
python scripts/arxiv_retriever.py --id_list "1706.03762,1810.04805"

# With date range
python scripts/arxiv_retriever.py --query "ti:attention AND submittedDate:[202301010000 TO 202412312359]"
```

### Output

```
./arxiv/
  <arxiv_id>/
    <arxiv_id>.pdf
    meta.json
    <arxiv_id>.bib
```

---

## pdf-parser

Convert PDF papers to markdown format using PaddleOCR-VL-1.5 API.

### Setup

1. **Get PaddleOCR API Token:**

   Obtain your token from [PaddleOCR AI Studio](https://aistudio.baidu.com/) and set:

   ```bash
   export PADDLE_TOKEN="your_token_here"
   ```

2. **Add to `~/.bashrc` for persistent configuration:**

   ```bash
   echo 'export PADDLE_TOKEN="your_token_here"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Usage

```bash
# Process PDFs matching a glob pattern
python3 skills/pdf-parser/scripts/paddleOCR.py -f "arxiv/*/*.pdf"

# Process specific directory
python3 skills/pdf-parser/scripts/paddleOCR.py -f "./papers/*.pdf"
```

### Features

- Concurrent processing (up to 16 PDFs in parallel)
- Extracts text content with layout preservation
- Downloads embedded images separately
- Skips already-processed files (`.md` exists)

### Output

```
input.pdf → input.md (same directory)
```

---

## Typical Workflow

```bash
# 1. Download papers using arxiv-retriever
# (Ask Claude to download papers you need)

# 2. Convert PDFs to markdown
python3 skills/pdf-parser/scripts/paddleOCR.py -f "arxiv/*/*.pdf"
```

---

## Loading into Claude Code

After installation, no additional configuration is needed. Simply ask Claude:

```
Help me download 5 papers about Transformer from arXiv
Convert these PDFs to markdown
```

Claude will automatically use the installed skills.



## Acknowledgements
Great thanks to the below projects:
- [anthropics/skills](https://github.com/anthropics/skills)
- [arXiv API User's manual](https://info.arxiv.org/help/api/index.html)
- [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py)
- [nathangrigg/arxiv2bib](https://github.com/nathangrigg/arxiv2bib)
- [PaddlePaddle/PaddleOCR](https://github.com/PADDLEPADDLE/PADDLEOCR)
