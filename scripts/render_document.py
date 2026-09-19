"""Render course Markdown as standalone, navigable HTML documents."""

import argparse
import re
from html import escape
from pathlib import Path

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v0.4"
SOURCE = ROOT / "docs" / f"培养目标与能力标准-{VERSION}.md"

STYLE = """
:root { color-scheme: light; --ink: #1d2b36; --muted: #5c6f79;
  --accent: #176b70; --border: #dce5e7; --paper: #fff; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 24px; }
body { margin: 0; background: #f2f5f5; color: var(--ink);
  font-family: "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: 16px; line-height: 1.85; }
a { color: var(--accent); text-underline-offset: 3px; overflow-wrap: anywhere; }
.layout { max-width: 1440px; margin: auto; display: grid;
  grid-template-columns: 280px minmax(0, 1fr); gap: 28px; padding: 28px; }
nav { position: sticky; top: 24px; height: calc(100vh - 48px); overflow-y: auto;
  padding: 10px 16px 24px 0; font-size: 13px; }
.eyebrow { color: var(--accent); font-size: 12px; letter-spacing: .12em; }
.nav-title { font-size: 19px; font-weight: 700; line-height: 1.6; margin: 8px 0; }
.nav-meta { color: var(--muted); font-size: 12px; margin: 8px 0 20px; }
nav ul { list-style: none; padding: 0; margin: 0; }
nav li { margin: 0 0 4px; }
nav a { display: block; padding: 6px 8px; border-radius: 6px;
  text-decoration: none; color: var(--muted); }
nav a:hover, nav a:focus { background: #e1ecec; color: var(--accent); }
.nav-sub { padding-left: 12px; font-size: 12px; }
.actions { display: flex; align-items: center; flex-wrap: wrap; gap: 10px;
  margin: 0 0 20px; }
.actions a, button { border: 1px solid var(--border); border-radius: 6px;
  padding: 5px 10px; background: white; color: var(--accent); font: inherit;
  font-size: 12px; cursor: pointer; text-decoration: none; }
main { min-width: 0; background: var(--paper); padding: 48px 56px;
  border: 1px solid var(--border); border-radius: 10px;
  box-shadow: 0 4px 24px #16383a05; }
h1 { font-size: 29px; line-height: 1.5; letter-spacing: -.015em; margin: 0 0 24px; }
h2 { font-size: 23px; line-height: 1.55; margin: 56px 0 22px;
  padding-top: 18px; border-top: 2px solid #d5e7e6; }
h3 { font-size: 18px; line-height: 1.6; margin: 30px 0 14px; }
p { margin: 14px 0; }
strong { color: #143d44; }
li { margin: 7px 0; }
blockquote { margin: 24px 0; padding: 6px 20px; background: #eff7f6;
  border-left: 4px solid var(--accent); }
.table-wrap { overflow-x: auto; margin: 22px 0; }
table { border-collapse: collapse; width: 100%; font-size: 13px; line-height: 1.75; }
th, td { text-align: left; vertical-align: top; padding: 11px 12px;
  border: 1px solid var(--border); min-width: 100px; }
th { background: #edf5f4; color: #204f55; font-weight: 700; }
tbody tr:nth-child(even) { background: #fafcfc; }
code { font-family: "Cascadia Code", "Noto Sans Mono CJK SC", monospace;
  font-size: .88em; background: #eef2f3; padding: 2px 5px; border-radius: 3px; }
pre { overflow-x: auto; border-radius: 7px; background: #edf2f4;
  border: 1px solid var(--border); padding: 18px; line-height: 1.7; }
pre code { padding: 0; background: none; }
.footer { margin-top: 44px; padding-top: 18px; border-top: 1px solid var(--border);
  font-size: 12px; color: var(--muted); }
@media (max-width: 1000px) {
  .layout { grid-template-columns: 220px minmax(0, 1fr); gap: 16px; padding: 16px; }
  main { padding: 32px 28px; }
}
@media (max-width: 720px) {
  .layout { display: block; padding: 12px; }
  nav { position: static; height: auto; max-height: 320px; margin-bottom: 20px; }
  main { padding: 28px 20px; } h1 { font-size: 24px; } h2 { font-size: 21px; }
}
@media print {
  html { scroll-behavior: auto; }
  @page { size: A4; margin: 18mm 15mm; }
  body { background: white; font-size: 10pt; line-height: 1.7; }
  .layout { display: block; padding: 0; } nav, .actions { display: none; }
  main { border: 0; padding: 0; box-shadow: none; }
  h1 { font-size: 21pt; } h2 { font-size: 15pt; margin-top: 28px; }
  h3 { font-size: 12pt; } h1, h2, h3 { break-after: avoid; }
  p { orphans: 3; widows: 3; }
  .table-wrap { overflow: visible; } table { font-size: 8pt; }
  th, td { min-width: 0; padding: 6px; } tr { break-inside: avoid; }
  pre { white-space: pre-wrap; overflow: visible; font-size: 8pt; }
  a { color: #176b70; }
}
"""


