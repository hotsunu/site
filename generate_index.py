#!/usr/bin/env python3
"""
站点目录生成器
==============
扫描本脚本所在目录下所有一级子目录中的 HTML 文件，提取每个页面的 <title>，
自动生成主网页 index.html，把所有下一级网页以目录链接的形式展示出来。

用法：
    python3 generate_index.py

以后新增、删除或改名页面后，重新运行一次即可更新主页目录。
可在下方 SITE_TITLE / SITE_DESC 处修改站点名称和简介。
"""
from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {".git", ".github", "node_modules"}

SITE_TITLE = "hotsunu 的网站"
SITE_DESC = "这是 hotsunu 的个人网站。下面列出了所有页面，点击即可打开。"

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def is_redirect_page(text: str) -> bool:
    """跳转页不列入目录。"""
    return 'http-equiv="refresh"' in text and "页面已迁移" in text


def page_title(path: Path) -> str:
    """读取页面的 <title>，读不到就用文件名。"""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return path.stem
    if is_redirect_page(text):
        return ""
    matched = TITLE_RE.search(text)
    if matched:
        title = html.unescape(re.sub(r"\s+", " ", matched.group(1)).strip())
        if title:
            return title
    return path.stem


def build_sections() -> list[tuple[str, list[tuple[str, str]]]]:
    """收集各子目录的页面，返回 [(目录名, [(标题, URL)])]。"""
    sections: list[tuple[str, list[tuple[str, str]]]] = []
    for directory in sorted(ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not directory.is_dir() or directory.name in SKIP_DIRS or directory.name.startswith("."):
            continue
        pages = sorted(directory.glob("*.html"), key=lambda p: p.name.lower())
        entries = []
        for page in pages:
            try:
                text = page.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                text = ""
            if is_redirect_page(text):
                continue
            title = page_title(page)
            if title:
                entries.append((title, quote(page.relative_to(ROOT).as_posix())))
        if not entries:
            continue
        sections.append((directory.name, entries))
    return sections


def render(sections: list[tuple[str, list[tuple[str, str]]]]) -> str:
    total = sum(len(entries) for _, entries in sections)
    cards = []
    for name, entries in sections:
        items = "\n".join(
            f'          <li><a href="{url}"><span class="dot"></span>{html.escape(title)}</a></li>'
            for title, url in entries
        )
        cards.append(
            f"""        <section class="card">
          <h2>{html.escape(name)}<span class="count">{len(entries)} 页</span></h2>
          <ul>
{items}
          </ul>
        </section>"""
        )
    cards_html = "\n".join(cards)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(SITE_TITLE)}</title>
<style>
  :root {{
    --bg: #f7f8fa;
    --surface: #ffffff;
    --text: #1d1d1f;
    --muted: #6e6e73;
    --line: #e5e5ea;
    --blue: #185fa5;
    --blue-soft: #e6f1fb;
    --radius: 14px;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif;
    font-size: 15px;
    line-height: 1.6;
  }}
  .wrap {{ max-width: 880px; margin: 0 auto; padding: 48px 24px 80px; }}
  header {{ margin-bottom: 32px; }}
  .eyebrow {{
    display: inline-block;
    font-size: 12px;
    color: var(--blue);
    background: var(--blue-soft);
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 14px;
  }}
  h1 {{ font-size: 32px; margin: 0 0 10px; letter-spacing: -.02em; }}
  .lead {{ color: var(--muted); margin: 0; }}
  .stats {{ font-size: 13px; color: var(--muted); margin-top: 14px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 20px 22px;
  }}
  .card h2 {{
    font-size: 16px;
    margin: 0 0 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .count {{ font-size: 12px; font-weight: 400; color: var(--muted); }}
  ul {{ list-style: none; margin: 0; padding: 0; }}
  li {{ margin-bottom: 8px; }}
  li:last-child {{ margin-bottom: 0; }}
  a {{
    color: var(--text);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 8px;
  }}
  a:hover {{ background: var(--blue-soft); color: var(--blue); }}
  .dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--blue); flex: none; }}
  footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line); font-size: 12px; color: var(--muted); }}
  @media (max-width: 600px) {{
    .wrap {{ padding: 28px 16px 60px; }}
    h1 {{ font-size: 26px; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="eyebrow">站点目录</span>
    <h1>{html.escape(SITE_TITLE)}</h1>
    <p class="lead">{html.escape(SITE_DESC)}</p>
    <p class="stats">共 {len(sections)} 个分类 · {total} 个页面 · 更新于 {date.today().isoformat()}</p>
  </header>

  <div class="grid">
{cards_html}
  </div>

  <footer>本页面由 generate_index.py 自动生成，请勿手动编辑；新增页面后重新运行脚本即可更新目录。</footer>
</div>
</body>
</html>
"""


def main() -> None:
    sections = build_sections()
    output = ROOT / "index.html"
    output.write_text(render(sections), encoding="utf-8")
    total = sum(len(entries) for _, entries in sections)
    print(f"已生成 {output.name}：{len(sections)} 个分类，{total} 个页面")
    for name, entries in sections:
        print(f"  - {name}: {len(entries)} 页")


if __name__ == "__main__":
    main()
