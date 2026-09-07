# Publishing guide

Target stores after Version 1.0 manuscript freeze: **Kindle (KDP)**, Apple Books, Kobo, Google Play Books. All of them take a well-formed **EPUB 3** file. That EPUB is the artifact this repo builds.

## What we produce

| Artifact | Command | Use |
| --- | --- | --- |
| HTML preview | `make html` | Proof chapters and diagrams in a browser |
| EPUB 3 | `make epub` | Kindle Direct Publishing and other stores |
| Chapter list check | `make lint` | Confirms every path in `book.yaml` exists |

Amazon no longer requires `.mobi`. Upload the EPUB. Convert to Kindle Package Format (KPF) only if you use **Kindle Previewer** locally for a final visual pass.

## Kindle Direct Publishing (KDP)

1. Freeze `book.yaml` `status` to `Copyedit` then `Production`.
2. `make epub` and open `_build/system-design-interview-playbook.epub`.
3. Replace `assets/cover/cover.svg` with a **print-quality cover**:
   - KDP ebook cover: JPEG or TIFF, RGB, recommended **1600 × 2560** or similar 1:1.6 portrait.
   - Do not rely on the placeholder SVG in the store listing; upload a dedicated cover in KDP.
4. In [KDP](https://kdp.amazon.com): New title → Kindle eBook → upload EPUB.
5. Preview with KDP Online Previewer **and** Kindle Previewer (phone, tablet, e-ink).
6. Fill metadata to match `book.yaml`: title, author **Abdul Hussain**, description, keywords (system design, software architecture, interviews).
7. Choose territories, pricing, KDP Select if you want Kindle Unlimited exclusivity.

### Kindle layout constraints

- No JavaScript. Mermaid **must** be pre-rendered images (the build does this).
- Avoid nested tables, `position: absolute`, and columns.
- Test every architecture diagram on a phone-width preview.
- Use real Unicode; do not paste screenshots of equations.

## Other ebook stores

The same EPUB is the source file:

- **Apple Books** — Apple Books for Authors or Aggregator.
- **Kobo Writing Life** — upload EPUB.
- **Google Play Books Partner Center** — upload EPUB.
- **Draft2Digital / Smashwords** — optional aggregators if you do not want to upload store-by-store.

Always validate with [EPUBCheck](https://github.com/w3c/epubcheck) before a store upload:

```bash
make epubcheck   # if Java and epubcheck are installed
```

## ISBN and legal

- Kindle does not require an ISBN; Apple/Kobo often want one. Buy ISBNs in your publishing country if you want store-independent identity.
- Keep copyright in `manuscript/frontmatter/01-copyright.md` in sync with the year of first publication.
- Do not paste vendor copyrighted interview questions verbatim. Use original prompts.

## Release checklist (Version 1.0)

- [ ] All chapter `status` values are `done`
- [ ] Every figure has a caption and readable labels on a 6-inch screen
- [ ] `make html` and `make epub` succeed in CI
- [ ] EPUBCheck reports no errors
- [ ] Kindle Previewer pass (reflow + tables + diagrams)
- [ ] Cover, description, and author bio match the manuscript
- [ ] Git tag `playbook-v1.0.0`