def render(source):
    output = source.with_suffix(".html")
    markdown = MarkdownIt("commonmark", {"html": False}).enable("table")
    text = source.read_text(encoding="utf-8")
    heading = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), source.stem)
    title = "培养目标与能力标准" if source == SOURCE else heading
    versions = re.findall(r"v\d+\.\d+", text[:1000])
    dates = re.findall(r"20\d{2}-\d{2}-\d{2}", text[:1000])
    meta = " · ".join(([versions[0]] if versions else []) + ([dates[0]] if dates else []))
    tokens = markdown.parse(text)
    navigation = []
    heading_count = 0
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        heading_count += 1
        anchor = f"section-{heading_count}"
        token.attrSet("id", anchor)
        label = tokens[index + 1].content
        if token.tag in ("h2", "h3"):
            css_class = ' class="nav-sub"' if token.tag == "h3" else ""
            navigation.append(
                f'<li{css_class}><a href="#{anchor}">{escape(label)}</a></li>'
            )
    body = markdown.renderer.render(tokens, markdown.options, {})
    body = body.replace("<table>", '<div class="table-wrap"><table>')
    body = body.replace("</table>", "</table></div>")
    source_name = escape(source.name, quote=True)
    navigation_html = "\n".join(navigation)
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="LLM 智能体课程的培养目标、能力标准、先修关系与实验设计。">
<title>{escape(title)} · {escape(meta)}</title>
<style>{STYLE}</style>
</head>
<body>
<div class="layout">
<nav aria-label="文档目录">
<div class="eyebrow">AGENTS 万事通</div>
<div class="nav-title">{escape(title)}</div>
<div class="nav-meta">{escape(meta)}<br>研究式学习与课程筹备</div>
<div class="actions"><a href="{source_name}">Markdown 源文档</a>
<button type="button" onclick="window.print()">打印 / 保存 PDF</button></div>
<ul>{navigation_html}</ul>
</nav>
<main>
{body}
<div class="footer">本阅读版由同名 Markdown 源文档生成。实验状态以源文档标注为准；前沿资料和工具行为需按版本核验。</div>
</main>
</div>
</body>
</html>
"""
    output.write_text(document, encoding="utf-8")
    print(f"Rendered {output} ({heading_count} headings)")


def main():
    parser = argparse.ArgumentParser(description="Render course Markdown documents as offline HTML.")
    parser.add_argument("sources", nargs="*", type=Path, help="Paths relative to the project root, or absolute paths.")
    args = parser.parse_args()
    sources = [path if path.is_absolute() else ROOT / path for path in args.sources] or [SOURCE]
    for source in sources:
        if not source.is_file():
            parser.error(f"Source does not exist: {source}")
    for source in sources:
        render(source)


if __name__ == "__main__":
    main()
