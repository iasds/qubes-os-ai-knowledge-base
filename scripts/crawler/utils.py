"""Qubes KB Crawler — concurrent, raw, efficient."""

import json
import os
import re
import time
import urllib.request
from pathlib import Path

# KB_DIR is ../../kb from scripts/crawler/
KB_DIR = Path(__file__).parent.parent.parent / "kb"
USER_AGENT = "Qubes-KB-Crawler/1.0 (github.com/iasds/qubes-os-ai-knowledge-base)"
REQUEST_TIMEOUT = 60

_REQUEST_DELAY = 0.5

def _rate_limit():
    time.sleep(_REQUEST_DELAY)

def fetch_json(url: str) -> dict:
    """Fetch JSON from URL with retries + backoff + rate limiting."""
    _rate_limit()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                if resp.status == 429:
                    wait = (attempt + 1) * 5
                    print(f"  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                data = json.loads(resp.read())
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 5
                print(f"  [429] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if attempt >= 4:
                raise
            time.sleep(2 ** attempt)
        except Exception as e:
            if attempt >= 4:
                raise
            time.sleep(2 ** attempt)

def html_to_md(html: str) -> str:
    """Convert Discourse cooked HTML to Markdown. Stdlib-only, no deps."""
    md = html
    md = re.sub(r'<pre[^>]*>\s*<code[^>]*>\s*(.*?)\s*</code>\s*</pre>', r'\n```\n\1\n```\n', md, flags=re.DOTALL)
    md = re.sub(r'<pre[^>]*>\s*(.*?)\s*</pre>', r'\n```\n\1\n```\n', md, flags=re.DOTALL)

    for level in range(4, 0, -1):
        md = re.sub(f"<h{level}[^>]*>(.*?)</h{level}>", f"\n{'#' * level} \\1\n", md, flags=re.DOTALL)

    md = re.sub(
        r'<aside[^>]*class="[^"]*quote[^"]*"[^>]*>.*?</aside>',
        _convert_quote, md, flags=re.DOTALL)
    md = md.replace("<blockquote>", "\n> ").replace("</blockquote>", "\n")
    md = re.sub(r"<blockquote>\s*(.*?)\s*</blockquote>", r"\n> \1\n", md, flags=re.DOTALL)
    md = re.sub(r"<li>\s*(.*?)\s*</li>", r"- \1\n", md, flags=re.DOTALL)
    md = re.sub(r"</?[ou]l[^>]*>\s*", "\n", md)
    md = re.sub(r"</?[ou]l[^>]*>", "", md)
    md = re.sub(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>\s*(.*?)\s*</details>', r"\n> **📋 \1**\n> \n\2\n\n", md, flags=re.DOTALL)
    md = re.sub(r"<(?:strong|b)>\s*(.*?)\s*</(?:strong|b)>", r"**\1**", md, flags=re.DOTALL)
    md = re.sub(r"<(?:em|i)>\s*(.*?)\s*</(?:em|i)>", r"*\1*", md, flags=re.DOTALL)
    md = re.sub(r"<code>\s*(.*?)\s*</code>", r"`\1`", md, flags=re.DOTALL)
    md = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>\s*(.*?)\s*</a>', r"[\2](\1)", md, flags=re.DOTALL)
    md = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r"![\2](\1)", md)
    md = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?>', r"![](https://forum.qubes-os.org\1)", md)
    md = md.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    md = md.replace("<hr>", "\n---\n").replace("<hr/>", "\n---\n")
    md = re.sub(r"</?p[^>]*>", "\n", md)
    md = re.sub(r"</?div[^>]*>", "\n", md)
    md = re.sub(r'<a[^>]*name="[^"]*"[^>]*></a>', "", md)
    md = re.sub(r'<a[^>]*class="anchor"[^>]*>.*?</a>', "", md, flags=re.DOTALL)
    md = re.sub(r"<[^>]+>", "", md)

    entities = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&apos;": "'", "&nbsp;": " ", "&#x27;": "'"}
    for ent, char in entities.items():
        md = md.replace(ent, char)

    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()

def _convert_quote(match: re.Match) -> str:
    html = match.group(0)
    username = ""
    post_link = ""
    title_match = re.search(r'class="[^"]*title[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    if title_match:
        title_html = title_match.group(1)
        username_match = re.search(r'<a[^>]*>(.*?)</a>', title_html, re.DOTALL)
        if username_match:
            username = username_match.group(1)
        link_match = re.search(r'href="([^"]*)"', title_html)
        if link_match:
            post_link = link_match.group(1)
    quote_content = re.sub(r'<div[^>]*class="[^"]*title[^"]*"[^>]*>.*?</div>', "", html, flags=re.DOTALL)
    quote_content = re.sub(r"</?aside[^>]*>", "", quote_content)
    quote_content = html_to_md(quote_content)
    prefix = f"> {username}" if username else ">"
    if post_link:
        prefix = f"> [{username}](https://forum.qubes-os.org{post_link})："
    elif username:
        prefix = f"> **{username}**："
    lines = quote_content.strip().split("\n")
    quoted_lines = []
    for line in lines:
        quoted_lines.append(f"> {line}" if line.strip() else ">")
    if quoted_lines:
        quoted_lines[0] = prefix + quoted_lines[0][1:]
    return "\n" + "\n".join(quoted_lines) + "\n"

def sanitize_filename(name: str, max_len: int = 60) -> str:
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "-", name)
    name = name[:max_len].strip("-").lower() or "untitled"
    return name

def scan_existing(kb_subdir: Path) -> dict[str, Path]:
    result = {}
    if not kb_subdir.exists():
        return result
    for fpath in kb_subdir.rglob("*.md"):
        try:
            content = fpath.read_text(encoding="utf-8")[:500]
            m = re.search(r"^id:\s*(\S+)", content, re.MULTILINE)
            if m:
                result[m.group(1)] = fpath
        except Exception:
            continue
    return result

def read_frontmatter_field(fpath: Path, field: str) -> str:
    try:
        content = fpath.read_text(encoding="utf-8")[:500]
        m = re.search(rf"^{field}:\s*(.+)$", content, re.MULTILINE)
        return m.group(1).strip() if m else ""
    except Exception:
        return ""
