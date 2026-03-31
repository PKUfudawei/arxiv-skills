#!/usr/bin/env python3
"""
OCR script to convert PDF papers to markdown using PaddleOCR
"""

import fitz
import json
import os
import requests
import argparse
import threading
from glob import glob

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
MODEL = "PaddleOCR-VL-1.5"

headers = {"Authorization": f"bearer {os.environ['PADDLE_TOKEN']}"}

optional_payload = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}

semaphore = threading.Semaphore(5)


def parse_args():
    parser = argparse.ArgumentParser(description="OCR PDFs to markdowns")
    parser.add_argument("-f", "--files", type=str, default="arxiv/*/*.pdf")
    return parser.parse_args()


def submit_job(file_path):
    data = {"model": MODEL, "optionalPayload": json.dumps(optional_payload)}
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(JOB_URL, headers=headers, data=data, files=files)
    resp.raise_for_status()
    return resp.json()["data"]["jobId"]


def wait_for_result(job_id):
    while True:
        r = requests.get(f"{JOB_URL}/{job_id}", headers=headers)
        r.raise_for_status()
        data = r.json()["data"]
        state = data["state"]

        if state == "done":
            return data["resultUrl"]["jsonUrl"]
        elif state == "failed":
            return None


def download_and_merge(jsonl_url, final_md):
    resp = requests.get(jsonl_url)
    resp.raise_for_status()

    lines = resp.text.strip().split("\n")
    all_md = []
    stop = False

    for line in lines:
        if not line.strip():
            continue
        result = json.loads(line)["result"]
        for res in result["layoutParsingResults"]:
            if stop:
                continue
            md_text = res["markdown"]["text"]
            lower = md_text.lower()
            keywords = ['acknowledgement', 'acknowledgment', 'references']
            indices = [lower.find(kw) for kw in keywords]
            valid_indices = [idx for idx in indices if idx != -1]
            if valid_indices:
                cut_index = min(valid_indices)
                all_md.append(md_text[:cut_index])
                stop = True
                break
            all_md.append(md_text)

    with open(final_md, "w", encoding="utf-8") as f:
        f.write("\n".join(all_md))


def process_pdf(pdf_path, md_path):
    if os.path.exists(md_path):
        return

    try:
        with semaphore:
            job_id = submit_job(pdf_path)
        json_url = wait_for_result(job_id)
        if json_url:
            download_and_merge(json_url, md_path)
    except Exception as e:
        tqdm.write(f"Error processing {os.path.basename(pdf_path)}: {e}")


if __name__ == "__main__":
    args = parse_args()
    pdf_files = glob(args.files)

    tasks = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for pdf_file in pdf_files:
            md_file = pdf_file.replace(".pdf", ".md")
            tasks.append(executor.submit(process_pdf, pdf_file, md_file))

        for future in tqdm(as_completed(tasks), total=len(tasks), desc="OCR"):
            pass
