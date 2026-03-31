---
name: arxiv
description: Extract structured JSON from user prompt and download arXiv papers via script
license: Proprietary. LICENSE.txt has complete terms
---

# arxiv-download-skill

## Overview

This skill converts a user's natural language request into a structured JSON config that strictly follows:

`references/config_schema.json`

Then executes:
```
python scripts/arxiv_download.py --config '<JSON>'
```

---

## Step 1: JSON Extraction (LLM)

The LLM MUST output a JSON object that strictly conforms to the schema.

---

## Output Requirements (STRICT)

- Output MUST be valid JSON
- Output MUST match `config_schema.json`
- Output MUST be a single JSON object
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include comments
- Do NOT include trailing commas
- Do NOT wrap JSON in code blocks
- Do NOT include fields not defined in schema
- Do NOT fill default values unless explicitly requested

---

## Step 2: User Confirmation (MANDATORY)

After generating the JSON:

1. Display the extracted JSON to the user
2. Ask the user to confirm before proceeding

### Confirmation Rules

- Do NOT execute the script automatically
- Wait for explicit user confirmation (e.g., "yes", "confirm", "run")
- If user requests changes, update the JSON and repeat confirmation
- Only proceed when user clearly approves

---

## Core Fields

### Required

- `query` (string OR structured array)

---

## Query Construction (CRITICAL)

### Mode 1: Simple Query (DEFAULT)

Use a **string** when the query is simple

Example:

User: quantum machine learning papers  
Output:
{"query": "quantum machine learning"}

---

### Mode 2: Structured Query

Use **array format** when user specifies:

- author constraints
- field-specific search
- boolean logic (AND / OR / NOT)

Example:

User: quantum papers by Shaw  
Output:
{
  "query": [
    {"field": "title", "value": "quantum"},
    {"field": "author", "value": "shaw"}
  ]
}

---

### Field Enum (STRICT)

- title
- author
- abstract
- comment
- journal
- category
- report_number
- all

---

### Operator Rules

- Default = AND (omit if unnecessary)
- Use OR / NOT only if clearly implied

---

## IDs Handling (HIGH PRIORITY)

If user provides arXiv IDs:

- Use `ids`
- Prefer NOT to include `query`

Example:

User: download 1706.03762 and 1810.04805  
Output:
{"ids": "1706.03762,1810.04805"}

---

## Sorting

| User intent | sort_by | sort_order |
|------------|--------|------------|
| latest / recent | submitted_date | descending |
| updated | last_updated | descending |
| relevant | relevance | (omit) |

---

## max_results

Only include if explicitly specified

---

## Advanced: search vs top-level

- Prefer top-level fields
- Use `search` only if explicitly required

---

## Client / Performance Fields

Only include if user explicitly requests:

- page_size
- delay_seconds
- num_retries
- client

---

## Output Directory

Only include `output_dir` if specified

---

## Step 3: Script Execution

ONLY after user confirmation:
```
python scripts/arxiv_download.py --config '<JSON>'
```

## Step 4 (Optional): Generate BibTeX from arXiv IDs

Provide a list of arXiv IDs to automatically generate ref.bib.

Example:
```bash
arxiv2bib <ID1> <ID2> <ID3> > ref.bib
```

---

## Full Workflow

1. User prompt
2. LLM → JSON
3. Show JSON → user confirmation (Mandatory)
4. Execute script
5. Generate BibTex from given arXiv IDs (Optional)
---

## Notes

- This is semantic extraction, not rule-based parsing
- Always prioritize schema compliance
- Prefer minimal valid JSON
- Never skip confirmation step