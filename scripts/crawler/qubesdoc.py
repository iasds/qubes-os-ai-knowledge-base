"""Qubes OS official documentation crawler.

Clones qubes-doc repo, converts .rst to Markdown, syncs to kb/official/.
"""

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .utils import KB_DIR

QUBES_DOC_REPO = "https://github.com/QubesOS/qubes-doc.git"
OFFICIAL_DIR = KB_DIR / "official"
STATE_FILE = KB_DIR.parent / ".state-qubesdoc"


def _pandoc_available() -> bool:
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _rst_to_md(content: str) -> tuple[str, str]:
    if _pandoc_available():
        try:
            proc = subprocess.run(
                ["pandoc", "-f", "rst", "-t", "markdown", "--wrap=none"],
                input=content, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout, "pandoc"
        except Exception:
            pass
    return f"```rst\n{content}\n```", "raw-rst"


def run(dry_run: bool = False):
    print("╔══ Qubes Docs Crawler ══╗")
    has_pandoc = _pandoc_available()
    print(f"  pandoc: {'available' if has_pandoc else 'NOT FOUND (fallback: raw RST)'}")

    last_commit = STATE_FILE.read_text().strip() if STATE_FILE.exists() else ""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        repo_dir = tmp / "qubes-doc"
        print(f"  Cloning {QUBES_DOC_REPO}...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", QUBES_DOC_REPO, str(repo_dir)],
                capture_output=True, text=True, timeout=120, check=True)
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Clone failed: {e.stderr}")
            return

        current_commit = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10).stdout.strip()
        print(f"  Current: {current_commit[:8]}, Last: {last_commit[:8] if last_commit else 'none'}")

        if current_commit == last_commit:
            print("  No changes. Skipping.")
            return

        if dry_run:
            print(f"  [DRY RUN] Would sync RST from {repo_dir}")
            return

        OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)
        rst_files = list(repo_dir.rglob("*.rst"))
        print(f"  Found {len(rst_files)} RST files")
        converted = 0
        skipped = 0
        new_hashes: dict[str, str] = {}

        for rst_path in rst_files:
            rel_path = rst_path.relative_to(repo_dir)
            target_path = OFFICIAL_DIR / rel_path.with_suffix(".md")
            content = rst_path.read_text(encoding="utf-8", errors="replace")
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            new_hashes[str(rel_path)] = content_hash

            if target_path.exists():
                try:
                    existing = target_path.read_text(encoding="utf-8")[:500]
                    if f"sha256: {content_hash}" in existing:
                        skipped += 1
                        continue
                except Exception:
                    pass

            md_content, method = _rst_to_md(content)
            title = rst_path.stem.replace("-", " ").replace("_", " ").title()
            fm = (
                f"---\nid: {rst_path.stem}\nsource: official\ntitle: {title}\n"
                f"original: {rel_path}\ncommit: {current_commit[:8]}\n"
                f"sha256: {content_hash}\n---\n\n"
            )
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(fm + md_content, encoding="utf-8")
            converted += 1

        # Remove deleted files
        for f in OFFICIAL_DIR.rglob("*.md"):
            try:
                ct = f.read_text(encoding="utf-8")[:500]
                m = __import__("re").search(r"^original:\s*(.+)$", ct, __import__("re").MULTILINE)
                if m and m.group(1).strip() not in new_hashes:
                    f.unlink()
                    print(f"  [DEL] {m.group(1)}")
            except Exception:
                pass

        STATE_FILE.write_text(current_commit)
        print(f"  Converted: {converted}, Skipped: {skipped}, Total: {len(rst_files)}")

    print("╚══ Docs crawl complete ══╝")


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
