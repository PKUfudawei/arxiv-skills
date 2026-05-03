#!/usr/bin/env python3
"""Download arXiv papers by query or ID list."""
import arxiv, argparse, os, requests
from tqdm import tqdm
import json


def parse_args():
    p = argparse.ArgumentParser(description="Download arXiv papers")
    p.add_argument("--query", default="", help="Search query")
    p.add_argument("--id_list", default="", help="Comma-separated arXiv IDs")
    p.add_argument("--max_results", type=int, help="Max papers to download")
    p.add_argument("--sort_by", default="SubmittedDate", choices=["Relevance", "LastUpdatedDate", "SubmittedDate"])
    p.add_argument("--sort_order", default="Descending", choices=["Ascending", "Descending"])
    p.add_argument("-o", "--output_dir", default=os.path.expanduser("."))
    p.add_argument("--page_size", type=int, default=100)
    p.add_argument("--delay_seconds", type=float, default=3.0)
    p.add_argument("--num_retries", type=int, default=3)
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
    with open(os.path.join(paper_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)


def download_pdf_by_url(paper_id, output_dir, filename):
    """Download PDF directly from arxiv URL."""
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    resp = requests.get(pdf_url, stream=True)
    resp.raise_for_status()
    with open(pdf_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded: {filename}")


def main():
    args = parse_args()
    id_list = args.id_list.split(",") if args.id_list else None

    if id_list:
        # ID list 模式：直接用 pdf_url 下载，不走 arxiv API
        for arxiv_id in tqdm(id_list, unit="papers"):
            arxiv_id = arxiv_id.strip()
            paper_dir = os.path.join(args.output_dir, arxiv_id)
            os.makedirs(paper_dir, exist_ok=True)
            pdf_filename = f"{arxiv_id}.pdf"
            download_pdf_by_url(arxiv_id, paper_dir, pdf_filename)
            # save_meta(paper, paper_dir)
            os.system(f"arxiv2bib {arxiv_id} > {os.path.join(paper_dir, arxiv_id)}.bib")
    else:
        # Query 模式：用 arxiv API
        search = arxiv.Search(
            query=args.query,
            max_results=args.max_results,
            sort_by=arxiv.SortCriterion[args.sort_by],
            sort_order=arxiv.SortOrder[args.sort_order],
        )
        client = arxiv.Client(page_size=args.page_size, delay_seconds=args.delay_seconds, num_retries=args.num_retries)

        for paper in tqdm(client.results(search), total=args.max_results, unit="papers"):
            arxiv_id = paper.get_short_id()
            paper_dir = os.path.join(args.output_dir, arxiv_id)
            os.makedirs(paper_dir, exist_ok=True)
            paper.download_pdf(dirpath=paper_dir, filename=f"{arxiv_id}.pdf")
            # save_meta(paper, paper_dir)
            os.system(f"arxiv2bib {arxiv_id} > {os.path.join(paper_dir, arxiv_id)}.bib")


    print(f"Downloaded to {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
