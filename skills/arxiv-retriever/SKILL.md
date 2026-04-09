---
name: arxiv-retriever
description: Search and download arXiv papers by extracting parameters from natural language requests
license: Proprietary. LICENSE has complete terms
---

# arXiv Paper Retrieval Guide

## Overview

Search arXiv and download papers by extracting parameters from user requests, synthesizing queries, and executing `scripts/arxiv_retriever.py` after user confirmation. For detailed arXiv API reference, see `references/arxiv.md`.

## Quick Start

```bash
# Install dependencies
pip3 install arxiv arxiv2bib

# Basic keyword search
python scripts/arxiv_retriever.py --query "quantum machine learning" --max_results 10

# Search by paper ID
python scripts/arxiv_retriever.py --id_list "1706.03762,2305.12345"

# Author + title search
python scripts/arxiv_retriever.py --query "au:vaswani AND ti:transformer"
```

## Workflow

```
User Prompt → Extract Parameters → Synthesize Query → User Confirmation → Execute Script → Download Papers
```

## Parameter Extraction

### Priority Order

1. **arXiv IDs** (highest priority): `"papers 1706.03762, 1810.04805"` → `--id_list "1706.03762,1810.04805"`
2. **Keywords**: `"quantum machine learning"` → `--query "quantum machine learning"`
3. **Author/title**: `"Vaswani's transformer"` → `--query "au:vaswani AND ti:transformer"`
4. **Sorting**: `"latest"` → `--sort_by SubmittedDate --sort_order Descending`
5. **Limit**: `"top 10"` → `--max_results 10`

### Date Range Conversion

| User Input | Query Format |
|------------|--------------|
| "papers from 2024" | `submittedDate:[202401010000 TO 202412312359]` |
| "last half year" | `submittedDate:[YYYYMMDD0000 TO CurrentDate2359]` |
| "June to December 2023" | `submittedDate:[202306010000 TO 202312312359]` |

## Query Syntax

### Field Prefixes

| Prefix | Field | Example |
|--------|-------|-------------|
| `ti` | title | `ti:transformer` |
| `au` | author | `au:shaw` |
| `abs` | abstract | `abs:attention mechanism` |
| `co` | comment | `co:machine learning` |
| `jr` | journal reference | `jr:Neural Networks` |
| `cat` | subject category | `cat:cs.LG` |
| `rn` | report number | `rn:CERN-TH-2023-001` |

### Boolean Operators

- `AND` — Both terms must match
- `OR` — At least one term matches
- `ANDNOT` / `NOT` — Exclude matching terms
- `()` — Group expressions

### Examples

```bash
# Keyword search
--query "quantum machine learning"

# Title + author
--query "ti:transformer AND au:vaswani"

# Category + abstract
--query "cat:cs.LG AND abs:deep learning"

# Date range + title
--query "ti:attention AND submittedDate:[202301010000 TO 202412312359]"

# Exclude terms
--query "ti:learning ANDNOT (reinforcement OR unsupervised)"

# Exact phrase
--query 'ti:"self-attention"'
```

## Script Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `--query` | str | Search query with field prefixes and boolean operators |
| `--id_list` | str | Comma-separated arXiv IDs (e.g., `"1706.03762,2305.12345"`) |
| `--max_results` | int | Maximum number of downloads |
| `--sort_by` | str | `Relevance` \| `LastUpdatedDate` \| `SubmittedDate` |
| `--sort_order` | str | `Ascending` \| `Descending` |
| `--output_dir` | str | Output directory (default: `~/arxiv`) |

## Few-Shot Examples

### Simple Keyword Search
```
User: Find me the latest 10 papers on quantum machine learning

→ Command: python scripts/arxiv_retriever.py --query "quantum machine learning" --max_results 10 --sort_by SubmittedDate --sort_order Descending
```

### Author + Title Search
```
User: Download Vaswani's transformer paper

→ Command: python scripts/arxiv_retriever.py --query "au:vaswani AND ti:transformer"
```

### Direct Paper IDs
```
User: Download papers 1706.03762 and 2305.12345

→ Command: python scripts/arxiv_retriever.py --id_list "1706.03762,2305.12345"
```

### Date Range Search
```
User: Find the first 20 papers about attention from 2024

→ Command: python scripts/arxiv_retriever.py --query "ti:attention AND submittedDate:[202401010000 TO 202412312359]" --max_results 20
```

## ⚠️ MANDATORY: User Confirmation Required

**CRITICAL:** You MUST display the synthesized command and wait for explicit confirmation (yes or revelant words) BEFORE executing.

### Confirmation Format
```
=== arXiv Search Command ===
python scripts/arxiv_retriever.py --query "au:He K AND submittedDate:[202504090000 TO 202604092359]"

Extracted Parameters:
  - query: au:He K AND submittedDate:[202504090000 TO 202604092359]

Execute this command? (yes/no)
```

### Required Steps
1. Display the full command
2. List extracted parameters
3. Ask "Execute this command? (yes/no)"
4. **WAIT** for explicit confirmation
5. Execute only after affirmative response

## Next Steps

- For detailed arXiv API reference, see `references/arxiv.md`
- For category taxonomy, see `references/arxiv_categories.md`
