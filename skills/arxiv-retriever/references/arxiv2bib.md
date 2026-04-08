# arxiv2bib Command Line Tool - Reference

This document provides a comprehensive reference for the `arxiv2bib` command-line tool, which generates BibTeX entries from arXiv paper metadata.

---

## Installation

```bash
# Via pip (recommended)
pip install arxiv2bib
```

**Standalone usage** (without installation): Copy `arxiv2bib.py` to a directory in your PATH.

---

## Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `arxiv2bib <ID> > <ID>.bib` | Get BibTeX for a single paper and save to `<ID>.bib` |
| `arxiv2bib <ID>` | Get BibTeX for a single paper by ID |
| `arxiv2bib <ID1> <ID2> ...` | Get BibTeX for multiple papers |
| `arxiv2bib < papers.txt` | Read paper IDs from stdin (one per line) |
| `arxiv2bib --help` | Show usage information |

# Specific version
$ arxiv2bib 1102.0001v2

# Multiple papers
$ arxiv2bib 1101.0001 1102.0002 1103.0003

# From file (one ID per line)
$ arxiv2bib < papers.txt
```

---

## Output Format

The tool outputs BibTeX entries in standard format:

```bibtex
@Article{
    author = "{Author Names}",
    title = "{Title of the Paper}",
    journal = "arXiv preprint arXiv:yyyy.mm.mm",
    year = "yyyy",
    month = "mmm",
    pages = "{pages if available}"
}
```

**Field details:**

| Field | Description | Format |
|-------|-------------|--------|
| `author` | Author names | Lastname, Firstname |
| `title` | Paper title | Capitalized per BibTeX style |
| `journal` | Source | "arXiv preprint arXiv:..." |
| `year` | Publication year | 4-digit year |
| `month` | Publication month | Full month name |
| `pages` | Page numbers | Optional, if available |

---

## Integration with arxiv Skill

The `arxiv2bib` tool can be used in conjunction with the `arxiv` Python package workflow:

1. Use `arxiv` skill to search and discover papers
2. Extract paper IDs from search results
3. Generate BibTeX entries using `arxiv2bib`

---

## References

- Repository: https://github.com/nthgrigg/arxiv2bib
- Homepage: http://nathangrigg.github.io/arxiv2bib
- PyPI: https://pypi.org/project/arxiv2bib/
- arXiv API: https://arxiv.org/help/api/index

---

## Notes

- Requires network access to arXiv.org
- Output follows BibLaTeX-compatible format
- Author names are output with curly braces for grouping
