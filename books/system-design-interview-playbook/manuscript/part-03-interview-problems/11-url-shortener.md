---
slug: url-shortener
status: draft
---

# Problem: URL shortener

*Outline for Version 1.0 — write the full loop here. Chapter 2 already previews the redirect path.*

## Prompt

Design a URL shortening service that creates short links and redirects users to the original URL.

## Playbook hooks

Requirements, estimates, code generation, mapping store, cache on GET, 301 vs 302, click events off the hot path.

Embed the architecture from Draw.io:

![URL shortener high-level](diagrams/drawio/url-shortener-high-level.drawio.svg)

*Figure 11.1 — High-level URL shortener. Writes go to the mapping service; reads hit cache then store; clicks are asynchronous.*
