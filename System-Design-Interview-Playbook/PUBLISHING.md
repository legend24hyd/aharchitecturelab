# Publishing guide

Target stores after Version 1.0 freeze: **Kindle (KDP)**, Apple Books, Kobo, Google Play Books. The artifact is **EPUB 3** from `output/epub/`.

## Commands

```bash
python3 tools/build.py epub   # output/epub/system-design-interview-playbook.epub
python3 tools/build.py docx   # editorial markup in Word
python3 tools/build.py pdf    # optional; needs xelatex, wkhtmltopdf, or weasyprint
```

Amazon no longer requires `.mobi`. Upload the EPUB. Use Kindle Previewer locally if you want a KPF visual pass.

## KDP

1. Freeze `book.yaml` status through Copyedit then Production.
2. Replace `assets/cover/cover.svg` with a **1600 × 2560** (or similar 1:1.6) RGB JPEG for the store listing.
3. Upload EPUB in KDP. Preview on phone, tablet, and e-ink.
4. Metadata: title, author **Abdul Hussain**, keywords around system design and interviews.

Mermaid must be images in the EPUB (install `mmdc` if you want automatic SVG). Draw.io already ships as SVG.

## Other stores

Same EPUB: Apple Books, Kobo Writing Life, Google Play Books Partner Center, or an aggregator.

## Release checklist

- [ ] Every chapter heading lint is clean (`python3 tools/build.py lint`)
- [ ] Figures readable on a 6-inch screen
- [ ] EPUBCheck clean
- [ ] Cover, description, and bio match the manuscript
- [ ] Git tag `playbook-v1.0.0`
