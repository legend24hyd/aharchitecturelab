#!/usr/bin/env python3
"""Compile the Markdown manuscript to HTML, EPUB, DOCX, and PDF."""

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

DEFAULT_HEADINGS = [
    "Learning Objectives",
    "Quote",
    "Introduction",
    "Core Concepts",
    "Architecture Diagram",
    "Real-world Example",
    "Enterprise Insight",
    "Interviewer's Mind",
    "AI Perspective",
    "Common Mistakes",
    "Best Practices",
    "Summary",
    "Key Takeaways",
    "Interview Questions",
    "Further Reading",
]

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def book_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_book(root: Path) -> dict:
    path = root / "book.yaml"
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    return parse_book_yaml_lite(text)


def parse_book_yaml_lite(text: str) -> dict:
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
        if stripped.startswith("- ") and stripped.endswith(".md"):
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
        items.append(("frontmatter", path))
    for part in book.get("parts") or []:
        title = part.get("title") or "Part"
        for path in part.get("chapters") or []:
            items.append((title, path))
    for path in book.get("backmatter") or []:
        items.append(("backmatter", path))
    return items


def chapter_files(book: dict) -> list[str]:
    files: list[str] = []
    for part in book.get("parts") or []:
        files.extend(part.get("chapters") or [])
    return files


def lint(root: Path, book: dict) -> int:
    missing = []
    heading_errors = []
    required = list(book.get("required_headings") or DEFAULT_HEADINGS)
    for _, rel in ordered_files(book):
        if not (root / rel).is_file():
            missing.append(rel)
    cover = book.get("cover_image")
    if cover and not (root / cover).is_file():
        missing.append(str(cover))
    for rel in chapter_files(book):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        found = [m.group(1).strip() for m in HEADING_RE.finditer(text)]
        for heading in required:
            if heading not in found:
                heading_errors.append(f"{rel}: missing ## {heading}")
    if missing or heading_errors:
        if missing:
            print("Missing files:")
            for item in missing:
                print(f"  - {item}")
        if heading_errors:
            print("Chapter structure:")
            for item in heading_errors:
                print(f"  - {item}")
        return 1
    print(
        f"OK — {len(ordered_files(book))} manuscript files, "
        f"{len(chapter_files(book))} chapters with required headings, "
        f"version {book.get('version')}, status {book.get('status')}"
    )
    return 0


def strip_yaml_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def which(name: str) -> str | None:
    return shutil.which(name)


def mermaid_cli(root: Path) -> list[str] | None:
    local = root / "tools" / "node_modules" / ".bin" / "mmdc"
    found = str(local) if local.is_file() else which("mmdc")
    if not found:
        return None
    cmd = [found]
    chrome = (
        os.environ.get("PUPPETEER_EXECUTABLE_PATH")
        or which("google-chrome")
        or which("google-chrome-stable")
        or which("chromium")
        or which("chromium-browser")
        or which("chrome")
    )
    if chrome:
        cmd.extend(["-p", str(_write_puppeteer_config(root, chrome))])
    return cmd


def _write_puppeteer_config(root: Path, chrome: str) -> Path:
    dest = root / "output" / "pdf" / "puppeteer.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        '{"executablePath": "%s", "args": ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]}\n'
        % chrome.replace("\\", "\\\\").replace('"', '\\"'),
        encoding="utf-8",
    )
    return dest


def render_mermaid_blocks(root: Path, markdown: str, stem: str) -> tuple[str, int, int]:
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
            err = getattr(exc, "stderr", "") or str(exc)
            print(f"warning: mermaid render failed for {stem}: {err[:400]}", file=sys.stderr)
            return match.group(0)
        if svg_path.is_file():
            rendered += 1
            return f"![]({rel})\n"
        skipped += 1
        return match.group(0)

    return MERMAID_FENCE.sub(repl, markdown), rendered, skipped


