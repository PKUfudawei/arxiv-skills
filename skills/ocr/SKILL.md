---
name: ocr
description: OCR PDF files to markdown files via paddleOCR API
license: Proprietary. LICENSE.txt has complete terms
---

# OCR Skill

Convert PDF papers to markdown using PaddleOCR.

---

## Overview

Extracts text from PDF files and converts them to markdown format. Stops at acknowledgement/acknowledgment/references sections.

---

## Usage

### Setup

Set the PaddleOCR API token:

```bash
export PADDLE_TOKEN="your_token_here"
```

### Run OCR

```bash
source /home/olympus/fudawei/proxy-cern.sh
python3 skills/ocr/scripts/paddleOCR.py -f "arxiv/*/*.pdf"
```

This will:
- Process all PDFs matching the pattern
- Convert each PDF to markdown (`filename.pdf` → `filename.md`)
- Stop extracting text at "acknowledgement", "acknowledgment", or "references" sections

---

## Example

```bash
python3 skills/ocr/scripts/paddleOCR.py -f /home/user/papers/*.pdf
```
