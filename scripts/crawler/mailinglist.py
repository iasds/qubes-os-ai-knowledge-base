"""Qubes mailing list crawler via mail-archive.com RSS.

Output: kb/mailing-lists/{list-name}/{msg-id}.md
"""

import hashlib
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from .utils import KB_DIR, USER_AGENT

MAILING_LISTS = [
    ("qubes-users", "https://www.mail-archive.com/qubes-users@googlegroups.com/maillist.xml"),
    ("qubes-devel", "https://www.mail-archive.com/qubes-devel@googlegroups.com/maillist.xml"),
    ("qubes-announce", "https://www.mail-archive.com/qubes-announce@googlegroups.com/maillist.xml"),
]

MAIL_DIR = KB_DIR / "mailing-lists"


def _fetch_rss(url: str) -> list[dict]:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_data = resp.read()
    root = ET.fromstring(xml_data)
    items = []
    for item_elem in root.findall(".//item"):
        item = {}
        for child in item_elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            item[tag] = (child.text or "").strip()
        items.append(item)
    return items


def _extract_msg_id(link: str) -> str:
    m = re.search(r"(msg\d+)", link)
    return m.group(1) if m else ""


def _html_to_plain(html_str: str) -> str:
    text = html.unescape(html_str)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def run(dry_run: bool = False):
    print("╔══ Mailing List Crawler ══╗")
    MAIL_DIR.mkdir(parents=True, exist_ok=True)
    total_new = 0
    total_skipped = 0
    for list_name, rss_url in MAILING_LISTS:
        print(f"\n  [{list_name}]")
        try:
            items = _fetch_rss(rss_url)
        except Exception as e:
            print(f"    [ERROR] {e}")
            continue
        print(f"    RSS: {len(items)} items")
        list_dir = MAIL_DIR / list_name
        list_dir.mkdir(parents=True, exist_ok=True)
        new_count = 0
        for item in items:
            link = item.get("link", "")
            msg_id = _extract_msg_id(link)
            if not msg_id:
                continue
            fpath = list_dir / f"{msg_id}.md"
            title = item.get("title", "No subject")
            pub_date = item.get("pubDate", "")
            desc = item.get("description", "")
            plain_desc = _html_to_plain(desc)
            sender = ""
            m = re.search(r"([\w.@+-]+)\s+([Ww]rote)", plain_desc)
            if m:
                sender = m.group(1)
            else:
                m = re.search(r"([\w.+-]+@[\w.+-]+)", plain_desc)
                if m:
                    sender = m.group(1)
            clean_desc = re.sub(r"^\d{4}/\d{2}/\d{2}\s*--\s*", "", plain_desc)
            content_hash = hashlib.sha256((title + pub_date + clean_desc).encode()).hexdigest()[:16]
            md = (
                f"---\nid: {msg_id}\nsource: mailing-list\nlist: {list_name}@googlegroups.com\n"
                f"title: {title}\nsender: {sender}\ndate: {pub_date}\nsha256: {content_hash}\nurl: {link}\n"
                f"---\n\n# {title}\n\n"
                f"**List**: {list_name}@googlegroups.com  \n**Date**: {pub_date}  \n**Sender**: {sender}  \n"
                f"**URL**: [{link}]({link})\n\n{clean_desc}\n"
            )
            if fpath.exists():
                existing = fpath.read_text(encoding="utf-8")[:500]
                if f"sha256: {content_hash}" in existing:
                    total_skipped += 1
                    continue
            if dry_run:
                new_count += 1
                continue
            fpath.write_text(md, encoding="utf-8")
            new_count += 1
        print(f"    New: {new_count}")
        total_new += new_count
    print(f"\n  Total: {total_new} new, {total_skipped} unchanged")
    print("╚══ Mailing lists complete ══╝")


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