def assemble(root: Path, book: dict, render_mermaid: bool) -> tuple[str, int, int]:
    chunks: list[str] = []
    total_r = 0
    total_s = 0
    last_part = None
    for part, rel in ordered_files(book):
        body = strip_yaml_front_matter((root / rel).read_text(encoding="utf-8"))
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
      const blocks = document.querySelectorAll('pre.mermaid, pre.sourceCode.mermaid');
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


def pandoc_base(root: Path, book: dict, md_path: Path) -> list[str]:
    pandoc = which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc is required. Install it (e.g. sudo apt-get install -y pandoc).")
    cmd = [
        pandoc,
        str(md_path),
        "--from",
        "markdown",
        "--resource-path",
        str(root),
        "--metadata",
        f"title={book.get('title')}",
        "--metadata",
        f"author={book.get('author')}",
    ]
    return cmd


def write_assembled_md(root: Path, markdown: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    md_path = dest_dir / "book.md"
    md_path.write_text(markdown, encoding="utf-8")
    return md_path


def write_html(root: Path, book: dict, markdown: str) -> Path:
    dest = root / "output" / "html"
    md_path = write_assembled_md(root, markdown, dest)
    html_path = dest / "preview.html"
    cmd = pandoc_base(root, book, md_path) + [
        "--to",
        "html5",
        "--standalone",
        "--toc",
        "--toc-depth=2",
        "--css",
        str(root / "styles" / "epub.css"),
        "--embed-resources",
        "-o",
        str(html_path),
    ]
    subprocess.run(cmd, check=True)
    raw = html_path.read_text(encoding="utf-8")
    if "</body>" in raw:
        html_path.write_text(raw.replace("</body>", mermaid_cdn_html() + "</body>"), encoding="utf-8")
    return html_path


def write_epub(root: Path, book: dict, markdown: str) -> Path:
    dest = root / "output" / "epub"
    md_path = write_assembled_md(root, markdown, dest)
    epub_path = dest / "system-design-interview-playbook.epub"
    cmd = pandoc_base(root, book, md_path) + [
        "--to",
        "epub3",
        "--toc",
        "--toc-depth=2",
        "--split-level=1",
        "--css",
        str(root / "styles" / "epub.css"),
        "--metadata",
        f"lang={book.get('language', 'en-US')}",
        "--metadata",
        f"rights={book.get('rights', '')}",
        "--metadata",
        f"description={(book.get('description') or '').strip()}",
        "--metadata",
        f"identifier={book.get('identifier')}",
        "-o",
        str(epub_path),
    ]
    cover = book.get("cover_image")
    if cover and (root / cover).is_file():
        cmd.extend(["--epub-cover-image", str(root / cover)])
    subprocess.run(cmd, check=True)
    return epub_path


def write_docx(root: Path, book: dict, markdown: str) -> Path:
    dest = root / "output" / "docx"
    md_path = write_assembled_md(root, markdown, dest)
    docx_path = dest / "system-design-interview-playbook.docx"
    cmd = pandoc_base(root, book, md_path) + ["--to", "docx", "-o", str(docx_path)]
    subprocess.run(cmd, check=True)
    return docx_path


def write_pdf(root: Path, book: dict, markdown: str) -> Path:
    dest = root / "output" / "pdf"
    dest.mkdir(parents=True, exist_ok=True)
    md_path = write_assembled_md(root, markdown, dest)
    pdf_path = dest / "system-design-interview-playbook.pdf"
    html_path = dest / "print.html"
    css = root / "styles" / "pdf.css"
    front = dest / "cover-front.html"
    back = dest / "cover-back.html"
    front.write_text(_cover_fragment(root, book.get("cover_image") or "assets/cover/cover-front.jpg", "Front cover"), encoding="utf-8")
    back.write_text(_cover_fragment(root, "assets/cover/cover-back.jpg", "Back cover"), encoding="utf-8")

    cmd = pandoc_base(root, book, md_path) + [
        "--to",
        "html5",
        "--standalone",
        "--toc",
        "--toc-depth=1",
        "--css",
        str(css),
        "--embed-resources",
        "--include-before-body",
        str(front),
        "--include-after-body",
        str(back),
        "-o",
        str(html_path),
    ]
    subprocess.run(cmd, check=True)

    last_err: object | None = None
    weasy_cmds = []
    if which("weasyprint"):
        weasy_cmds.append([which("weasyprint"), str(html_path), str(pdf_path)])
    weasy_cmds.append([sys.executable, "-m", "weasyprint", str(html_path), str(pdf_path)])
    for wcmd in weasy_cmds:
        try:
            subprocess.run(wcmd, check=True, capture_output=True, text=True)
            if pdf_path.is_file() and pdf_path.stat().st_size >= 1000:
                _copy_pdf_to_workspace(root, pdf_path)
                return pdf_path
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            last_err = exc

    engines = ["xelatex", "pdflatex", "lualatex", "wkhtmltopdf"]
    for engine in engines:
        if not which(engine):
            continue
        cmd = pandoc_base(root, book, md_path) + [
            "--to",
            "pdf",
            "--pdf-engine",
            engine,
            "-o",
            str(pdf_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if pdf_path.is_file() and pdf_path.stat().st_size >= 1000:
                _copy_pdf_to_workspace(root, pdf_path)
            return pdf_path
        except subprocess.CalledProcessError as exc:
            last_err = exc
    raise SystemExit(
        "PDF engine not available (install weasyprint: pip install -r tools/requirements.txt). "
        f"Last error: {last_err}"
    )


def _copy_pdf_to_workspace(root: Path, pdf_path: Path) -> None:
    """Also write the PDF at the repo root so it is easy to find."""
    dest = root.parent / "system-design-interview-playbook.pdf"
    shutil.copy2(pdf_path, dest)


def _cover_fragment(root: Path, rel: str, alt: str) -> str:
    path = root / rel
    src = path.resolve().as_uri() if path.is_file() else rel
    return (
        f'<section class="cover-page"><img src="{src}" alt="{alt}" /></section>\n'
    )


def check_tools(root: Path) -> int:
    print(f"python: {sys.executable}")
    print(f"pandoc: {which('pandoc') or 'NOT FOUND'}")
    print(f"mermaid-cli: {mermaid_cli(root) or 'NOT FOUND'}")
    print(f"pyyaml: {'yes' if yaml else 'no'}")
    try:
        import weasyprint as _weasy

        print(f"weasyprint: {_weasy.__version__}")
    except ImportError:
        print(f"weasyprint: {which('weasyprint') or 'not found'}")
    for engine in ("xelatex", "pdflatex", "wkhtmltopdf"):
        print(f"{engine}: {which(engine) or 'not found'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["html", "epub", "docx", "pdf", "lint", "check-tools", "markdown", "all"],
    )
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
    commands = ["html", "epub", "docx"] if args.command == "all" else [args.command]
    if args.command == "all":
        md_plain, _, _ = assemble(root, book, render_mermaid=False)
        md_epub, r, s = assemble(root, book, render_mermaid=render)
        print(write_html(root, book, md_plain))
        print(write_epub(root, book, md_epub), f"(mermaid rendered={r}, source={s})")
        print(write_docx(root, book, md_plain))
        try:
            print(write_pdf(root, book, md_epub))
        except SystemExit as exc:
            print(f"pdf skipped: {exc}", file=sys.stderr)
        return 0
    if args.command in {"html", "markdown", "docx"}:
        md, _, _ = assemble(root, book, render_mermaid=False)
        if args.command == "markdown":
            path = write_assembled_md(root, md, root / "output" / "html")
            print(path)
            return 0
        if args.command == "html":
            print(f"Wrote {write_html(root, book, md)} (mermaid in-browser)")
            return 0
        print(f"Wrote {write_docx(root, book, md)}")
        return 0
    if args.command in {"epub", "pdf"}:
        md, r, s = assemble(root, book, render_mermaid=render)
        if args.command == "epub":
            print(f"Wrote {write_epub(root, book, md)} (mermaid rendered={r}, source={s})")
            return 0
        print(f"Wrote {write_pdf(root, book, md)} (mermaid rendered={r}, source={s})")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
