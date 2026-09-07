# AH Architecture Lab

Writing lab for technical books by **Abdul Hussain** (Enterprise Architect).

Manuscripts live in Git as Markdown so chapters, diagrams, and ebook builds stay versioned together.

## Books

| Book | Status | Version | Path |
| --- | --- | --- | --- |
| *System Design Interview Playbook* | Writing | 1.0 | [`books/system-design-interview-playbook`](books/system-design-interview-playbook) |

## How this repo is organized

```text
books/<book-slug>/
  book.yaml              # title, author, status, chapter order
  manuscript/            # Markdown chapters
  diagrams/drawio/       # Editable diagrams.net / Draw.io sources
  diagrams/mermaid/      # Optional standalone .mmd files
  styles/                # EPUB/Kindle CSS
  tools/                 # Build scripts
```

## Diagrams

- **Mermaid** — sequence, flow, and state diagrams written in Markdown (rendered at ebook build time).
- **Draw.io** — architecture diagrams stored as `.drawio` and `.drawio.svg` so they stay editable *and* publishable.

See the book’s [AUTHORING.md](books/system-design-interview-playbook/AUTHORING.md) for conventions and [PUBLISHING.md](books/system-design-interview-playbook/PUBLISHING.md) for Kindle and other stores.
