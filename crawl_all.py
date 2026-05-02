#!/usr/bin/env python3
"""爬取 Qubes OS 论坛所有板块，按分组输出为独立 markdown 文件。"""

import requests
import time
import re
import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

BASE = "https://forum.qubes-os.org"
RAW_TOPIC = f"{BASE}/raw"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

OUTPUT_DIR = Path(__file__).parent / "references"

# 速率控制
REQ_DELAY = 0.15  # 请求间隔（秒）— 加速模式
_last_req = 0.0
_req_lock = Lock()


def wait_rate():
    """确保两次请求之间间隔 >= REQ_DELAY"""
    global _last_req
    with _req_lock:
        now = time.time()
        gap = REQ_DELAY - (now - _last_req)
        if gap > 0:
            time.sleep(gap)
        _last_req = time.time()


def safe_get(url, as_json=True):
    """带限速和重试的 GET 请求。429 时等待后重试。"""
    for attempt in range(5):
        try:
            wait_rate()
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 429:
                delay = int(r.headers.get("Retry-After", 10))
                print(f"     ⚡ 限流，等待 {delay}s...", flush=True)
                time.sleep(delay + 2)
                continue
            r.raise_for_status()
            return r.json() if as_json else r.text
        except requests.exceptions.Timeout:
            print(f"     ⏱ 超时，重试...", flush=True)
            if attempt == 4:
                return None
            time.sleep(3)
        except Exception as e:
            if attempt == 4:
                return None
            time.sleep(1 + attempt)
    return None


FILE_CATEGORIES = {
    "user-support.md": [
        ("user-support", 5, "User Support"),
        ("hardware-issues", 13, "Hardware Issues"),
        ("hcl-reports", 23, "HCL Reports"),
        ("general-support", 24, "General Support"),
        ("testing-release", 37, "Testing Release"),
        ("help-hacked", 42, "Help, I think I've been hacked"),
    ],
    "general-discussion.md": [
        ("general-discussion", 15, "General Discussion"),
    ],
    "community-guides.md": [
        ("guides", 14, "Community Guides"),
        ("high-quality-guides", 43, "High Quality Guides"),
    ],
    "testing.md": [
        ("testing-team", 28, "Testing Team"),
        ("4-2-testing", 29, "4.2 Testing"),
        ("4-1-testing", 30, "4.1 Testing"),
        ("43-testing", 45, "4.3 Testing"),
        ("44-testing", 46, "4.4 Testing"),
    ],
    "news.md": [
        ("news", 6, "News"),
    ],
    "qubes-users-mailing.md": [
        ("qubes-users", 21, "qubes-users Mailing List"),
    ],
    "feedback.md": [
        ("feedback", 16, "Feedback"),
        ("forum-feedback", 2, "Forum Feedback"),
        ("website", 8, "Website Feedback"),
        ("forum-account-deletion-requests", 36, "Account Deletion Requests"),
    ],
    "paid-support.md": [
        ("paid-support-providers", 44, "Paid Support Providers"),
    ],
    "multilingual.md": [
        ("in-your-language", 12, "In your language"),
        ("chinese", 9, "中文"),
        ("german", 10, "Deutsch"),
        ("spanish", 11, "Español"),
        ("portuguese", 27, "Português"),
        ("italian", 32, "Italiano"),
        ("francais-french", 33, "Français"),
        ("japanese-japanese", 34, "日本語"),
        ("p-russian", 35, "Pусский"),
        ("bahasa-indonesia-indonesian", 38, "Bahasa Indonesia"),
        ("korean", 39, "한국어"),
    ],
    "uncategorized.md": [
        ("uncategorized", 1, "Uncategorized"),
    ],
}


def get_topics_for_category(slug, cat_id):
    """获取某个板块的所有帖子列表。"""
    topics = []
    page = 0
    while True:
        data = safe_get(f"{BASE}/c/{slug}/{cat_id}.json?page={page}")
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
    """从 raw 端点提取第一个帖子的正文。"""
    if not raw_text:
        return ""
    parts = raw_text.split("\n-------------------------\n", 1)
    first = parts[0].strip()
    first = re.sub(r'^.*?\|\s*\d{4}-\d{2}-\d{2}.*?\|\s*#1\s*\n', '', first, count=1)
    first = re.sub(r'<div data-theme-toc="true">\s*</div>', '', first)
    return first.strip()


