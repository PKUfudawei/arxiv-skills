---
name: arxiv-retriever
description: Search and download arXiv papers by extracting parameters from natural language requests
license: Proprietary. LICENSE has complete terms
---

# arxiv-retriever

Search arXiv and download papers by extracting parameters from user requests, synthesizing queries, and executing `scripts/arxiv_retriever.py` after user confirmation.

## Workflow

```
User Prompt → Extract Parameters → Synthesize Query → User Confirmation → Execute Script → Download Papers
```

## Few-Shot Examples

### Example 1: Simple Keyword Search
```
User: Find me the latest 10 papers on quantum machine learning

→ Extracted: query="quantum machine learning", max_results=10, sort_by=SubmittedDate, sort_order=Descending
→ Command: python scripts/arxiv_retriever.py --query "quantum machine learning" --max_results 10 --sort_by SubmittedDate --sort_order Descending
→ Ask: "Execute this command? (yes/no)"
```

### Example 2: Author + Title Search
```
User: Download Vaswani's transformer paper

→ Extracted: query="au:vaswani AND ti:transformer"
→ Command: python scripts/arxiv_retriever.py --query "au:vaswani AND ti:transformer"
→ Ask: "Execute this command? (yes/no)"
```

### Example 3: arXiv IDs Directly
```
User: Download papers 1706.03762 and 2305.12345

→ Extracted: id_list="1706.03762,2305.12345"
→ Command: python scripts/arxiv_retriever.py --id_list "1706.03762,2305.12345"
→ Ask: "Execute this command? (yes/no)"
```

### Example 4: Date Range Search
```
User: Find the first 20 papers about attention from 2024

→ Extracted: query="ti:attention AND submittedDate:[202401010000 TO 202412312359]", max_results=20
→ Command: python scripts/arxiv_retriever.py --query "ti:attention AND submittedDate:[202401010000 TO 202412312359]" --max_results 20
→ Ask: "Execute this command? (yes/no)"
```

### Example 5: Category + Abstract Filter
```
User: Search for deep learning papers in cs.LG category

→ Extracted: query="cat:cs.LG AND abs:deep learning"
→ Command: python scripts/arxiv_retriever.py --query "cat:cs.LG AND abs:deep learning"
→ Ask: "Execute this command? (yes/no)"
```

### Example 6: Exclude Terms
```
User: Find learning papers but exclude reinforcement learning

→ Extracted: query="ti:learning ANDNOT (reinforcement OR RL)"
→ Command: python scripts/arxiv_retriever.py --query "ti:learning ANDNOT (reinforcement OR RL)"
→ Ask: "Execute this command? (yes/no)"
```

## Parameter Extraction Rules

### 1. arXiv ID (Highest Priority)
When user provides paper IDs directly:
```
"Download 1706.03762 and 1810.04805" → --id_list "1706.03762,1810.04805"
"paper 2107.05580v1" → --id_list "2107.05580v1"
```

### 2. Search Keywords
```
"quantum machine learning papers" → --query "quantum machine learning"
"find transformer related" → --query "transformer"
```

### 3. Author/Title
```
"Vaswani's transformer" → --query "au:vaswani AND ti:transformer"
"attention by Shaw" → --query "au:shaw AND ti:attention"
```

### 4. Date Range
```
"papers from 2024" → submittedDate:[202401010000 TO 202412312359]
"last half year" → submittedDate:[YYYYMMDD0000 TO CurrentDate2359]
"June to December 2023" → submittedDate:[202306010000 TO 202312312359]
```

### 5. Sorting
```
"latest" → --sort_by SubmittedDate --sort_order Descending
"most relevant" → --sort_by Relevance
```

### 6. Quantity Limit
```
"first 10" → --max_results 10
"top 5" → --max_results 5
```

## Args
- `--query` (str): Search query, supports field prefixes and boolean operators
- `--id_list` (str): Comma-separated arXiv IDs
- `--max_results` (int): Maximum number of downloads
- `--sort_by`: `Relevance` | `LastUpdatedDate` | `SubmittedDate`
- `--sort_order`: `Ascending` | `Descending`
- `--output_dir`: Output directory (default `./arxiv/`)

## Query Syntax Reference

### Field Prefixes
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

### Boolean Operators
- `AND` — Both terms must match
- `OR` — At least one term matches
- `ANDNOT` / `NOT` — Exclude matching terms
- `()` — Group expressions

### Date Filtering (submittedDate)
Format: `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]` (GMT time)

```
# Papers submitted in 2024
submittedDate:[202401010000 TO 202412312359]

# Papers from the last 30 days
submittedDate:[202403100000 TO 202404092359]

# Combine with other queries
ti:attention AND submittedDate:[202301010000 TO 202412312359]
```

### Examples
```
# Keyword search
--query "quantum machine learning"

# Title + author
--query "ti:transformer AND au:vaswani"

# Category + abstract
--query "cat:cs.LG AND abs:deep learning"

# Date range + title
--query "ti:attention AND submittedDate:[202301010000 TO 202412312359]"

# Exclude certain terms
--query "ti:learning ANDNOT (reinforcement OR unsupervised)"

# Exact phrase
--query 'ti:"self-attention"'
```

## Extraction Rules
1. **arXiv IDs** (highest priority): `"papers 1706.03762, 1810.04805"` → `--id_list "1706.03762,1810.04805"`
2. **Query**: `"quantum machine learning"` → `--query "quantum machine learning"`
3. **Author/title**: `"quantum by Shaw"` → `--query "ti:quantum AND au:shaw"`
4. **Sorting**: `"latest"` → `--sort_by SubmittedDate --sort_order Descending`; `"relevant"` → `--sort_by Relevance`
5. **Limit**: `"top 10"` → `--max_results 10`

## ⚠️ MANDATORY: User Confirmation Required Before Execution

**CRITICAL:** You MUST display the synthesized command to the user and explicitly wait for their confirmation (yes/是/同意 or no/否/取消) BEFORE executing `scripts/arxiv_retriever.py`.

**DO NOT** execute the script without user confirmation. This is a hard requirement.

### Confirmation Format
```
=== arXiv Search Command ===
python scripts/arxiv_retriever.py --query "au:He K AND submittedDate:[202504090000 TO 202604092359] ANDNOT abs:diffusion"

Extracted Parameters:
  - query: au:He K AND submittedDate:[202504090000 TO 202604092359] ANDNOT abs:diffusion

Execute this command? (yes/no)
```

### Required Steps
1. Display the full command that will be executed
2. List extracted parameters for user verification
3. Ask "Execute this command? (yes/no)" or equivalent
4. **WAIT** for explicit user confirmation
5. Only after user says "yes", "是", "同意", or similar affirmative response, execute the script

### What NOT to do
- ❌ Do NOT run the script immediately after synthesizing the command
- ❌ Do NOT assume implicit consent
- ❌ Do NOT skip the confirmation step even for simple queries
