#!/usr/bin/env python3
"""Compile the Markdown manuscript to HTML preview and EPUB."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

MERMAID_FENCE = re.compile(
    r"```mermaid[ \t]*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def book_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_book(root: Path) -> dict:
    path = root / "book.yaml"
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    return parse_book_yaml_lite(text)


def parse_book_yaml_lite(text: str) -> dict:
    """Minimal parser so lint/html work without PyYAML."""
    data: dict = {"frontmatter": [], "backmatter": [], "parts": []}
    current_part: dict | None = None
    current_list: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^[a-zA-Z_][\w]*:", line) and not line.startswith(" "):
            key, _, val = line.partition(":")
            val = val.strip().strip('"')
            current_part = None
            if key == "frontmatter":
                current_list = "frontmatter"
            elif key == "backmatter":
                current_list = "backmatter"
            elif key == "parts":
                current_list = "parts"
            else:
                current_list = None
                if val and val != ">":
                    data[key] = val
            continue
        stripped = line.strip()
        if stripped.startswith("- title:"):
            title = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            current_part = {"title": title, "chapters": []}
            data["parts"].append(current_part)
            current_list = "part-chapters"
            continue
        if stripped == "chapters:":
            current_list = "part-chapters"
            continue
        if stripped.startswith("- manuscript/"):
            item = stripped[2:].strip()
            if current_list == "frontmatter":
                data["frontmatter"].append(item)
            elif current_list == "backmatter":
                data["backmatter"].append(item)
            elif current_list == "part-chapters" and current_part is not None:
                current_part["chapters"].append(item)
    return data


def ordered_files(book: dict) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for path in book.get("frontmatter") or []:
        items.append (("frontmatter", path))
    for part in book.get("parts") or []:
        title = part.get("title") or "Part"
        for path in part.get("chapters") or []:
            items.append((title, path))
    for path in book.get("backmatter") or []:
        items.append(("backmatter", path))
    return items


def lint(root: Path, book: dict) -> int:
    missing = []
    for _, rel in ordered_files(book):
        if not (root / rel).is_file():
            missing.append(rel)
    cover = book.get("cover_image")
    if cover and not (root / cover).is_file():
        missing.append(str(cover))
    if missing:
        print("Missing files:")
        for item in missing:
            print(f"  - {item}")
        return 1
    print(f"OK — {len(ordered_files(book))} manuscript files, version {book.get('version')}, status {book.get('status')}")
    return 0


def strip_yaml_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            rest = text[end + 4 :]
            return rest.lstrip("\n")
    return text


def which(name: str) -> str | None:
    return shutil.which(name)


def mermaid_cli(root: Path) -> list[str] | None:
    local = root / "tools" / "node_modules" / ".bin" / "mmdc"
    if local.is_file():
        return [str(local)]
    found = which("mmdc")
    if found:
        return [found]
    npx = which("npx")
    if npx:
        return [npx, "--yes", "@mermaid-js/mermaid-cli", "mmdc"]
    return None


def render_mermaid_blocks(root: Path, markdown: str, stem: str) -> tuple[str, int, int]:
    """Replace ```mermaid fences with image links. Returns text, rendered, skipped."""
    out_dir = root / "diagrams" / "exported" / "mermaid"
    out_dir.mkdir(parents=True, exist_ok=True)
    cli = mermaid_cli(root)
    rendered = 0
    skipped = 0

    def repl(match: re.Match) -> str:
        nonlocal rendered, skipped
        source = match.group(1).strip() + "\n"
        digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
        svg_name = f"{stem}-{digest}.svg"
        svg_path = out_dir / svg_name
        mmd_path = out_dir / f"{stem}-{digest}.mmd"
        mmd_path.write_text(source, encoding="utf-8")
        rel = f"diagrams/exported/mermaid/{svg_name}"
        if svg_path.is_file() and svg_path.stat().st_size > 0:
            rendered += 1
            return f"![]({rel})\n"
        if not cli:
            skipped += 1
            return match.group(0)
        cmd = cli + ["-i", str(mmd_path), "-o", str(svg_path), "-b", "white"]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            skipped += 1
            print(f"warning: mermaid render failed for {stem}: {exc}", file=sys.stderr)
            return match.group(0)
        if svg_path.is_file():
            rendered += 1
            return f"![]({rel})\n"
        skipped += 1
        return match.group(0)

    new_text = MERMAID_FENCE.sub(repl, markdown)
    return new_text, rendered, skipped


def assemble(root: Path, book: dict, render_mermaid: bool) -> tuple[str, int, int]:
    chunks: list[str] = []
    total_r = 0
    total_s = 0
    last_part = None
    for part, rel in ordered_files(book):
        path = root / rel
        body = strip_yaml_front_matter(path.read_text(encoding="utf-8"))
        stem = Path(rel).stem
        if render_mermaid:
            body, r, s = render_mermaid_blocks(root, body, stem)
            total_r += r
            total_s += s
        if part not in {"frontmatter", "backmatter"} and part != last_part:
            chunks.append(f"# {part}\n")
            last_part = part
        chunks.append(body.rstrip() + "\n")
    return "\n\n".join(chunks) + "\n", total_r, total_s


def mermaid_cdn_html() -> str:
    return """<script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
      const blocks = document.querySelectorAll('pre.mermaid, pre.sourceCode.mermaid, code.language-mermaid');
      let i = 0;
      for (const el of blocks) {
        const src = el.textContent;
        const host = el.closest('pre') || el;
        const div = document.createElement('div');
        div.className = 'mermaid';
        const id = 'mmd-' + (i++);
        const { svg } = await mermaid.render(id, src);
        div.innerHTML = svg;
        host.replaceWith(div);
      }
    </script>
"""


def write_html(root: Path, book: dict, markdown: str, build_dir: Path) -> Path:
    build_dir.mkdir(parents=True, exist_ok=True)
    md_path = build_dir / "book.md"
    md_path.write_text(markdown, encoding="utf-8")
    html_path = build_dir / "preview.html"
    pandoc = which("pandoc")
    title = book.get("title", "Book")
    if pandoc:
        cmd = [
            pandoc,
            str(md_path),
            "--from",
            "markdown",
            "--to",
            "html5",
            "--standalone",
            "--toc",
            "--toc-depth=2",
            "--css",
            str(root / "styles" / "epub.css"),
            "--resource-path",
            str(root),
            "--metadata",
            f"title={title}",
            "--metadata",
            f"author={book.get('author', '')}",
            "-o",
            str(html_path),
        ]
        subprocess.run(cmd, check=True)
        raw = html_path.read_text(encoding="utf-8")
        if "</body>" in raw:
            raw = raw.replace("</body>", mermaid_cdn_html() + "</body>")
            html_path.write_text(raw, encoding="utf-8")
    else:
        escaped = (
            markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        html_path.write_text(
            f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" href="../styles/epub.css"/>
</head>
<body>
<h1>{title}</h1>
<p>{book.get('author', '')} — {book.get('author_role', '')}</p>
<pre class="manuscript">{escaped}</pre>
{mermaid_cdn_html()}
</body>
</html>
""",
            encoding="utf-8",
        )
    return html_path


def write_epub(root: Path, book: dict, markdown: str, build_dir: Path) -> Path:
    pandoc = which("pandoc")
    if not pandoc:
        raise SystemExit(
            "pandoc is required for EPUB. Install it (e.g. sudo apt-get install -y pandoc)."
        )
    build_dir.mkdir(parents=True, exist_ok=True)
    md_path = build_dir / "book.md"
    md_path.write_text(markdown, encoding="utf-8")
    slug = "system-design-interview-playbook"
    epub_path = build_dir / f"{slug}.epub"
    cmd = [
        pandoc,
        str(md_path),
        "--from",
        "markdown",
        "--to",
        "epub3",
        "--toc",
        "--toc-depth=2",
        "--split-level=1",
        "--css",
        str(root / "styles" / "epub.css"),
        "--resource-path",
        str(root),
        "--metadata",
        f"title={book.get('title')}",
        "--metadata",
        f"author={book.get('author')}",
        "--metadata",
        f"lang={book.get('language', 'en-US')}",
        "--metadata",
        f"rights={book.get('rights', '')}",
        "--metadata",
        f"description={book.get('description', '').strip()}",
        "--metadata",
        f"identifier={book.get('identifier', slug)}",
        "-o",
        str(epub_path),
    ]
    cover = book.get("cover_image")
    if cover and (root / cover).is_file():
        cmd.extend(["--epub-cover-image", str(root / cover)])
    subprocess.run(cmd, check=True)
    return epub_path


def check_tools(root: Path) -> int:
    print(f"python: {sys.executable}")
    print(f"pandoc: {which('pandoc') or 'NOT FOUND (needed for EPUB)'}")
    cli = mermaid_cli(root)
    print(f"mermaid-cli: {' '.join(cli) if cli else 'NOT FOUND (EPUB will keep mermaid as source; HTML preview still works)'}")
    print(f"pyyaml: {'yes' if yaml else 'no (lite parser in use)'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["html", "epub", "lint", "check-tools", "markdown"])
    parser.add_argument("--no-render-mermaid", action="store_true")
    args = parser.parse_args()
    root = book_root()
    os.chdir(root)
    book = load_book(root)
    if args.command == "lint":
        return lint(root, book)
    if args.command == "check-tools":
        return check_tools(root)
    render = not args.no_render_mermaid
    if args.command in {"html", "markdown"}:
        # HTML can render mermaid in-browser; skip CLI unless we want images.
        md, r, s = assemble(root, book, render_mermaid=False)
        if args.command == "markdown":
            out = root / "_build" / "book.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf-8")
            print(out)
            return 0
        path = write_html(root, book, md, root / "_build")
        print(f"Wrote {path} (mermaid in-browser)")
        return 0
    if args.command == "epub":
        md, r, s = assemble(root, book, render_mermaid=render)
        path = write_epub(root, book, md, root / "_build")
        print(f"Wrote {path} (mermaid rendered={r}, left as source={s})")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
