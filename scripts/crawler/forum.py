"""Qubes Forum concurrent crawler — all categories, all topics, all posts.

Usage from repo root: cd scripts && python3 -m crawler.forum [--dry-run]
"""

import concurrent.futures
import os
import sys
import re
import threading
from pathlib import Path

from .utils import KB_DIR, fetch_json, html_to_md, sanitize_filename, scan_existing, read_frontmatter_field

FORUM_BASE = "https://forum.qubes-os.org"
FORUM_DIR = KB_DIR / "forum"

CATEGORY_WORKERS = 3
DETAIL_WORKERS = 2     # ultra-conservative to avoid 429

_lock = threading.Lock()
_done_count = 0


def get_categories() -> list[dict]:
    data = fetch_json(f"{FORUM_BASE}/site.json")
    return [c for c in data.get("categories", []) if c.get("topic_count", 0) > 0]


def get_category_topics(category: dict) -> tuple[str, list[dict]]:
    slug = category["slug"]
    cid = category["id"]
    all_topics = []
    page = 0
    while True:
        try:
            data = fetch_json(f"{FORUM_BASE}/c/{slug}/{cid}.json?page={page}")
            topics = data["topic_list"].get("topics", [])
            all_topics.extend(topics)
            if not data["topic_list"].get("more_topics_url"):
                break
            page += 1
        except Exception as e:
            print(f"  [WARN] {slug} page {page}: {e}")
            break
    return slug, all_topics


