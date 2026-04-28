# Qubes OS 终极指南

**为 AI / LLM 准备的 Qubes OS 知识大全。** 将官方文档与社区精华合并为单一 Markdown 文件，方便 AI 一次性加载、检索、回答 Qubes 相关问题。

## 数据来源

| 来源 | 内容 | 数量 |
|---|---|---|
| [QubesOS/qubes-doc](https://github.com/QubesOS/qubes-doc) | Qubes OS 官方文档（RST → Markdown 转换） | 191 页 |
| [forum.qubes-os.org/c/guides/14](https://forum.qubes-os.org/c/guides/14) | 社区论坛精华指南（全文爬取） | 499 篇 |
| **合计** | | **690 篇 / ~4MB** |

> 全部原始内容一字未删，仅做格式转换与合并。内容截至 **2026-04-23**。
>
> 📢 Qubes OS 中文 Telegram 频道：[t.me/qubeszh](https://t.me/qubeszh)
>
> [English](README.md)

## 文件

- **`qubes-guides.md`** — 主文件，3.95 MB，含完整目录索引，AI 可直接读取
- `crawl_guides.py` — 论坛爬虫脚本

## 使用方式

```
# 喂给 AI — 作为上下文或 RAG 知识库
cat qubes-guides.md

# 人肉搜索
grep -i "split gpg" qubes-guides.md
```

## 许可

原始内容 © Qubes OS Project。本仓库为教育和参考用途的衍生整理。
