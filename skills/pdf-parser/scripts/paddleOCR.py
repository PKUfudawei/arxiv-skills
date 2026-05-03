#!/usr/bin/env python3
"""
OCR script to convert PDF papers to markdown using PaddleOCR
"""

import json
import os
import requests
import argparse
import threading
import time
from glob import glob

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()


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
    parser.add_argument("-f", "--files", type=str, default="../data/arxiv/*/*.pdf")
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
    output_dir = os.path.dirname(final_md)
    os.makedirs(output_dir, exist_ok=True)

    for line in lines:
        if not line.strip():
            continue
        result = json.loads(line)["result"]
        for res in result["layoutParsingResults"]:
            if stop:
                continue
            md_text = res["markdown"]["text"]

            for img_path, img_data in res["markdown"]["images"].items():
                img_bytes = requests.get(img_data).content
                full_img_path = os.path.join(output_dir, img_path)
                os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
                with open(full_img_path, "wb") as f:
                    f.write(img_bytes)
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
    with ThreadPoolExecutor(max_workers=16) as executor:
        for pdf_file in pdf_files:
            md_file = pdf_file.replace(".pdf", ".md")
            if os.path.exists(md_file):
                tqdm.write(f"Skipping {os.path.basename(pdf_file)}: MD already exists")
                continue
            tasks.append(executor.submit(process_pdf, pdf_file, md_file))
            time.sleep(1)

        for future in tqdm(as_completed(tasks), total=len(tasks), desc="OCR"):
            pass
