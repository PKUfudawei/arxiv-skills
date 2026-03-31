# arxiv-skills

Two skills for working with academic papers:

1. **arxiv skill** - Search and download arXiv papers with meta data and BibTex
2. **OCR skill** - Convert PDF papers to markdown using PaddleOCR



## Quick start
```bash
git clone git@github.com:PKUfudawei/arxiv-skills.git

cp -r arxiv-skills/skills/* ~/.claude/skills
```
Then restart `claude` to load global skills

## 1. arxiv Skill

Automatically search and download papers from arXiv.

### Usage

**Using in Claude Code (conversational):**

Simply tell Claude what papers you need, and it will:
1. Understand your request and generate JSON config
2. Ask for your confirmation
3. Execute the download script

**Example prompts:**

```
Download 10 latest papers about quantum machine learning
Download papers 1706.03762 and 1810.04805
Find papers about quantum by author Shaw
```

### JSON Configuration Format

LLM outputs JSON matching this schema:

```json
{
  "query": "quantum machine learning",
  "max_results": 10,
  "sort_by": "SubmittedDate",
  "sort_order": "Descending",
  "page_size": 100
}
```

Or structured query:

```json
{
  "query": [
    {"field": "title", "value": "quantum"},
    {"field": "author", "value": "shaw"}
  ],
  "max_results": 5
}
```

Or specify IDs directly:

```json
{"ids": "1706.03762,1810.04805"}
```

### Field Descriptions

- `query` - Search keyword (simple string or structured array)
- `ids` - Direct arXiv IDs (mutually exclusive with query)
- `max_results` - Maximum number of results
- `sort_by` - `SubmittedDate` / `LastUpdatedDate` / `Relevance`
- `sort_order` - `Ascending` / `Descending`
- `page_size` / `delay_seconds` / `num_retries` - Performance parameters
- `output_dir` - Output directory

**Supported search fields:** title, author, abstract, comment, journal, category, report_number

### Output

Each paper is downloaded as a separate directory:
```
./arxiv/
  <arxiv_id>/
    pdf.pdf
    meta.json (contains title, authors, date, etc.)
```

### Optional Feature: Generate BibTeX

Provide ID list to quickly generate `.bib` file:

```bash
arxiv2bib <ID1> <ID2> <ID3> > ref.bib
```

---

## 2. OCR Skill

Convert PDF papers to Markdown using PaddleOCR.

### Environment Setup

1. **Get PaddleOCR API Token:**
   ```bash
   export PADDLE_TOKEN="your_token_here"
   ```

2. **Configure proxy (if needed):**
   ```bash
   source /home/olympus/fudawei/proxy-cern.sh
   ```

### Usage

**Basic usage:**

```bash
source /home/olympus/fudawei/proxy-cern.sh
python3 skills/ocr/scripts/paddleOCR.py -f "arxiv/*/*.pdf"
```

**Specify file path:**

```bash
python3 skills/ocr/scripts/paddleOCR.py -f /path/to/papers/*.pdf
```

### Features

- Concurrent processing of multiple PDFs (8 threads)
- OCR using PaddleOCR-VL-1.5 model for each page
- Stops extracting at "acknowledgement" / "acknowledgment" / "references" sections
- Outputs `.pdf` → `.md` files

### Supported Files

- PDF format academic papers
- Requires accessible PaddleOCR service

### Output

```
input.pdf
→ output.md (markdown format paper content)
```

---

## Loading into Claude Code

### Direct Conversation

No additional configuration needed. Simply tell Claude in conversation:

```
Help me download 5 papers about Transformer from arXiv
```

Claude will automatically understand and call the Python scripts.



## Acknowledgements
Great thanks to the below projects:
- [anthropics/skills](https://github.com/anthropics/skills)
- [arXiv API User's manual](https://info.arxiv.org/help/api/index.html)
- [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py)
- [nathangrigg/arxiv2bib](https://github.com/nathangrigg/arxiv2bib)
- [PaddlePaddle/PaddleOCR](https://github.com/PADDLEPADDLE/PADDLEOCR)
