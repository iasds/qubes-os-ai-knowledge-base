#!/usr/bin/env python3
"""爬取 Qubes OS 论坛 Community Guides 分区所有指南，合并为一个 markdown 文件。"""

import requests
import time
import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://forum.qubes-os.org"
CATEGORY_JSON = f"{BASE}/c/guides/14.json"
RAW_TOPIC = f"{BASE}/raw"
OUTPUT = Path(__file__).parent / "qubes-guides.md"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

# 排除的帖子：置顶帖、分类说明帖
EXCLUDE_IDS = {
    45,     # About the Community Guides category (pinned)
    38466,  # Meta-topic: List of all VPN guides (pinned)
}


def fetch_url(url, as_json=True, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json() if as_json else r.text
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(2)


def get_all_topics():
    topics = []
    page = 1
    while True:
        print(f"📄 获取第 {page} 页...")
        data = fetch_url(f"{CATEGORY_JSON}?page={page}")
        if not data:
            break
        page_topics = data.get("topic_list", {}).get("topics", [])
        if not page_topics:
            break
        topics.extend(page_topics)
        more = data.get("topic_list", {}).get("more_topics_url")
        if not more:
            break
        page += 1
    return topics


def strip_first_post(raw_text):
    if not raw_text:
        return ""
    parts = raw_text.split("\n-------------------------\n", 1)
    first = parts[0].strip()
    # 去掉第一行元信息 "username | timestamp | #1"
    first = re.sub(r'^.*?\|\s*\d{4}-\d{2}-\d{2}.*?\|\s*#1\s*\n', '', first, count=1)
    # 去掉 Discourse TOC div
    first = re.sub(r'<div data-theme-toc="true">\s*</div>', '', first)
    return first.strip()


def fetch_one(topic):
    """获取单个帖子的正文。返回 (title, body) 或 (title, None) 表示失败。"""
    tid = topic["id"]
    title = topic["title"]
    raw = fetch_url(f"{RAW_TOPIC}/{tid}", as_json=False)
    if raw is None:
        return (title, None)
    body = strip_first_post(raw)
    return (title, body if body else None)


def main():
    print("=" * 50)
    print("Qubes OS 论坛社区指南爬虫")
    print("=" * 50)

    # 1. 获取所有帖子
    all_topics = get_all_topics()
    print(f"\n✅ 共获取 {len(all_topics)} 个帖子\n")

    # 2. 过滤
    guides = [t for t in all_topics if t["id"] not in EXCLUDE_IDS]
    print(f"📋 过滤后剩余 {len(guides)} 篇指南\n")

    # 3. 并发获取正文
    articles = []
    failed = []
    done = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_one, t): t for t in guides}
        for f in as_completed(futures):
            done += 1
            title, body = f.result()
            if body:
                articles.append((title, body))
            else:
                failed.append(title)
            print(f"\r⏳ [{done}/{len(guides)}] {title[:50]}...", end="", flush=True)

    print()

    # 4. 写入 markdown
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Qubes OS 社区指南汇总\n\n")
        f.write(f"> 来源：{BASE}/c/guides/14\n")
        f.write(f"> 共 {len(articles)} 篇指南\n\n")
        f.write("---\n\n")

        for title, body in articles:
            f.write(f"## {title}\n\n")
            f.write(body)
            f.write("\n\n---\n\n")

    print(f"\n{'='*50}")
    print(f"✅ 完成！{len(articles)} 篇指南已写入 {OUTPUT}")
    if failed:
        print(f"⚠ 失败 {len(failed)} 篇：")
        for t in failed[:10]:
            print(f"  - {t}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
