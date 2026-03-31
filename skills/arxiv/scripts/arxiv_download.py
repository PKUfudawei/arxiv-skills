#!/usr/bin/env python3
import arxiv
import argparse
import os
from tqdm import tqdm
import json

FIELD_PREFIXES = ['ti', 'au', 'abs', 'co', 'jr', 'cat', 'rn']

FIELD_MAP = {
    'title': 'ti',
    'author': 'au',
    'abstract': 'abs',
    'comment': 'co',
    'journal': 'jr',
    'category': 'cat',
    'report_number': 'rn',
    'all': '',
}

def parse_args():
    parser = argparse.ArgumentParser(description="Download arXiv papers")

    parser.add_argument("-o", "--output_dir", type=str, default="./arxiv/",
                        help="Directory to download papers to")

    parser.add_argument("--page_size", type=int, default=100,
                        help="Number of results per API request (1-2000)")
    parser.add_argument("--delay_seconds", type=float, default=3.0,
                        help="Delay between requests in seconds")
    parser.add_argument("--num_retries", type=int, default=3,
                        help="Number of retry attempts per request")

    parser.add_argument("--max_results", type=int, default=None,
                        help="Maximum number of results (1-300000, None for all)")
    parser.add_argument("--id_list", type=str, default="",
                        help="Comma-separated arXiv IDs to filter (optional)")
    parser.add_argument("--sort_by", type=str, default="SubmittedDate",
                        choices=["Relevance", "LastUpdatedDate", "SubmittedDate"],
                        help="Sort criterion")
    parser.add_argument("--sort_order", type=str, default="Descending",
                        choices=["Ascending", "Descending"],
                        help="Sort order")

    for flag in FIELD_PREFIXES:
        parser.add_argument("--" + flag, type=str, default="",
                            help=f'Search in {flag} field')

    parser.add_argument("--config", type=str, default="",
                            help='JSON string with search settings')

    return parser.parse_args()


def build_query_from_config(config):
    """Build query from config dictionary."""
    if not config or 'query' not in config or not config['query']:
        return None
    query_terms = config['query']
    if isinstance(query_terms, list) and len(query_terms) > 0:
        return _build_query_from_terms(query_terms)
    return query_terms


def _build_query_from_terms(terms):
    """
    Convert structured query terms to arXivQL.
    terms: [{"field": "title", "value": "quantum"}]
    """
    query_parts = []
    for term in terms:
        field = term.get('field', 'all')
        value = term.get('value', '')
        prefix = FIELD_MAP.get(field, 'ti')
        if prefix:
            term_str = f'{prefix}:{value}'
        query_parts.append(term_str)

    query = ' AND '.join(query_parts) if query_parts else None
    return query


def build_query_from_args(args):
    """Build query from command-line arguments."""
    query_parts = []
    for flag in FIELD_PREFIXES:
        value = getattr(args, flag, None)
        if value:
            query_parts.append(f"{flag}:{value}")
    query = ' '.join(query_parts) if query_parts else ''
    return query


def save_result_metadata(result, paper_dir):
    """Save paper metadata to meta.json."""
    meta = {
        "id": result.get_short_id(),
        "title": result.title,
        "authors": list(result.authors),
        "published": result.published,
        "updated": result.updated,
        "summary": result.summary,
        "comment": result.comment,
        "journal_ref": result.journal_ref,
        "doi": result.doi,
        "primary_category": result.primary_category,
        "categories": result.categories,
        "links": list(result.links),
        "pdf_url": result.pdf_url,
        "source_url": result.source_url(),
    }
    with open(os.path.join(paper_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)


def main():
    args = parse_args()

    config_str = getattr(args, 'config', '')
    try:
        config = json.loads(config_str)
        query = build_query_from_config(config)
        for key, value in config.items():
            if key != 'query' and hasattr(args, key):
                setattr(args, key, value)
    except json.JSONDecodeError:
        config = None
        query = build_query_from_args(args)


    print(query)
    search_kwargs = {"query": query}
    if args.max_results:
        search_kwargs["max_results"] = args.max_results
    if args.id_list:
        search_kwargs["id_list"] = args.id_list.split(',')
    search_kwargs["sort_by"] = arxiv.SortCriterion[args.sort_by]
    search_kwargs["sort_order"] = arxiv.SortOrder[args.sort_order]
    search = arxiv.Search(**search_kwargs)

    client = arxiv.Client(
        page_size=args.page_size,
        delay_seconds=args.delay_seconds,
        num_retries=args.num_retries
    )

    id_filter = None
    if hasattr(args, 'ids') and args.ids:
        id_filter = [aid.strip() for aid in args.ids.split(',') if aid.strip()]

    for idx, paper in tqdm(enumerate(client.results(search)), total=args.max_results, unit=' papers', desc="Downloaded"):
        arxiv_id = paper.get_short_id()
        if id_filter is not None and arxiv_id not in id_filter:
            continue

        paper_dir = os.path.join(args.output_dir, arxiv_id)
        os.makedirs(paper_dir, exist_ok=True)
        paper.download_pdf(dirpath=paper_dir, filename=f"{arxiv_id}.pdf")
        save_result_metadata(paper, paper_dir)

    print(f"Downloaded papers to {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
