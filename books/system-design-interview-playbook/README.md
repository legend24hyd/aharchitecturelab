# System Design Interview Playbook

**Author:** Abdul Hussain, Enterprise Architect  
**Status:** Writing  
**Version:** 1.0

A Markdown-first manuscript for a system design interview book, with Draw.io and Mermaid diagrams, Git version control, and an EPUB build aimed at Kindle and other ebook stores.

## Quick start

From this directory:

```bash
python3 tools/build.py html    # browser preview → _build/preview.html
python3 tools/build.py epub    # Kindle-ready EPUB → _build/*.epub
python3 tools/build.py lint    # check chapter paths
```

Or `make html` / `make epub` / `make lint`.

Install build tools once (Pandoc required for EPUB; Node required to render Mermaid to SVG):

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y pandoc
# Mermaid CLI (optional but needed for diagram images in EPUB)
npm install --prefix tools @mermaid-js/mermaid-cli
```

VS Code: accept the recommended extensions (Draw.io, Mermaid preview, Markdown).

## Layout

```text
book.yaml                 # metadata + chapter order
manuscript/               # the book
diagrams/drawio/          # architecture diagrams
diagrams/mermaid/         # optional standalone .mmd
assets/cover/             # cover art
styles/epub.css           # Kindle/EPUB typography
tools/build.py            # compiler
```

Authoring conventions: [AUTHORING.md](AUTHORING.md)  
Store upload: [PUBLISHING.md](PUBLISHING.md)

## Current outline

1. How system design interviews work  
2. The playbook (worked method)  
3. Requirements and scope  
4. Back-of-the-envelope estimates  
5. APIs and data models  
6. Load balancing and traffic  
7. Caching  
8. Databases and storage  
9. Messaging and async  
10. Reliability and consistency  
11. Problem: URL shortener  
12. Problem: Rate limiter  
13. Problem: News feed  
14. Problem: Chat system  
15. Problem: Unique ID generator  
16. Tradeoff narratives  
17. Deep dives and failure  
18. Closing the interview  

Chapters are stubs except **Chapter 2**, which is a writing sample that demonstrates Mermaid and Draw.io embeds.
