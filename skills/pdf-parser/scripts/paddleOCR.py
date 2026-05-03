#!/usr/bin/env python3
"""
Robust OCR script: PDF -> Markdown (PaddleOCR API)
"""

import json
import os
import requests
import argparse
import threading
import time
import traceback
from glob import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
MODEL = "PaddleOCR-VL-1.5"

TOKEN = os.getenv("PADDLE_TOKEN")
if not TOKEN:
    raise ValueError("PADDLE_TOKEN not set")

headers = {"Authorization": f"bearer {TOKEN}"}

optional_payload = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}

# 全局限流（所有 HTTP 请求）
REQUEST_SEMAPHORE = threading.Semaphore(5)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", nargs="+", default=["../data/arxiv/*/*.pdf"])
    parser.add_argument("--workers", type=int, default=5)
    return parser.parse_args()


# -----------------------
# 通用请求函数（带 retry）
# -----------------------
def safe_request(method, url, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            with REQUEST_SEMAPHORE:
                resp = requests.request(method, url, timeout=60, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


# -----------------------
# 提交任务
# -----------------------
def submit_job(file_path):
    data = {"model": MODEL, "optionalPayload": json.dumps(optional_payload)}

    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = safe_request("POST", JOB_URL, headers=headers, data=data, files=files)

    return resp.json()["data"]["jobId"]


# -----------------------
# 等待结果（带 timeout）
# -----------------------
def wait_for_result(job_id, timeout=600, interval=5):
    start = time.time()

    while True:
        if time.time() - start > timeout:
            raise TimeoutError(f"Job {job_id} timeout")

        resp = safe_request("GET", f"{JOB_URL}/{job_id}", headers=headers)
        data = resp.json()["data"]

        state = data["state"]

        if state == "done":
            return data["resultUrl"]["jsonUrl"]
        elif state == "failed":
            return None

        time.sleep(interval)


# -----------------------
# 下载并合并 markdown
# -----------------------
def download_and_merge(jsonl_url, final_md):
    resp = safe_request("GET", jsonl_url)
    lines = resp.text.strip().split("\n")

    all_md = []
    output_dir = os.path.dirname(final_md)
    os.makedirs(output_dir, exist_ok=True)

    for line in lines:
        if not line.strip():
            continue

        result = json.loads(line)["result"]

        for res in result["layoutParsingResults"]:
            md_text = res["markdown"]["text"]

            # 下载图片
            for img_path, img_url in res["markdown"]["images"].items():
                try:
                    img_resp = safe_request("GET", img_url)
                    full_img_path = os.path.join(output_dir, img_path)
                    os.makedirs(os.path.dirname(full_img_path), exist_ok=True)

                    with open(full_img_path, "wb") as f:
                        f.write(img_resp.content)
                except Exception:
                    tqdm.write(f"[WARN] Image download failed: {img_url}")

            all_md.append(md_text)

    with open(final_md, "w", encoding="utf-8") as f:
        f.write("\n".join(all_md))


# -----------------------
# 主处理逻辑
# -----------------------
def process_pdf(pdf_path):
    md_path = os.path.splitext(pdf_path)[0] + ".md"

    if os.path.exists(md_path):
        return "skip", pdf_path

    try:
        job_id = submit_job(pdf_path)
        json_url = wait_for_result(job_id)

        if not json_url:
            return "failed", pdf_path

        download_and_merge(json_url, md_path)
        return "success", pdf_path

    except Exception:
        tqdm.write(f"[ERROR] {pdf_path}")
        tqdm.write(traceback.format_exc())
        return "error", pdf_path


# -----------------------
# 主程序
# -----------------------
if __name__ == "__main__":
    args = parse_args()

    pdf_files = []
    for pattern in args.files:
        expanded = glob(pattern)
        if expanded:
            pdf_files.extend(expanded)
        elif os.path.exists(pattern):
            pdf_files.append(pattern)

    results = {"success": [], "failed": [], "error": [], "skip": []}

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(process_pdf, pdf) for pdf in pdf_files]

        for future in tqdm(as_completed(futures), total=len(futures), desc="OCR"):
            status, path = future.result()
            results[status].append(path)

    # summary
    print("\n===== Summary =====")
    for k, v in results.items():
        print(f"{k}: {len(v)}")

    # 保存失败列表（方便重跑）
    if results["failed"] or results["error"]:
        with open("failed_files.txt", "w") as f:
            for x in results["failed"] + results["error"]:
                f.write(x + "\n")
