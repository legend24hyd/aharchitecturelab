# System Design Interview Playbook

**Author:** Abdul Hussain, Enterprise Architect  
**Status:** Writing  
**Version:** 1.0

Markdown-first manuscript with a fixed chapter shape, Mermaid and Draw.io diagrams, and builds to EPUB, PDF, and DOCX.

## Layout

```text
System-Design-Interview-Playbook/
├── README.md
├── manuscript.md                 # master map of the book
├── frontmatter/
├── chapters/                     # one file per chapter, same section order
├── diagrams/chapterNN/           # Mermaid .mmd and Draw.io sources
├── assets/cover|author|icons|screenshots   # KDP front/back JPEGs + author photo
├── glossary/
├── appendix/
├── references/
└── output/epub|pdf|docx
```

## Chapter shape (every chapter)

Chapter Title → Learning Objectives → Quote → Introduction → Core Concepts → Architecture Diagram → Real-world Example → Enterprise Insight → Interviewer's Mind → AI Perspective → Common Mistakes → Best Practices → Summary → Key Takeaways → Interview Questions → Further Reading

## Diagrams

- **Mermaid** for request paths, sequences, and simple flows (inline in the chapter, optional `.mmd` copy under `diagrams/chapterNN/`).
- **Draw.io** for multi-layer architectures (Netflix-scale, Uber-scale, multi-region). Store `.drawio` plus `.drawio.svg`.

## Content rules

- Write from first principles, in our own words.
- Public material is a *reference for concepts*, never source text to copy.
- Ground every explanation in an engineering trade-off.
- Keep the enterprise-architect voice in **Enterprise Insight**.
- Add AI and cloud-native notes only where they change the design.

Full conventions: [STANDARDS.md](STANDARDS.md). Store upload: [PUBLISHING.md](PUBLISHING.md).

## Part I — Foundations (ten chapters)

1. Welcome to the World of System Design *(completed)*
2. Understanding requirements
3. Capacity estimation (users, QPS, storage, bandwidth, memory, growth)
4. Scalability
5. Availability
6. Reliability
7. Performance
8. CAP theorem
9. Consistency models
10. Architectural trade-offs

Then Part II (caching, storage, messaging, consistent hashing) and Part III (interview method, URL shortener, rate limiter, close).

## Build

```bash
python3 tools/build.py lint
python3 tools/build.py html    # output/html/preview.html
python3 tools/build.py epub    # output/epub/*.epub  (Kindle)
python3 tools/build.py docx    # output/docx/*.docx
python3 tools/build.py pdf     # also copies to /workspace/system-design-interview-playbook.pdf
python3 tools/render_covers.py # assets/cover/cover-front.jpg and cover-back.jpg
```
