#!/usr/bin/env python3
"""Render KDP-sized front and back covers (1600 x 2560).

Publisher edition: system-design emblem and AH Architecture Lab only.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
COVER = ROOT / "assets" / "cover"
LOGO = COVER / "system-design-logo.png"

W, H = 1600, 2560
NAVY = (15, 39, 68)
GOLD = (212, 179, 106)
CREAM = (244, 241, 234)
MUTED = (201, 214, 229)
INK = (232, 236, 242)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
SANS_MED = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
SANS_SEMI = "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"

BLURB = (
    "System design interviews reward a method, not a catalog of logos. "
    "This playbook is for software engineers and architects who must design "
    "a service in forty-five minutes and still sound like they have operated one."
    "\n\n"
    "You will learn to bound the problem, size the load, draw one honest picture, "
    "and name the trade-off that holds the design together. Foundations cover "
    "requirements, capacity, scale, availability, reliability, performance, CAP, "
    "consistency, and the sentence that makes a choice defensible. Building blocks "
    "then give you caches, stores, queues, and consistent hashing. Worked problems "
    "— a URL shortener and a rate limiter — show the loop at interview speed, "
    "with original diagrams throughout."
    "\n\n"
    "Write it on the board. Defend it in the room."
)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_cover(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.Resampling.LANCZOS)
    left = (im.width - W) // 2
    top = (im.height - H) // 2
    return im.crop((left, top, left + W, top + H))


def circular_badge(src_path: Path, size: int, ring: int | None = 10) -> Image.Image:
    src = Image.open(src_path).convert("RGB")
    side = min(src.size)
    left = (src.width - side) // 2
    top = (src.height - side) // 2
    src = src.crop((left, top, left + side, top + side)).resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    badge.paste(src, (0, 0), mask)
    if not ring:
        return badge
    outer = size + ring * 2
    canvas = Image.new("RGBA", (outer, outer), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.ellipse((0, 0, outer - 1, outer - 1), fill=GOLD)
    inner = (ring - 3, ring - 3, outer - ring + 2, outer - ring + 2)
    d.ellipse(inner, fill=NAVY)
    canvas.paste(badge, (ring, ring), badge)
    return canvas


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        words = para.split()
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt: ImageFont.FreeTypeFont, fill) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, y), text, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def render_front() -> Image.Image:
    base = fit_cover(COVER / "motif-front.png")
    overlay = Image.new("RGB", (W, H), NAVY)
    base = Image.blend(base, overlay, 0.18)
    # Keep the architecture readable at the top, darken mid for type.
    veil = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(veil)
    for y in range(720, 1680):
        t = (y - 720) / 960
        vd.line([(0, y), (W, y)], fill=int(40 + 90 * t))
    for y in range(1680, H):
        vd.line([(0, y), (W, y)], fill=130)
    navy = Image.new("RGB", (W, H), NAVY)
    base = Image.composite(navy, base, veil.filter(ImageFilter.GaussianBlur(8)))

    rgba = base.convert("RGBA")
    logo = circular_badge(LOGO, 560, ring=None)
    px = (W - logo.width) // 2
    py = 1420
    rgba.paste(logo, (px, py), logo)
    img = rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    y = 720
    y += draw_centered(draw, "SYSTEM DESIGN", y, font(SERIF, 78), CREAM) + 18
    y += draw_centered(draw, "INTERVIEW", y, font(SERIF, 78), CREAM) + 18
    y += draw_centered(draw, "PLAYBOOK", y, font(SERIF, 78), GOLD) + 36
    draw.rectangle((620, y, 980, y + 3), fill=GOLD)
    y += 36
    sub = font(SANS, 28)
    for line in (
        "A structured method for designing",
        "systems under interview pressure",
    ):
        y += draw_centered(draw, line, y, sub, MUTED) + 10

    name_y = py + logo.height + 28
    draw_centered(draw, "AH Architecture Lab", name_y, font(SANS_SEMI, 36), CREAM)
    draw_centered(draw, "Version 1.0", name_y + 52, font(SANS, 24), GOLD)
    return img


def render_back() -> Image.Image:
    base = fit_cover(COVER / "motif-back.png")
    overlay = Image.new("RGB", (W, H), NAVY)
    base = Image.blend(base, overlay, 0.12)
    img = base.convert("RGB")
    draw = ImageDraw.Draw(img)

    left, right = 280, W - 140
    width = right - left
    y = 220
    y += draw_centered(draw, "SYSTEM DESIGN INTERVIEW PLAYBOOK", y, font(SANS_BOLD, 26), GOLD) + 18
    draw.rectangle((560, y, 1040, y + 2), fill=GOLD)
    y += 48
    draw.text((left, y), "ABOUT THIS BOOK", font=font(SANS_SEMI, 22), fill=GOLD)
    y += 48
    body = font(SANS, 28)
    for line in wrap(draw, BLURB, body, width):
        if line == "":
            y += 22
            continue
        draw.text((left, y), line, font=body, fill=INK)
        y += 40

    y += 36
    draw.rectangle((left, y, right, y + 2), fill=GOLD)
    y += 56

    logo = circular_badge(LOGO, 360, ring=None)
    img_rgba = img.convert("RGBA")
    lx = (W - logo.width) // 2
    img_rgba.paste(logo, (lx, y), logo)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    draw_centered(draw, "AH Architecture Lab", y + logo.height + 28, font(SANS_SEMI, 32), CREAM)
    draw_centered(draw, "Version 1.0", y + logo.height + 76, font(SANS, 22), GOLD)
    return img


def main() -> None:
    front = render_front()
    back = render_back()
    front_path = COVER / "cover-front.jpg"
    back_path = COVER / "cover-back.jpg"
    front.save(front_path, "JPEG", quality=92, optimize=True)
    back.save(back_path, "JPEG", quality=92, optimize=True)
    print(front_path)
    print(back_path)


if __name__ == "__main__":
    main()