def get_all_topics(categories: list[dict]) -> list[dict]:
    all_topics = []
    cat_topics: dict[str, int] = {}
    print(f"Fetching topic lists from {len(categories)} categories "
          f"({CATEGORY_WORKERS} concurrent)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=CATEGORY_WORKERS) as executor:
        futures = {executor.submit(get_category_topics, cat): cat for cat in categories}
        for future in concurrent.futures.as_completed(futures):
            cat = futures[future]
            try:
                slug, topics = future.result()
                print(f"  {slug}: {len(topics)} topics")
                cat_topics[slug] = len(topics)
                for t in topics:
                    t["_category_slug"] = slug
                all_topics.extend(topics)
            except Exception as e:
                print(f"  [ERROR] {cat['slug']}: {e}")
    print(f"\nTotal: {len(all_topics)} topics across {len(cat_topics)} categories")
    return all_topics


def fetch_and_write_topic(topic: dict) -> bool:
    global _done_count
    tid = topic["id"]
    slug = topic["_category_slug"]
    title = topic.get("title", f"Topic {tid}")
    try:
        data = fetch_json(f"{FORUM_BASE}/t/{tid}.json")
    except Exception as e:
        with _lock:
            sys.stderr.write(f"  [ERR] fetch topic {tid}: {e}\n")
        return False
    posts = data.get("post_stream", {}).get("posts", [])
    if not posts:
        return False
    md = _build_topic_md(topic, posts)
    cat_dir = FORUM_DIR / slug
    cat_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{sanitize_filename(title)}-{tid}.md"
    filepath = cat_dir / filename
    try:
        filepath.write_text(md, encoding="utf-8")
    except OSError as e:
        with _lock:
            sys.stderr.write(f"  [ERR] write {filepath}: {e}\n")
        return False
    with _lock:
        _done_count += 1
        if _done_count % 100 == 0:
            print(f"  [{_done_count}]", end="", flush=True)
        elif _done_count % 20 == 0:
            print(".", end="", flush=True)
    return True


def _build_topic_md(topic: dict, posts: list[dict]) -> str:
    tid = topic["id"]
    slug = topic["_category_slug"]
    title = topic.get("title", f"Topic {tid}")
    first_author = posts[0].get("username", "unknown") if posts else "unknown"
    created = topic.get("created_at", "")
    updated = topic.get("last_posted_at", topic.get("bumped_at", ""))
    url = f"{FORUM_BASE}/t/{topic.get('slug', tid)}/{tid}"
    tags = topic.get("tags", [])
    views = topic.get("views", 0)
    likes = topic.get("like_count", 0)
    post_count = topic.get("posts_count", len(posts))
    parts = ["---", f"id: {tid}", f"title: {_esc(title)}", f"category: {slug}",
             f"author: {first_author}", f"created_at: {created}", f"last_updated: {updated}",
             f"total_posts: {post_count}", f"views: {views}", f"likes: {likes}"]
    if tags:
        parts.append(f"tags: [{', '.join(tags)}]")
    parts.append(f"url: {url}")
    parts.append("---")
    parts.append("")
    parts.append(f"# {title}")
    parts.append("")
    for i, post in enumerate(posts, 1):
        username = post.get("username", "unknown")
        post_created = post.get("created_at", "")
        cooked = post.get("cooked", "")
        post_number = post.get("post_number", i)
        if not cooked.strip():
            continue
        md_content = html_to_md(cooked)
        parts.append(f"## 回复 #{post_number} — **{username}** _{post_created}_")
        parts.append("")
        parts.append(md_content)
        parts.append("")
    parts.append("---")
    parts.append(f"*来源: [{FORUM_BASE}/t/{topic.get('slug', tid)}/{tid}]({url})*")
    return "\n".join(parts)


def _esc(value: str) -> str:
    return f'"{value}"' if any(c in value for c in '":{}[]&*!|>\'@`,') else value


def remove_deleted_topics(remote_topic_ids: set[str], existing: dict[str, Path]):
    removed = 0
    for tid, fpath in existing.items():
        if tid not in remote_topic_ids:
            try:
                os.remove(fpath)
                removed += 1
            except OSError:
                pass
    for cat_dir in sorted(FORUM_DIR.iterdir()):
        if cat_dir.is_dir() and not any(cat_dir.iterdir()):
            try:
                cat_dir.rmdir()
            except OSError:
                pass
    if removed:
        print(f"  Removed {removed} deleted topics")


def run(dry_run: bool = False):
    global _done_count
    _done_count = 0
    print("╔══ Qubes Forum Crawler ══╗")
    FORUM_DIR.mkdir(parents=True, exist_ok=True)
    print("\n[Phase 1] Getting categories...")
    categories = get_categories()
    print(f"  Found {len(categories)} active categories")
    print("\n[Phase 2] Fetching all topic lists...")
    all_topics = get_all_topics(categories)
    remote_ids = {str(t["id"]) for t in all_topics}
    print("\n[Phase 3] Checking existing files...")
    existing = scan_existing(FORUM_DIR)
    print(f"  Local: {len(existing)} files")
    to_fetch = []
    skipped = 0
    for t in all_topics:
        tid = str(t["id"])
        fpath = existing.get(tid)
        if fpath is None:
            to_fetch.append(t)
            continue
        topic_updated = t.get("last_posted_at", t.get("bumped_at", ""))
        file_updated = read_frontmatter_field(fpath, "last_updated")
        if topic_updated and file_updated and topic_updated > file_updated:
            to_fetch.append(t)
        else:
            skipped += 1
    remove_deleted_topics(remote_ids, existing)
    print(f"  New/updated: {len(to_fetch)}, Unchanged: {skipped}")
    if dry_run:
        print("\n[DRY RUN] Would fetch:")
        for t in to_fetch[:10]:
            print(f"  [{t['_category_slug']}] #{t['id']}: {t.get('title', '')[:60]}")
        if len(to_fetch) > 10:
            print(f"  ... and {len(to_fetch) - 10} more")
        print("\nDone (dry run).")
        return
    if not to_fetch:
        print("\n  Nothing to fetch. Done.")
        return
    print(f"\n[Phase 4] Fetching {len(to_fetch)} topic details ({DETAIL_WORKERS} concurrent)...")
    print("  ", end="", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
        futures = [executor.submit(fetch_and_write_topic, t) for t in to_fetch]
        concurrent.futures.wait(futures)
    success = sum(1 for f in futures if f.result())
    failed = len(futures) - success
    print(f"\n  Fetched: {success} succeeded, {failed} failed")
    print("╚══ Forum crawl complete ══╝")


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