def fetch_one(topic):
    """获取单个帖子正文。返回 (title, body, topic_id, cat_name) 或失败。"""
    tid = topic["id"]
    title = topic["title"]
    cat_name = topic.get("_cat_name", "")
    raw = safe_get(f"{RAW_TOPIC}/{tid}", as_json=False)
    if raw is None:
        return (title, None, tid, cat_name)
    body = strip_first_post(raw)
    return (title, body if body else None, tid, cat_name)


def collect_topics(categories):
    """收集多个板块的帖子，去重。"""
    seen_ids = set()
    all_topics = []
    for slug, cat_id, desc in categories:
        print(f"  📂 {desc} (/{slug}/{cat_id})...", flush=True)
        topics = get_topics_for_category(slug, cat_id)
        new_count = 0
        for t in topics:
            tid = t["id"]
            if tid not in seen_ids:
                seen_ids.add(tid)
                t["_cat_name"] = desc
                all_topics.append(t)
                new_count += 1
        print(f"     → {len(topics)} 话题, {new_count} 新增", flush=True)
    return all_topics


def crawl_file(filename, categories):
    """爬取一组板块并写入一个 markdown 文件。支持增量续爬。"""
    output_path = OUTPUT_DIR / filename
    progress_path = OUTPUT_DIR / f".progress_{filename}"
    print(f"\n{'='*60}")
    print(f"📝 {filename}")
    print(f"{'='*60}")

    all_topics = collect_topics(categories)
    if not all_topics:
        print(f"  ⚠ 无帖子，跳过")
        return 0

    topics = [t for t in all_topics if not t.get("pinned", False)]
    pinned_count = len(all_topics) - len(topics)
    print(f"\n  📊 共 {len(all_topics)} 话题, 过滤 {pinned_count} 置顶帖, 剩余 {len(topics)} 篇\n")

    done_ids = set()
    if progress_path.exists():
        with open(progress_path) as pf:
            done_ids = {int(line.strip()) for line in pf if line.strip()}
        print(f"  📂 续爬：已完成 {len(done_ids)} 篇\n")

    remaining = [t for t in topics if t["id"] not in done_ids]
    if not remaining:
        print(f"  ✅ 全部已完成")
        return len(done_ids)

    is_resume = bool(done_ids)
    if not is_resume:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Qubes OS Forum — {filename.replace('.md','').replace('-',' ').title()}\n\n")
            f.write(f"> 来源：{BASE}\n")
            f.write(f"> 板块：{', '.join(c[2] for c in categories)}\n")
            f.write(f"> 爬取时间：{time.strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")

    written = len(done_ids)
    failed = []
    done = 0
    total = len(remaining)
    file_lock = Lock()

    def fetch_and_write(topic):
        nonlocal written
        title, body, tid, cat_name = fetch_one(topic)
        if body:
            with file_lock:
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(f"## {title}\n\n")
                    if cat_name:
                        f.write(f"> 板块: {cat_name}\n\n")
                    f.write(body)
                    f.write("\n\n---\n\n")
                with open(progress_path, "a") as pf:
                    pf.write(f"{tid}\n")
                written += 1
        else:
            failed.append((title, tid))
        return (title, body is not None)

    with ThreadPoolExecutor(max_workers=5) as pool:  # 加速并发
        futures = {pool.submit(fetch_and_write, t): t for t in remaining}
        for f in as_completed(futures):
            done += 1
            title, ok = f.result()
            if done % 30 == 0 or done == total:
                print(f"  ⏳ [{done}/{total}] ({written} ✓) {title[:50]}...", flush=True)

    size_kb = output_path.stat().st_size / 1024
    print(f"\n  ✅ {written} 篇 → {output_path} ({size_kb:.0f} KB)")
    if failed:
        print(f"  ⚠ 失败 {len(failed)} 篇:")
        for t, tid in failed[:10]:
            print(f"    - [{tid}] {t}")
        if len(failed) > 10:
            print(f"    ... 还有 {len(failed)-10} 篇")
    return written


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(FILE_CATEGORIES.keys())

    total_articles = 0
    start = time.time()

    for filename in targets:
        if filename not in FILE_CATEGORIES:
            print(f"⚠ 未知文件: {filename}")
            continue
        count = crawl_file(filename, FILE_CATEGORIES[filename])
        total_articles += count

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"🎉 全部完成！共 {total_articles} 篇帖子, 耗时 {elapsed/60:.1f} 分钟")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
