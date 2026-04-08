---
name: pdf-parser
description: Convert PDF papers to markdown using PaddleOCR API
license: Proprietary. LICENSE has complete terms
---

# pdf-parser

Convert PDF papers to markdown format using PaddleOCR-VL-1.5 API, with automatic image extraction and layout preservation.

## Overview

This skill uses PaddleOCR's cloud API to convert PDF academic papers into markdown format. It preserves document structure, extracts text content, and downloads embedded images.

## Workflow

```
PDF Files → PaddleOCR API → JSONL Result → Markdown + Images
```

### Processing Steps

1. **Submit Job**: Upload each PDF to PaddleOCR API
2. **Wait for Result**: Poll job status until completion
3. **Download & Merge**: Fetch JSONL result, extract markdown text and images
4. **Save Output**: Write combined markdown file with embedded image references

## Setup

### 1. Obtain PaddleOCR API Token

Get your API token from [PaddleOCR AI Studio](https://aistudio.baidu.com/) and set the environment variable:

```bash
export PADDLE_TOKEN="your_token_here"
```

Or add to `~/.bashrc` or `.env` file for persistent configuration:

```bash
echo 'export PADDLE_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Basic Usage

```bash
python3 skills/pdf-parser/scripts/paddleOCR.py -f "path/to/pdfs/*.pdf"
```

### Process Multiple Directories

```bash
# Process all PDFs in arxiv subdirectories
python3 skills/pdf-parser/scripts/paddleOCR.py -f "arxiv/*/*.pdf"

# Process specific directory
python3 skills/pdf-parser/scripts/paddleOCR.py -f "/home/user/papers/*.pdf"
```

## Args

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--files` | `-f` | `../data/arxiv/*/*.pdf` | Glob pattern for PDF files to process |

## Output Format

### File Naming
- Input: `paper_123.pdf`
- Output: `paper_123.md` (same directory as input)

### Markdown Structure
- Text content extracted and preserved in reading order
- Images saved as separate files with references in markdown
- Layout structure maintained (headers, paragraphs, lists)

### Image Handling
- Images extracted from PDF are downloaded separately
- Saved in the same directory as the markdown file
- Referenced in markdown using standard image syntax

## Configuration

### API Settings (Hardcoded)

| Setting | Value | Description |
|---------|-------|-------------|
| `MODEL` | `PaddleOCR-VL-1.5` | OCR model version |
| `useDocOrientationClassify` | `False` | Disable auto-orientation |
| `useDocUnwarping` | `False` | Disable document unwarping |
| `useChartRecognition` | `False` | Disable chart recognition |

### Concurrency Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_workers` | `16` | Maximum parallel PDF processing threads |
| `semaphore` | `5` | Maximum concurrent API requests |
| `sleep_interval` | `1s` | Delay between job submissions |

## Example

### Convert Single Directory

```bash
# Convert all PDFs in the papers directory
python3 skills/pdf-parser/scripts/paddleOCR.py -f "./papers/*.pdf"

# Output:
# ./papers/paper1.pdf → ./papers/paper1.md
# ./papers/paper2.pdf → ./papers/paper2.md
```

### Convert arXiv Download Directory

```bash
# Typical workflow after arxiv-retriever download
python3 skills/pdf-parser/scripts/paddleOCR.py -f "arxiv/*/*.pdf"

# Output:
# arxiv/cs.LG/paper_123.pdf → arxiv/cs.LG/paper_123.md
```

## Error Handling

- **Skipped Files**: PDFs that already have a corresponding `.md` file are skipped
- **Failed Jobs**: Errors are logged to console with `tqdm.write()`
- **Network Errors**: Request failures are caught and logged per-file

## Performance

- **Parallel Processing**: Up to 16 PDFs processed concurrently
- **Rate Limiting**: Max 5 simultaneous API requests to avoid throttling
- **Progress Tracking**: Real-time progress bar using `tqdm`

## Dependencies

- `fitz` (PyMuPDF) - PDF handling
- `requests` - HTTP API calls
- `tqdm` - Progress bars
- `python-dotenv` - Environment variable loading

## Notes

- Requires internet connection for API calls
- API usage may be subject to quotas or billing
- Large PDFs may take longer to process
- Image files are downloaded separately and saved alongside markdown
