#!/usr/bin/env python3
"""Draw the front page of Thursday 19 November 2026 in one 1024x1024 PNG.

Every story below was checked against reporting published on that day
(AP, Reuters, Just Security Early Edition, USA Today, Yahoo Finance,
SensorTower): a lead story, a world map with eight datelines, six feature
cards, fifteen one-line briefings and a midday markets strip.
Drawn entirely with Pillow; no network, no external assets, no clock:
running it twice produces byte-identical output.
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# ---- palette -------------------------------------------------------------
PAPER = (246, 241, 229)
PAGE_CARD = (255, 253, 247)
INK = (28, 28, 28)
NAVY = (20, 38, 63)
CRIMSON = (166, 30, 34)
GOLD = (185, 138, 30)
SLATE = (90, 90, 82)
RULE = (201, 191, 165)
OCEAN = (169, 198, 220)
LAND = (138, 160, 122)
LAND_EDGE = (96, 118, 84)
PIN = (178, 34, 34)

MARGIN = 30
CONTENT_W = SIDE - 2 * MARGIN

# ---- copy ----------------------------------------------------------------
LEAD = {
    "kicker": "LEAD STORY  ·  SHENZHEN, CHINA",
    "headline": "Trump, Xi and Putin meet in Shenzhen — a first three-way summit",
    "deck": "Ninety minutes at APEC on nuclear arms, Ukraine and Iran ended with a "
            "\u201cpeace declaration\u201d that named neither war — and no new arms deal.",
}

# (x, y, legend label) — pins are numbered on the map; the legend below it
# names each one. Coordinates are my own rough stylised world map.
PINS = [
    (860, 352, "SHENZHEN — summit"),
    (488, 315, "THE HAGUE — genocide ruling"),
    (622, 378, "RIYADH — missile hits tower"),
    (548, 350, "GAZA — tanks push in"),
    (588, 312, "CRIMEA — bridge hit"),
    (878, 326, "YONGBYON — enrichment grows"),
    (522, 366, "ANTALYA — COP31 draft"),
    (205, 352, "WASHINGTON — war-powers vote"),
]

CARDS = [
    ("THE HAGUE", "World Court: Myanmar committed genocide",
     "ICJ finds state-sponsored genocide of the Rohingya, 9–6 — the first "
     "ruling of its kind."),
    ("WALL STREET", "Anthropic's record $81.3bn IPO",
     "Priced at $83, opened at $111.50 on Nasdaq as ANT — the biggest "
     "stock-market listing ever."),
    ("MARKETS", "Dow drops 1,014 as the Fed turns hawkish",
     "The S&P 500 slides a sixth straight day; minutes point to more "
     "hikes ahead."),
    ("ANTALYA", "COP31 draft drops fossil fuels",
     "Slimmed text, 144 paragraphs to 80, names no fuel — but concedes "
     "1.5°C will be passed."),
    ("LOS ANGELES", "GTA 6 is out — $1.84bn day one",
     "Rockstar's launch sells 19 million-plus copies by Thursday and "
     "scores 99 on Metacritic."),
    ("GAZA", "Israeli ground push into central Gaza",
     "Tanks move past the Yellow Line near Nuseirat despite the ceasefire, "
     "after evacuation orders."),
]

BRIEFS = [
    ("TEHRAN", "Trump: U.S. to \u201csee what happens\u201d after Jan. 1."),
    ("DHAKA", "Four killed; Yunus ancestral home set ablaze."),
    ("BLACK SEA", "LPG tanker Gas Husky sinks off Bulgaria."),
    ("COPENHAGEN", "Denmark backs Greenland defence deal, 109–0."),
    ("TOKYO", "PM Takaichi talks with Putin; contact to continue."),
    ("SEOUL", "President Lee urges new dialogue with Pyongyang."),
    ("WASHINGTON", "Administration asks court to end Venezuelan TPS."),
    ("LONDON", "UK and Norway fund £100m for Ukraine naval craft."),
    ("MANILA", "White House pursues a $2bn-plus loan package."),
    ("LOS ANGELES", "Jazz end the Lakers' nine-game streak, 109–97."),
    ("MIAMI", "Heat beat Bucks 137–130; Milwaukee falls to 1–14."),
    ("LAS VEGAS", "No. 8 Houston upsets No. 1 Florida, 86–76."),
    ("NEW YORK", "MLB lockout looms as owners demand salary cap."),
    ("GENEVA", "589m children lived in conflict zones in 2025."),
    ("PORT MORESBY", "Rio Tinto pledges $250m over PNG mine damage."),
]

MARKETS = [
    "DOW 49,184  \u25bc2.0%",
    "S&P 7,208  \u25bc1.6%",
    "NASDAQ 24,054  \u25bc1.5%",
    "BTC $62,236  \u25bc2.6%",
    "VIX 28.2  \u25b214%",
    "ANT $99  (IPO $83)",
]

FOOTER = ("All events of Thursday 19 November 2026  ·  Sources: AP, Reuters, "
          "Just Security, USA Today, Yahoo Finance, SensorTower")


# ---- helpers -------------------------------------------------------------
def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, face, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    out = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=face) <= max_w:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def fit_lines(draw, text, face, max_w, max_lines):
    """Wrap to at most max_lines, trimming the last line with an ellipsis."""
    lines = wrap_text(draw, text, face, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " …", font=face) > max_w:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
    lines[-1] = (lines[-1] + " …").strip()
    return lines


def centred(draw, y, text, face, fill):
    w = draw.textlength(text, font=face)
    draw.text(((SIDE - w) / 2, y), text, font=face, fill=fill)


def section_head(draw, y, text):
    face = load(SANS_B, 14)
    draw.text((MARGIN, y), text, font=face, fill=NAVY)
    w = draw.textlength(text, font=face)
    draw.rectangle([MARGIN, y + 21, MARGIN + w, y + 24], fill=GOLD)


def draw_masthead(draw):
    draw.rectangle([0, 0, SIDE, 3], fill=NAVY)
    title = load(SERIF_B, 54)
    centred(draw, 14, "THE GLOBAL EDITION", title, NAVY)
    date_face = load(SANS_B, 20)
    centred(draw, 78, "THURSDAY,  19 NOVEMBER 2026", date_face, CRIMSON)
    tag_face = load(SANS, 13)
    centred(draw, 104, "O N E   D A Y   ·   O N E   P A G E   ·   T H E   W O R L D ' S   N E W S",
            tag_face, SLATE)
    draw.rectangle([MARGIN, 128, SIDE - MARGIN, 131], fill=NAVY)
    draw.rectangle([MARGIN, 133, SIDE - MARGIN, 134], fill=GOLD)


def draw_lead(draw):
    y = 146
    draw.rectangle([MARGIN, y, MARGIN + 5, y + 104], fill=CRIMSON)
    x = MARGIN + 18
    kicker = load(SANS_B, 13)
    draw.text((x, y), LEAD["kicker"], font=kicker, fill=CRIMSON)
    head = load(SERIF_B, 30)
    lines = fit_lines(draw, LEAD["headline"], head, CONTENT_W - 18, 2)
    yy = y + 18
    for line in lines:
        draw.text((x, yy), line, font=head, fill=INK)
        yy += 36
    deck = load(SANS, 15)
    dlines = fit_lines(draw, LEAD["deck"], deck, CONTENT_W - 18, 2)
    yy += 4
    for line in dlines:
        draw.text((x, yy), line, font=deck, fill=(58, 58, 58))
        yy += 20


def draw_map(draw):
    top = 306
    bottom = 446
    section_head(draw, 284, "WHERE IT HAPPENED")
    draw.rectangle([MARGIN, top, SIDE - MARGIN, bottom], fill=OCEAN,
                   outline=RULE, width=1)
    continents = [
        [(75, 314), (140, 303), (215, 305), (268, 319), (285, 338),
         (255, 356), (225, 365), (195, 382), (150, 387), (105, 376),
         (70, 354), (58, 331)],
        [(240, 387), (285, 382), (310, 395), (300, 416), (275, 433),
         (250, 422), (238, 402)],
        [(470, 308), (525, 301), (560, 308), (575, 321), (545, 335),
         (505, 335), (478, 322)],
        [(478, 344), (545, 341), (580, 356), (600, 378), (575, 410),
         (530, 424), (495, 402), (475, 371)],
        [(580, 303), (680, 296), (800, 299), (905, 310), (935, 329),
         (905, 350), (860, 365), (800, 378), (730, 382), (660, 371),
         (615, 348), (585, 324)],
        [(820, 384), (860, 387), (880, 397), (840, 401)],
        [(800, 406), (865, 399), (895, 411), (875, 430), (825, 430),
         (800, 419)],
    ]
    for poly in continents:
        draw.polygon(poly, fill=LAND, outline=LAND_EDGE)
    num_face = load(SANS_B, 11)
    for num, (px, py, _label) in enumerate(PINS, start=1):
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PIN,
                     outline=(255, 255, 255), width=2)
        digit = str(num)
        dw = draw.textlength(digit, font=num_face)
        draw.text((px - dw / 2, py - 8), digit, font=num_face,
                  fill=(255, 255, 255))
    legend_face = load(SANS, 11)
    legend = "   ·   ".join("%d %s" % (n, label)
                            for n, (_x, _y, label) in enumerate(PINS, start=1))
    legend_lines = fit_lines(draw, legend, legend_face, CONTENT_W, 2)
    yy = 452
    for line in legend_lines:
        draw.text((MARGIN, yy), line, font=legend_face, fill=NAVY)
        yy += 14


def draw_cards(draw):
    section_head(draw, 490, "SIX STORIES THAT DEFINED THE DAY")
    gap = 13
    cw = (CONTENT_W - 2 * gap) // 3
    rows = [(512, 616), (624, 728)]
    for idx, (kicker, title, body) in enumerate(CARDS):
        col = idx % 3
        row = idx // 3
        y0, y1 = rows[row]
        x0 = MARGIN + col * (cw + gap)
        x1 = x0 + cw
        draw.rectangle([x0, y0, x1, y1], fill=PAGE_CARD, outline=RULE, width=1)
        draw.rectangle([x0, y0, x1, y0 + 3], fill=NAVY)
        kx = x0 + 12
        kick = load(SANS_B, 11)
        draw.text((kx, y0 + 10), kicker, font=kick, fill=CRIMSON)
        head = load(SERIF_B, 16)
        lines = fit_lines(draw, title, head, cw - 24, 2)
        yy = y0 + 28
        for line in lines:
            draw.text((kx, yy), line, font=head, fill=INK)
            yy += 20
        body_face = load(SANS, 12)
        blines = fit_lines(draw, body, body_face, cw - 24, 2)
        yy += 4
        for line in blines:
            draw.text((kx, yy), line, font=body_face, fill=(58, 58, 58))
            yy += 15


def draw_briefs(draw):
    section_head(draw, 740, "THE DAY IN BRIEF")
    col_w = (CONTENT_W - 24) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 24
    row_h = 24
    y_start = 764
    bold = load(SANS_B, 13)
    plain = load(SANS, 13)
    for idx, (place, text) in enumerate(BRIEFS):
        col = 0 if idx < 8 else 1
        row = idx if idx < 8 else idx - 8
        x = left_x if col == 0 else right_x
        y = y_start + row * row_h
        head = place + " — "
        hw = draw.textlength(head, font=bold)
        draw.text((x, y), head, font=bold, fill=NAVY)
        body_lines = fit_lines(draw, text, plain, col_w - hw, 1)
        draw.text((x + hw, y), body_lines[0], font=plain, fill=INK)


def draw_markets(draw):
    y0, y1 = 962, 996
    draw.rectangle([MARGIN, y0, SIDE - MARGIN, y1], fill=NAVY)
    items = "   ·   ".join(MARKETS)
    face = None
    for size in (14, 13, 12):
        face = load(SANS_B, size)
        if draw.textlength(items, font=face) <= CONTENT_W - 16:
            break
    w = draw.textlength(items, font=face)
    draw.text(((SIDE - w) / 2, y0 + 10), items, font=face,
              fill=(255, 255, 255))


def draw_footer(draw):
    face = load(SANS, 11)
    centred(draw, 1004, FOOTER, face, SLATE)


def build():
    canvas = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw_masthead(draw)
    draw_lead(draw)
    draw_map(draw)
    draw_cards(draw)
    draw_briefs(draw)
    draw_markets(draw)
    draw_footer(draw)
    canvas.save(TARGET, format="PNG")
    blob = open(TARGET, "rb").read()
    print("wrote %s (%d bytes) sha256=%s"
          % (TARGET, len(blob), hashlib.sha256(blob).hexdigest()))


if __name__ == "__main__":
    build()
