# Publishing guide

Target stores after Version 1.0 freeze: **Kindle (KDP)**, Apple Books, Kobo, Google Play Books. The artifact is **EPUB 3** from `output/epub/`.

## Commands

```bash
python3 tools/build.py epub   # output/epub/system-design-interview-playbook.epub
python3 tools/build.py docx   # editorial markup in Word
python3 tools/build.py pdf    # output/pdf/*.pdf (WeasyPrint + mermaid-cli; 6 x 9.6 in)
```

Amazon no longer requires `.mobi`. Upload the EPUB. Use Kindle Previewer locally if you want a KPF visual pass.

## KDP

1. Freeze `book.yaml` status through Copyedit then Production.
2. Store listing and EPUB/PDF covers: `assets/cover/cover-front.jpg` and `cover-back.jpg` (1600 × 2560). Publisher mark is AH Architecture Lab plus the architecture emblem — no author photo or byline on the jackets. Rebuild with `python3 tools/render_covers.py`. Drop ISBN/barcode onto the back in a later pass.
3. Upload EPUB in KDP. Preview on phone, tablet, and e-ink.
4. Metadata: title, publisher **AH Architecture Lab**, keywords around system design and interviews.

## PDF

Digital PDF is 6 × 9.6 inches (same ratio as the KDP cover). Front and back covers are the first and last pages.

```bash
pip install -r tools/requirements.txt          # WeasyPrint
PUPPETEER_SKIP_DOWNLOAD=true npm install --prefix tools   # mermaid-cli
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome   # or chromium
python3 tools/build.py pdf
```

The compiler writes `output/pdf/system-design-interview-playbook.pdf` and copies it to the repo root as `system-design-interview-playbook.pdf`. CI also uploads that file as an artifact.

Mermaid diagrams are exported as **PNG** (not SVG) so PDF engines keep node labels. WeasyPrint does not paint HTML inside SVG `foreignObject`.

## Other stores

Same EPUB: Apple Books, Kobo Writing Life, Google Play Books Partner Center, or an aggregator.

## Release checklist

- [ ] Every chapter heading lint is clean (`python3 tools/build.py lint`)
- [ ] Figures readable on a 6-inch screen
- [ ] EPUBCheck clean
- [ ] Cover, description, and bio match the manuscript
- [ ] Git tag `playbook-v1.0.0`
