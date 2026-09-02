#!/usr/bin/env python3
"""Download arXiv papers by query or ID list.

Query mode uses the arXiv API and saves each paper's PDF, metadata (meta.json)
and BibTeX.  ID-list mode downloads PDFs directly from arxiv.org (no API
quota) and then best-effort fetches metadata/BibTeX.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

try:
    import arxiv
    import requests
    from tqdm import tqdm
except ImportError:
    # Allow `--help` to work before dependencies are installed; main() reports
    # a clear install hint when a required dependency is actually missing.
    arxiv = None
    requests = None
    tqdm = None

DEP_INSTALL_HINT = "pip3 install arxiv arxiv2bib requests tqdm"

USER_AGENT = (
    "arxiv-retriever-skill/1.0 "
    "(https://github.com/PKUfudawei/arxiv-skills; skill for reading arXiv papers)"
)
ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


def parse_args():
    p = argparse.ArgumentParser(description="Download arXiv papers")
    p.add_argument("--query", default="", help="Search query")
    p.add_argument("--id_list", default="", help="Comma-separated arXiv IDs")
    p.add_argument("--max_results", type=int, default=None, help="Max papers to download (default: 10 in query mode)")
    p.add_argument("--sort_by", default="SubmittedDate", choices=["Relevance", "LastUpdatedDate", "SubmittedDate"])
    p.add_argument("--sort_order", default="Descending", choices=["Ascending", "Descending"])
    p.add_argument("-o", "--output_dir", default=os.path.expanduser("."), help="Output directory (default: current directory)")
    p.add_argument("--page_size", type=int, default=100)
    p.add_argument("--delay_seconds", type=float, default=3.0)
    p.add_argument("--num_retries", type=int, default=3)
    p.add_argument("--force", action="store_true", help="Re-download and overwrite existing files")
    return p.parse_args()


def save_meta(paper, paper_dir):
    meta = {
        "id": paper.get_short_id(),
        "title": paper.title,
        "authors": list(paper.authors),
        "published": paper.published,
        "updated": paper.updated,
        "summary": paper.summary,
        "comment": paper.comment,
        "journal_ref": paper.journal_ref,
        "doi": paper.doi,
        "primary_category": paper.primary_category,
        "categories": paper.categories,
        "links": list(paper.links),
        "pdf_url": paper.pdf_url,
        "source_url": paper.source_url(),
    }
    with open(os.path.join(paper_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)


def bibtex_for_id(arxiv_id):
    """Best-effort BibTeX via the `arxiv2bib` CLI.

    Returns the BibTeX text, or None if arxiv2bib is not installed / fails.
    The caller decides whether a missing entry is an error.
    """
    exe = shutil.which("arxiv2bib")
    if not exe:
        return None
    proc = subprocess.run([exe, arxiv_id], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout


def download_pdf_by_url(session, paper_id, output_dir, filename):
    """Download PDF directly from the arXiv PDF URL."""
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    resp = session.get(pdf_url, stream=True, timeout=120)
    resp.raise_for_status()
    with open(pdf_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return pdf_path


def new_http_session():
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def base_id(arxiv_id):
    """Strip a trailing version suffix (e.g. 1706.03762v1 -> 1706.03762)."""
    return re.sub(r"v\d+$", "", arxiv_id)


def handle_id_list(ids, args, client):
    """ID-list mode: direct PDF download, then best-effort meta + BibTeX."""
    session = new_http_session()

    # One lightweight API call to fetch metadata for all IDs (best effort).
    papers_by_id = {}
    try:
        search = arxiv.Search(id_list=[base_id(i) for i in ids])
        for paper in client.results(search):
            papers_by_id[paper.get_short_id()] = paper
    except Exception as exc:  # noqa: BLE001 - API quota / network should not abort downloads
        tqdm.write(f"[WARN] Could not fetch metadata from the arXiv API: {exc}")

    ok = skipped = failed = 0
    for arxiv_id in tqdm(ids, unit="papers"):
        paper_dir = os.path.join(args.output_dir, arxiv_id)
        os.makedirs(paper_dir, exist_ok=True)
        pdf_path = os.path.join(paper_dir, f"{arxiv_id}.pdf")

        if os.path.exists(pdf_path) and not args.force:
            skipped += 1
            tqdm.write(f"[SKIP] {pdf_path} already exists (use --force to re-download)")
            continue

        try:
            download_pdf_by_url(session, arxiv_id, paper_dir, f"{arxiv_id}.pdf")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            tqdm.write(f"[ERROR] Failed to download {arxiv_id}: {exc}")
            continue

        # Metadata + BibTeX are best effort; failures are warned, not fatal.
        paper = papers_by_id.get(base_id(arxiv_id))
        if paper is not None:
            save_meta(paper, paper_dir)
        bibtex = bibtex_for_id(arxiv_id)
        if bibtex:
            with open(os.path.join(paper_dir, f"{arxiv_id}.bib"), "w", encoding="utf-8") as f:
                f.write(bibtex)
        elif paper is None:
            tqdm.write(f"[WARN] No meta.json / .bib for {arxiv_id}: arXiv API and arxiv2bib both unavailable")

    return ok, skipped, failed


def handle_query(query, args, client):
    """Query mode: arXiv API search, then PDF + meta.json + BibTeX per hit."""
    max_results = args.max_results or 10
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion[args.sort_by],
        sort_order=arxiv.SortOrder[args.sort_order],
    )

    ok = skipped = failed = 0
    for paper in tqdm(client.results(search), total=max_results, unit="papers"):
        arxiv_id = paper.get_short_id()
        paper_dir = os.path.join(args.output_dir, arxiv_id)
        os.makedirs(paper_dir, exist_ok=True)
        pdf_path = os.path.join(paper_dir, f"{arxiv_id}.pdf")

        if os.path.exists(pdf_path) and not args.force:
            skipped += 1
            tqdm.write(f"[SKIP] {pdf_path} already exists (use --force to re-download)")
        else:
            try:
                paper.download_pdf(dirpath=paper_dir, filename=f"{arxiv_id}.pdf")
                ok += 1
            except Exception as exc:  # noqa: BLE001
                failed += 1
                tqdm.write(f"[ERROR] Failed to download {arxiv_id}: {exc}")

        save_meta(paper, paper_dir)
        bibtex = bibtex_for_id(arxiv_id)
        if bibtex:
            with open(os.path.join(paper_dir, f"{arxiv_id}.bib"), "w", encoding="utf-8") as f:
                f.write(bibtex)
        else:
            tqdm.write(f"[WARN] arxiv2bib not installed or failed for {arxiv_id}; no .bib file")

    return ok, skipped, failed


def main():
    args = parse_args()

    if arxiv is None or requests is None or tqdm is None:
        sys.exit(f"Missing required dependency. Install with: {DEP_INSTALL_HINT}")

    ids = [i.strip() for i in args.id_list.split(",") if i.strip()] if args.id_list else None
    if not ids and not args.query:
        sys.exit("Provide either --query or --id_list.")

    if ids:
        for arxiv_id in ids:
            if not ARXIV_ID_RE.match(arxiv_id):
                sys.exit(f"Invalid arXiv ID: {arxiv_id}")

    client = arxiv.Client(page_size=args.page_size, delay_seconds=args.delay_seconds, num_retries=args.num_retries)

    if ids:
        ok, skipped, failed = handle_id_list(ids, args, client)
    else:
        ok, skipped, failed = handle_query(args.query, args, client)

    print(f"\nDownloaded to {os.path.abspath(args.output_dir)}")
    print(f"Summary: {ok} downloaded, {skipped} skipped, {failed} failed")
    if ok and not shutil.which("arxiv2bib"):
        print(f"Note: arxiv2bib is not installed, so .bib files were not written ({DEP_INSTALL_HINT})")


if __name__ == "__main__":
    main()
