# Qubes OS Ultimate Guide

> **Complete Qubes OS official documentation — compiled into a single, AI-readable Markdown file.**

## What Is This?

This is the **entire [Qubes OS official documentation](https://github.com/QubesOS/qubes-doc)** (191 pages, ~1.5 MB) converted from RST to clean Markdown and organized into 11 logical sections. No content has been removed, filtered, or summarized — every command, configuration, warning, and note is preserved verbatim.

It's designed to be:

- **AI-friendly** — load the whole file into an LLM context or RAG pipeline and query any Qubes topic
- **Searchable** — `grep`, `Ctrl+F`, or semantic search across all Qubes docs at once
- **Offline** — a single file you can read anywhere, no internet needed

## Contents

| # | Section | Topics | Description |
|---|---------|--------|-------------|
| 1 | [Introduction](#1-introduction) | 13 | FAQ, getting started, support, code of conduct |
| 2 | [Downloading & Installing](#2-downloading--installing) | 17 | Installation guide, system requirements, upgrade paths (2→4.3) |
| 3 | [Hardware & System Requirements](#3-hardware--system-requirements) | 14 | Certified hardware, HCL, system requirements |
| 4 | [How-to Guides](#4-how-to-guides) | 21 | USB devices, PCI devices, backups, file copying, disposables, updates |
| 5 | [Security in Qubes](#5-security-in-qubes) | 9 | Split GPG, firewall, device security, anti-evil-maid, MFA, data leak prevention |
| 6 | [Templates](#6-templates) | 11 | Fedora, Debian, Windows, minimal templates, XFCE |
| 7 | [Advanced Topics](#7-advanced-topics) | 20 | Salt, bind-dirs, RPC policy, USB qubes, disk resize, standalone HVMs, i3/awesome/KDE |
| 8 | [Troubleshooting](#8-troubleshooting) | 15 | Installation, UEFI, PCI, USB, GUI, disk, HVM, VM troubleshooting |
| 9 | [Reference](#9-reference) | 2 | Glossary, command-line tools |
| 10 | [Project Security](#10-project-security) | 3 | Security bulletins, PGP key verification, security pack |
| 11 | [Developer Documentation](#11-developer-documentation) | 66 | Qubes Builder, architecture, qrexec internals, admin API, coding style |

## How It Was Made

1. **Source**: Cloned from [QubesOS/qubes-doc](https://github.com/QubesOS/qubes-doc) official repository
2. **Conversion**: Custom Python script converts RST → Markdown:
   - Section headers (`===`, `---`, `~~~`) → `#`, `##`, `###`
   - `.. code:: language` → ` ```language `
   - `.. note::` / `.. warning::` / `.. important::` → blockquote admonitions
   - Sphinx cross-references → italic text with paths
   - Images, navigation, and build artifacts stripped (non-text content)
3. **Organization**: 191 RST files grouped into 11 topical sections with a clickable Table of Contents
4. **Quality**: Zero content loss — every command, step, and warning preserved

## Content Date

**As of 2026-04-23** — sourced from the Qubes OS documentation repository at that date.

## Usage

### For AI / LLM
```bash
# Load into Claude, ChatGPT, or any LLM via context/RAG
# The TOC at the top helps the model navigate
cat qubes-guides.md
```

### For humans
```bash
# Search for any topic
grep -i "split gpg" qubes-guides.md
grep -i "usb qube" qubes-guides.md

# Read in your favorite Markdown viewer
glow qubes-guides.md
```

### As a RAG knowledge base
The hierarchical structure (`# Section` → `## Topic` → `### Subsection`) is ideal for chunking strategies.

## License

Original content © Qubes OS Project. This compilation is a derivative work for educational and reference purposes.

---

⭐ **Star this repo** if you find it useful! Contributions and updates welcome.
