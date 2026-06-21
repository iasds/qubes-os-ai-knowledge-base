"""Generate kb/index.md from kb/ directory structure.

Usage: python3 scripts/index_gen.py
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_frontmatter(fpath: Path) -> dict:
    content = fpath.read_text(encoding="utf-8")[:2000]
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    fm = content[3:end]
    result = {}
    for line in fm.strip().split("\n"):
        m = re.match(r"^(\w+):\s*(.+)$", line)
        if m:
            result[m.group(1)] = m.group(2).strip().strip('"')
    return result


def count_files(base: Path) -> int:
    return len(list(base.rglob("*.md"))) if base.exists() else 0


def generate(kb_dir: str = "kb") -> str:
    kb = Path(kb_dir)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    official_count = count_files(kb / "official")
    forum_count = count_files(kb / "forum")
    mail_count = count_files(kb / "mailing-lists")
    total = official_count + forum_count + mail_count

    lines = [
        "# Qubes OS 知识库索引", "",
        f"> 总计 **{total}** 篇 | 官方 {official_count} + 论坛 {forum_count} + 邮件列表 {mail_count} | 更新 {now}", "",
        "## 官方文档 (`kb/official/`)", ""
    ]
    _build_section(lines, kb / "official", max_entries=None)
    lines.append("")

    if (kb / "forum").exists():
        lines.append("## 论坛 (`kb/forum/`)")
        for cat_dir in sorted((kb / "forum").iterdir()):
            if cat_dir.is_dir():
                cnt = count_files(cat_dir)
                lines.extend(["", f"### {cat_dir.name} ({cnt})", ""])
                _build_section(lines, cat_dir, max_entries=50)
        lines.append("")

    if (kb / "mailing-lists").exists():
        lines.append("## 邮件列表 (`kb/mailing-lists/`)")
        for ml_dir in sorted((kb / "mailing-lists").iterdir()):
            if ml_dir.is_dir():
                cnt = count_files(ml_dir)
                lines.extend(["", f"### {ml_dir.name} ({cnt})", ""])
                _build_section(lines, ml_dir, max_entries=50)
        lines.append("")

    lines.extend([
        "---",
        f"*最后生成: {now} | "
        "来源: [qubes-doc](https://github.com/QubesOS/qubes-doc) + "
        "[Qubes Forum](https://forum.qubes-os.org) + mail-archive*"
    ])
    return "\n".join(lines)


def _build_section(lines, base_dir, max_entries=None):
    entries = []
    for fpath in sorted(base_dir.rglob("*.md")):
        rel = fpath.relative_to(base_dir.parent.parent)
        fm = read_frontmatter(fpath)
        title = fm.get("title", fpath.stem)
        date = fm.get("date", fm.get("created_at", fm.get("last_updated", "")))[:10]
        entries.append((title, rel, date))
    if max_entries and len(entries) > max_entries:
        entries.sort(key=lambda x: x[2], reverse=True)
        entries = entries[:max_entries]
        lines.append(f"  *...（只显示最近 {max_entries} 条）*")
        lines.append("")
    for title, rel, date in entries:
        line = f"- [{title}]({rel})"
        if date:
            line += f" — {date}"
        lines.append(line)


if __name__ == "__main__":
    kb_dir = "kb"
    idx = generate(kb_dir)
    Path(kb_dir, "index.md").write_text(idx, encoding="utf-8")
    print(f"Written: kb/index.md ({len(idx)} bytes)")
