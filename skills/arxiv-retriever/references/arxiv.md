# arxiv Python Module - Comprehensive Reference

This document provides a comprehensive overview of the Python `arxiv` module, its API, and usage patterns, culminating from `arxiv.py` (wrapper API), `arxiv/__init__.py`, and the original arXiv API documentation.

The `arxiv` Python module is a wrapper for [the arXiv API](https://arxiv.org/help/api/index). [arXiv](https://arxiv.org/) provides open access to 1,000,000+ articles in Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, and Statistics.

---

## Installation

```bash
pip install arxiv  # or `uv add arxiv`
```

## Usage

```python
import arxiv
```

---

## Core API

### Client

A `Client` specifies a reusable strategy for fetching results from arXiv's API. It encapsulates pagination and retry logic. *Reusing* a client allows successive API calls to use the same connection pool and ensures they abide by the rate limit you set.

**Configuration parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page_size` | 100 | Maximum number of results fetched in a single API request. API limit: 2000 per page. |
| `delay_seconds` | 3.0 | Seconds to wait between API requests. arXiv recommends "no more than one request every three seconds." |
| `num_retries` | 3 | Number of times to retry a failing API request before raising an Exception. |

**Example:**

```python
# Use default client
client = arxiv.Client()

# Custom client with larger page size
big_client = arxiv.Client(
    page_size=1000,
    delay_seconds=10.0,
    num_retries=5
)
```

### Search

A `Search` specifies a search of arXiv's database. Use `Client.results` to get a generator yielding `Result`s.

**Configuration parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `query` | "" | Unencoded query string. See [arXiv API User Manual: Query Details](https://arxiv.org/help/api/user-manual#query_details). |
| `id_list` | [] | List of arXiv article IDs to limit the search. |
| `max_results` | None | Maximum number of results to return. API limit: 300,000 results per query. Set to `None` to fetch all. |
| `sort_by` | `SortCriterion.Relevance` | Sort criterion: `Relevance`, `LastUpdatedDate`, or `SubmittedDate`. |
| `sort_order` | `SortOrder.Descending` | Sort order: `Ascending` or `Descending`. |

**Example:**

```python
# Keyword search with sorting
search = arxiv.Search(
    query="quantum",
    max_results=10,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

# Advanced query syntax
search = arxiv.Search(
    query="au:del_maestro AND ti:checkerboard"
)

# Search by ID
search = arxiv.Search(id_list=["1605.08386v1"])
```

### Results

The `results()` method returns a generator that yields `Result` objects one at a time, until `max_results` have been yielded or there are no more results.

```python
# Using generator (memory efficient)
for result in client.results(search):
    print(result.title)

# Or exhaust into a list (warning: slow for large result sets)
all_results = list(client.results(search))
```

---

## Result Type

`Result` objects include metadata about each paper and helper methods for downloading their content.

**Result attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `entry_id` | str | URL of the form `https://arxiv.org/abs/{id}` |
| `updated` | datetime | When the result was last updated |
| `published` | datetime | When the result was originally published |
| `title` | str | The paper title |
| `authors` | `list[Author]` | List of author objects |
| `summary` | str | The paper abstract |
| `comment` | str\|None | Authors' comment if present |
| `journal_ref` | str\|None | Journal reference if present |
| `doi` | str\|None | Resolved DOI URL if present |
| `primary_category` | str | Primary arXiv category |
| `categories` | `list[str]` | All arXiv categories |
| `links` | `list[Link]` | Up to three associated URLs |
| `pdf_url` | str\|None | PDF URL if present |
| `source_url` | str\|None | Source tarfile URL |

**Helper methods:**

- `Result.download_pdf(dirpath="./", filename="") -> str` — Downloads PDF to specified directory (deprecated: use `result.pdf_url` directly)
- `Result.download_source(dirpath="./", filename="") -> str` — Downloads source tarfile (deprecated: use `result.source_url` directly)
- `Result.get_short_id() -> str` — Returns short ID (e.g., `2107.05580v1`)
- `Result.source_url() -> str\|None` — Derives the source tarfile URL

**Example:**

```python
author_names = [author.name for author in result.authors]
print(f"Title: {result.title}")
print(f"Authors: {', '.join(author_names)}")
print(f"Published: {result.published}")
print(f"PDF URL: {result.pdf_url}")

# Download PDF and source
pdf_path = result.download_pdf(dirpath="./papers", filename="quantum_paper.pdf")
```

---

## API Reference

```python
imports
    import arxiv
    import logging  # Optional: for debugging

consts
    arxiv.SortCriterion.Relevance
    arxiv.SortCriterion.LastUpdatedDate
    arxiv.SortCriterion.SubmittedDate
    arxiv.SortOrder.Ascending
    arxiv.SortOrder.Descending
```

### Client API

```python
class Client
    ### Constructor
    def __init__(page_size: int = 100, delay_seconds: float = 3.0, num_retries: int = 3)

    ### Results
    def results(search: Search, offset: int = 0) -> Iterator[Result]
        Uses this client configuration to fetch results. If all tries fail, raises an error.
        Setting a nonzero `offset` discards leading records in the result set.

    ### Helpers
    def __str__() -> str
    def __repr__() -> str
```

### Search API

```python
class Search
    ### Constructor
    def __init__(
        query: str = "",
        id_list: list[str] | None = None,
        max_results: int | None = None,
        sort_by: SortCriterion = SortCriterion.Relevance,
        sort_order: SortOrder = SortOrder.Descending
    )

    ### URL args
    def _url_args(self) -> dict[str, str]

    ### Results (deprecated, use Client.results)
    def results(self, offset: int = 0) -> Iterator[Result]

    ### Helpers
    def __str__() -> str
    def __repr__() -> str
```

### Result API

```python
class Result
    ### Constructors
    @classmethod
    def _from_feed_entry(entry: feedparser.FeedParserDict) -> Result

    ### Download helpers (deprecated: use PDF URL directly)
    def download_pdf(self, dirpath="./", filename="") -> str
    def download_source(self, dirpath="./", filename="") -> str

    ### Helpers
    def get_short_id(self) -> str
    def source_url(self) -> str | None
    def _get_default_filename(self, extension: str = "pdf") -> str

    ### Nested types
    class Author
        name: str
        def _from_feed_author(feed_author: feedparser.FeedParserDict) -> Author

    class Link
        href: str
        title: str | None
        rel: str
        content_type: str | None
        def _from_feed_link(feed_link: feedparser.FeedParserDict) -> Link

    class MissingFieldError(Exception)

    ### Helpers
    def __str__() -> str
    def __repr__() -> str
    def __eq__(self, other: object) -> bool
```

---

## Complete Examples

### Basic Search

```python
import arxiv

client = arxiv.Client()
search = arxiv.Search(
    query="quantum",
    max_results=10,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

for result in client.results(search):
    print(f"{result.title} by {', '.join(a.name for a in result.authors)}")
```

### Search by Paper ID

```python
import arxiv

client = arxiv.Client()
search = arxiv.Search(id_list=["1605.08386v1"])
result = next(client.results(search))
print(result)
print(result.title)
print(result.summary[:200])  # First 200 chars of abstract
```

### Download PDF

```python
import arxiv
import os

client = arxiv.Client()
search = arxiv.Search(query="attention mechanism", max_results=3)

os.makedirs("./papers", exist_ok=True)

for result in client.results(search):
    pdf_path = result.download_pdf(dirpath="./papers")
    print(f"Downloaded: {pdf_path}")
    print(f"PDF URL: {result.pdf_url}")
```

### Pagination

```python
import arxiv

client = arxiv.Client()
search = arxiv.Search(
    query="transformer",
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

# Skip first 90 results, fetch next 10
 results = list(client.results(search, offset=90))
```

### Custom Client Configuration

```python
import arxiv

# Faster requests, higher delay (respect rate limits for slow connections)
fast_client = arxiv.Client(
    page_size=200,  # Max per page
    delay_seconds=5.0,  # Longer delay
    num_retries=3
)

search = arxiv.Search(query="deep learning", max_results=50)

for result in fast_client.results(search):
    print(result.title)
```

---

## Debugging

To inspect the package's network behavior and API logic:

```python
import logging
import arxiv

logging.basicConfig(level=logging.DEBUG)
client = arxiv.Client()
paper = next(client.results(arxiv.Search(id_list=["1605.08386v1"])))
```

Sample output:

```
INFO:arxiv.arxiv:Requesting 100 results at offset 0
INFO:arxiv.arxiv:Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?...
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): export.arxiv.org:443
DEBUG:urllib3.connectionpool:https://export.arxiv.org:443 "GET /api/query?... HTTP/1.1" 200 979
```

---

## Query Syntax

See [arXiv API User Manual: Query Details](https://arxiv.org/help/api/user-manual#query_details) for advanced search syntax.

### Field Search Prefixes

Prefix terms with field codes to search specific article fields:

| Prefix | Field | Description |
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

Example:
```python
search = arxiv.Search(query="au:del_maestro AND ti:checkerboard")
```

### Boolean Operators

Combine field searches with Boolean operators (case-insensitive):

| Operator | Description |
|----------|-------------|
| `AND` | Both terms must match |
| `OR` | At least one term matches |
| `ANDNOT` or `NOT` | Exclude matching terms |
| `()` | Group expressions |

Example:
```python
# Use AND to combine searches
search = arxiv.Search(query="au:del_maestro AND ti:checkerboard")

# Use ANDNOT to exclude
search = arxiv.Search(query="au:del_maestro ANDNOT ti:checkerboard")

# Use parentheses for grouping
search = arxiv.Search(query="au:del_maestro ANDNOT (ti:checkerboard OR ti:pyrochlore)")

# Use OR for alternatives
search = arxiv.Search(query="(transformer OR self-attention) AND decoder")
```

### Phrase and Grouping

- **Phrase search**: Use double quotes (`"..."`) for exact phrases. URL encoding: `%22`
  ```python
  search = arxiv.Search(query='ti:"quantum criticality"')
  ```

- **Grouping**: Use parentheses to control operator precedence. URL encoding: `(%28)` and `)%29`
  ```python
  search = arxiv.search(query="au:del_maestro ANDNOT (ti:checkerboard OR ti:Pyrochlore)")
  ```

- **Spaces**: Use `+` in URLs (encodes as space) or just spaces in Python strings

### Date Filtering

Use `submittedDate` filter with format `[YYYYMMDDTTTT+TO+YYYYMMDDTTTT]` (GMT time):

```python
search = arxiv.Search(
    query="au:del_maestro AND submittedDate:[202301010600 TO 202401010600]"
)
```

### Search Query vs ID List Logic

- `search_query` only → return articles matching the query
- `id_list` only → return articles in the ID list
- Both provided → filter `id_list` by `search_query`

```python
# Search by ID list (latest versions)
search = arxiv.Search(id_list=["1605.08386"])

# Search by specific version
search = arxiv.Search(id_list=["1605.08386v1"])

# Filter ID list by query
search = arxiv.Search(
    query="quantum",
    id_list=["1605.08386", "2107.05580"]
)
```

### URL Encoding

| Character | Encoding | Purpose |
|-----------|----------|---------|
| `(` | `%28` | Left parenthesis |
| `)` | `%29` | Right parenthesis |
| `"` | `%22` | Double quotes |
| ` ` (space) | `+` | Field separator / multiple terms |

### Complex Examples

1. **Multiple authors:**
```python
search = arxiv.Search(query='au:shaw AND au:power')
```

2. **Category + field combination:**
```python
search = arxiv.Search(query="cat:cs.LG AND abs:deep learning")
```

3. **Date range + title search:**
```python
search = arxiv.Search(
    query='ti:attention AND submittedDate:[201706010000 TO 201812312359]',
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)
```

4. **Phrase with exclusions:**
```python
search = arxiv.Search(
    query='ti:"self-attention" ANDNOT (implies OR redundant)'
)
```

### Notes

- `all:` (empty prefix) searches all fields simultaneously
- Boolean operators have lower precedence than field limits
- Use parentheses to override precedence
- Query is case-insensitive and whitespace-insensitive
- No `id:` field prefix — use `id_list` parameter instead
- Up to 3 links per article
- API returns Atom feed format by default

---

## Error Handling

```python
import arxiv
from arxiv import UnexpectedEmptyPageError, HTTPError

client = arxiv.Client(num_retries=3)
search = arxiv.Search(query="test", max_results=10)

try:
    for result in client.results(search):
        print(result.title)
except HTTPError as e:
    print(f"HTTP error: {e.status} at {e.url}")
except UnexpectedEmptyPageError as e:
    print(f"Empty page encountered: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Performance Tips

1. **Reuse the client**: Create one `Client` instance and reuse it for multiple searches to benefit from connection pooling.
2. **Set appropriate `max_results`**: Be mindful that iterating through results is slow for large result sets. The API limit is 300,000 results per query.
3. **Use generators**: `Client.results()` returns a generator; iterate directly rather than exhaust into a list for memory efficiency.
4. **Use `pdf_url` directly**: Instead of `result.download_pdf()`, use `result.pdf_url` to download PDFs with your preferred tool.

---

## References

- [arXiv API documentation](https://arxiv.org/help/api/index)
- [arXiv API User Manual](https://arxiv.org/help/api/user-manual)
- [arXiv category taxonomy](https://arxiv.org/category_taxonomy)
- [arXiv API Terms of Use](https://arxiv.org/help/api/tou)
- PyPI package: https://pypi.org/project/arxiv/
- GitHub repo: https://github.com/lukasschwab/arxiv.py
- `arxivql`: https://pypi.org/project/arxivql/ (may simplify constructing complex query strings)

---

## License

This document references the `arxiv` Python package and the arXiv API for open access research papers.
