#!/usr/bin/env python3
"""Sum up 24 November 2026's world news in one image.

Deterministic generator: fixed data, no network, no clock, no randomness.
Writes a 1024x1024 PNG front page to /output/entry.png (fallback ./output).
Uses Pillow when available; otherwise falls back to a tiny built-in bitmap
renderer so the entry still produces a valid image instead of crashing.
"""

import os
import struct
import zlib

W = 1024
H = 1024

INK = (20, 16, 12)
PAPER = (247, 243, 234)
ACCENT = (164, 32, 24)
BLUE = (24, 62, 120)
GREY = (92, 86, 76)
LIGHT = (232, 225, 208)
GREEN = (28, 96, 52)
AMBER = (166, 106, 10)

TOP = [
    {
        "kicker": "IRAN WAR",
        "headline": "VANCE AND RUBIO MEET QATAR'S PM AT THE WHITE HOUSE",
        "summary": "Iran vows to use every tool against a US naval blockade as "
                   "Washington and Doha talk in private. Meeting held 23 Nov, "
                   "first reported 24 Nov.",
        "source": "AP / Reuters via Just Security",
        "label": "REPORTED",
    },
    {
        "kicker": "NVIDIA",
        "headline": "HUANG RESTORED AS CEO; SHARES LEAP 31%",
        "summary": "Huang returns under two weeks after stepping down. Nvidia "
                   "adds nearly $1tn; Nasdaq +6.5%, S&P 500 +4.75%.",
        "source": "BBC / FT",
        "label": "REPORTED",
    },
    {
        "kicker": "RUSSIA-UKRAINE",
        "headline": "STRIKE ON ZAPORIZHZHIA HOMES: 2 DEAD, 40 HURT",
        "summary": "Overnight attack hits an apartment block, injuring four "
                   "children. Kyiv accuses Moscow over a nuclear-armed satellite.",
        "source": "Reuters / BBC",
        "label": "REPORTED",
    },
]

# region, headline, source, label
STORIES = [
    ("NORTH AMERICA", "US puts Singapore's Megaspeed on Entity List over chip-diversion risk", "Politico", "REPORTED"),
    ("NORTH AMERICA", "Pentagon questions Canada's reliability in North American defence", "AP", "CLAIM"),
    ("NORTH AMERICA", "CIA and second US agency hit by cyberattack; core work 'not disrupted'", "CBS", "REPORTED"),
    ("NORTH AMERICA", "FBI probes suspected breach of NCIC's 18m-record database", "BBC", "CLAIM"),
    ("NORTH AMERICA", "DOJ admits it wrongly deported US citizen Brian Jose Morales Garcia", "The Hill", "REPORTED"),
    ("LATIN AMERICA", "UN chief Guterres urges a global AI risk framework at Bridgetown summit", "UN News", "REPORTED"),
    ("LATIN AMERICA", "US pauses joint military operations with Ecuador amid raid inquiry", "NYT via Reuters", "REPORTED"),
    ("LATIN AMERICA", "US hails progress in Venezuela reconciliation talks", "US State Dept", "REPORTED"),
    ("EUROPE", "Seven EU states urge tighter visa limits for Russians", "Kyiv Independent", "REPORTED"),
    ("EUROPE", "Germany first to access Ukraine's Delta battlefield-management system", "Kyiv Independent", "REPORTED"),
    ("EUROPE", "Brexit debate returns as five former PMs warn Burnham in Parliament", "Politico", "REPORTED"),
    ("EUROPE", "UK sanctions Houthi figures over torture, rape and abuse", "Reuters", "REPORTED"),
    ("MIDDLE EAST", "Israeli strike in Gaza kills Hamas internal-security chief and six others", "Reuters", "REPORTED"),
    ("MIDDLE EAST", "Oxfam: Israeli attacks leave Gaza 'a toxic land'", "Al Arabiya / Oxfam", "CLAIM"),
    ("MIDDLE EAST", "Houthi attack on Riyadh's KAFD tower injures 11", "Al Arabiya", "REPORTED"),
    ("MIDDLE EAST", "Iraq's PM orders oil ministry to run fields in Kurdish-held areas", "Reuters", "REPORTED"),
    ("MIDDLE EAST", "Iran's rial slides on the black market after new US sanctions", "AFP", "REPORTED"),
    ("AFRICA", "Fighting near an Ituri hospital disrupts the Ebola response in DR Congo", "UN News / WHO", "REPORTED"),
    ("AFRICA", "Amnesty seeks a war-crimes probe into shelling in Tigray, Ethiopia", "Reuters / Amnesty", "CLAIM"),
    ("AFRICA", "UN mission urges an independent probe into the Benghazi port attack", "UN News", "CLAIM"),
    ("ASIA-PACIFIC", "Russian jet enters Seoul's air-defence zone; protest lodged", "AFP / AP", "REPORTED"),
    ("ASIA-PACIFIC", "Seoul offers a $375,000 bounty to catch AI exam cheating", "Wall Street Journal", "REPORTED"),
    ("ASIA-PACIFIC", "Japan to pay its full 2027 ICC contribution by year-end, Takaichi says", "Reuters", "REPORTED"),
    ("ASIA-PACIFIC", "China begins 6G trials across eight provinces and cities", "Global Times / CCTV", "REPORTED"),
    ("ASIA-PACIFIC", "Australia's AI committee tables 46 governance recommendations", "Digital Watch", "REPORTED"),
    ("ASIA-PACIFIC", "Hasina aide: she returns 16 Dec; Dhaka minister denies it", "Reuters / BBC", "CLAIM+DENIAL"),
]

# Which regions go in which of the three story columns (keeps columns even).
COLUMNS = [
    ["NORTH AMERICA", "LATIN AMERICA"],
    ["EUROPE", "MIDDLE EAST"],
    ["AFRICA", "ASIA-PACIFIC"],
]

NUMBERS = [
    "2 dead, 40 hurt in Zaporizhzhia - Reuters",
    "+31% Nvidia in one day - BBC",
    "11 injured in Riyadh attack - Saudi Civil Defense",
    "2.82m rials to $1, up 5% - AFP",
    "18m records in NCIC probe - BBC",
]

DATE_CHECK = (
    "Date check: every item was reported on 24 Nov 2026. Excluded as earlier news: the "
    "Bahrain/Hormuz tanker incident (21 Nov), the Pakistan PM Russia-trip cancellation "
    "(23 Nov) and the Russian missile incursion into Poland (22 Nov). The Vance/Rubio-Qatar "
    "meeting was held 23 Nov but first reported 24 Nov, so it is included and labelled."
)

LEGEND = "Labels: REPORTED = sourced report of an event - CLAIM = asserted, not independently confirmed - DENIAL = disputed by the other side"

TIMELINE = "Through the day, by region: Middle East - Asia-Pacific - Europe - Africa - the Americas (sources give no exact UTC times; none are invented here)"

# Coarse schematic world map as a dot grid (rows of equal length).
MAP_ROWS = [
    "        oooo          oooooooooooo   oooooooo                         ",
    "      oooooooo      oooooooooooooooooooooooooooo      ooooo           ",
    "     oooooooooo    ooooooooooooooooooooooooooooooo  ooooooooo         ",
    "      oooooooo      ooooooooooooooooooooooooooooo  ooooooooooo        ",
    "       oooooo        ooooo oooooooooooooooooooo     ooooooooo         ",
    "        oooo          oo   oooooooooooooooooo        ooooooo          ",
    "         oo                oooooooooooooooo           ooooo           ",
    "          o                 oooooooooooooo             ooo            ",
    "          oo                 oooooooooooo                             ",
    "          ooo                 oooooooooo              oo              ",
    "           ooo                 oooooooo              oooo             ",
    "           oooo                 oooooo                oo              ",
    "            ooo                  oooo                                 ",
    "            oooo                  oo                  oo              ",
    "             oo                                       oooo            ",
    "             o                                         oo             ",
]


def wrap(text, font, max_width, draw):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def render_pil():
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    def F(size):
        return ImageFont.load_default(size=size)

    M = 28  # margin
    # Masthead
    d.rectangle([0, 0, W, 78], fill=INK)
    d.text((M, 10), "THE WORLD IN ONE PAGE", font=F(42), fill=PAPER)
    d.text((M, 56), "Tuesday 24 November 2026 - 29 stories - 7 regions - all reported on 24 Nov", font=F(16), fill=(210, 200, 178))
    y = 86

    # Top story (full width)
    t = TOP[0]
    d.rectangle([M, y, W - M, y + 104], outline=INK, width=2)
    d.rectangle([M, y, M + 150, y + 24], fill=ACCENT)
    d.text((M + 8, y + 4), t["kicker"], font=F(16), fill=PAPER)
    d.text((W - M - 118, y + 4), t["label"], font=F(14), fill=ACCENT)
    yy = y + 30
    for ln in wrap(t["headline"], F(27), W - 2 * M - 24, d)[:2]:
        d.text((M + 12, yy), ln, font=F(27), fill=INK)
        yy += 32
    for ln in wrap(t["summary"] + "  (" + t["source"] + ")", F(15), W - 2 * M - 24, d)[:2]:
        d.text((M + 12, yy), ln, font=F(15), fill=GREY)
        yy += 19
    y += 112

    # Top stories 2 and 3 (two columns)
    colw2 = (W - 2 * M - 16) // 2
    for i, t in enumerate(TOP[1:]):
        x = M + i * (colw2 + 16)
        d.rectangle([x, y, x + colw2, y + 116], outline=INK, width=2)
        d.rectangle([x, y, x + 170, y + 24], fill=BLUE if i == 0 else ACCENT)
        d.text((x + 8, y + 4), t["kicker"], font=F(16), fill=PAPER)
        d.text((x + colw2 - 118, y + 4), t["label"], font=F(14), fill=ACCENT)
        yy = y + 30
        for ln in wrap(t["headline"], F(21), colw2 - 20, d)[:2]:
            d.text((x + 10, yy), ln, font=F(21), fill=INK)
            yy += 25
        for ln in wrap(t["summary"] + "  (" + t["source"] + ")", F(13), colw2 - 20, d)[:3]:
            d.text((x + 10, yy), ln, font=F(13), fill=GREY)
            yy += 16
    y += 124

    # Region index + day in numbers strip
    d.rectangle([M, y, W - M, y + 108], fill=LIGHT)
    rx = M + 14
    d.text((rx, y + 8), "REGIONS AT A GLANCE", font=F(18), fill=INK)
    chips = [
        "NORTH AMERICA 5", "LATIN AMERICA 3", "EUROPE 4",
        "MIDDLE EAST 5", "AFRICA 3", "ASIA-PACIFIC 6", "TOP STORIES 3",
    ]
    cx, cy = rx, y + 36
    for chip in chips:
        wchip = d.textlength(chip, font=F(13)) + 16
        if cx + wchip > M + 428:
            cx = rx
            cy += 30
        d.rectangle([cx, cy, cx + wchip, cy + 24], fill=BLUE)
        d.text((cx + 8, cy + 5), chip, font=F(13), fill=PAPER)
        cx += wchip + 8
    nx = M + 452
    d.text((nx, y + 8), "DAY IN NUMBERS", font=F(18), fill=INK)
    yy = y + 32
    for line in NUMBERS:
        d.text((nx, yy), line, font=F(14.5), fill=ACCENT)
        yy += 16
    y += 116

    # Story columns: three columns, grouped by region, auto-fit headline size
    regions = {}
    for region, headline, source, label in STORIES:
        regions.setdefault(region, []).append((headline, source, label))
    gap = 14
    colw = (W - 2 * M - 2 * gap) // 3
    footer_top = H - 100
    avail = footer_top - y - 4

    def col_height(groups, hsize):
        total = 0
        hf = F(hsize)
        for region in groups:
            total += 24 + 5
            for headline, source, label in regions[region]:
                total += len(wrap(headline, hf, colw - 8, d)) * (hsize + 2.5) + 15 + 3
            total += 5
        return total

    hsize = 14.5
    while hsize > 11 and max(col_height(g, hsize) for g in COLUMNS) > avail:
        hsize -= 0.5
    hf = F(hsize)
    lh = hsize + 2.5
    for ci, groups in enumerate(COLUMNS):
        x = M + ci * (colw + gap)
        yy = y
        for region in groups:
            d.rectangle([x, yy, x + colw, yy + 21], fill=INK)
            d.text((x + 6, yy + 3), region, font=F(13.5), fill=PAPER)
            yy += 26
            for headline, source, label in regions[region]:
                lab_col = GREEN if label == "REPORTED" else (AMBER if label == "CLAIM" else ACCENT)
                for ln in wrap(headline, hf, colw - 8, d):
                    d.text((x + 2, yy), ln, font=hf, fill=INK)
                    yy += lh
                d.text((x + 2, yy), source + " - ", font=F(11), fill=GREY)
                sw = d.textlength(source + " - ", font=F(11))
                d.text((x + 2 + sw, yy), label, font=F(11), fill=lab_col)
                yy += 15 + 3
            yy += 5

    # Footer: timeline + legend + date check
    fy = footer_top
    d.rectangle([0, fy, W, H], fill=INK)
    d.text((M, fy + 7), TIMELINE, font=F(13), fill=(210, 200, 178))
    d.text((M, fy + 27), LEGEND, font=F(12), fill=(210, 200, 178))
    yy = fy + 47
    for ln in wrap(DATE_CHECK, F(12), W - 2 * M, d)[:3]:
        d.text((M, yy), ln, font=F(12), fill=(168, 160, 144))
        yy += 15
    return img


def render_fallback():
    """Pure-stdlib PNG with a 3x5 micro font (only used if Pillow is absent)."""
    px = [[PAPER for _ in range(W)] for _ in range(H)]

    def set_px(x, y, col):
        if 0 <= x < W and 0 <= y < H:
            px[y][x] = col

    glyphs = {
        "A": (2, 5, 7, 5, 5), "B": (6, 5, 6, 5, 6), "C": (3, 4, 4, 4, 3),
        "D": (6, 5, 5, 5, 6), "E": (7, 4, 6, 4, 7), "F": (7, 4, 6, 4, 4),
        "G": (3, 4, 5, 5, 3), "H": (5, 5, 7, 5, 5), "I": (7, 2, 2, 2, 7),
        "J": (1, 1, 1, 5, 2), "K": (5, 5, 6, 5, 5), "L": (4, 4, 4, 4, 7),
        "M": (5, 7, 7, 5, 5), "N": (5, 7, 7, 7, 5), "O": (2, 5, 5, 5, 2),
        "P": (6, 5, 6, 4, 4), "Q": (2, 5, 5, 6, 3), "R": (6, 5, 6, 5, 5),
        "S": (3, 4, 2, 1, 6), "T": (7, 2, 2, 2, 2), "U": (5, 5, 5, 5, 7),
        "V": (5, 5, 5, 5, 2), "W": (5, 5, 7, 7, 5), "X": (5, 5, 2, 5, 5),
        "Y": (5, 5, 2, 2, 2), "Z": (7, 1, 2, 4, 7),
        "0": (7, 5, 5, 5, 7), "1": (2, 2, 2, 2, 2), "2": (6, 1, 2, 4, 7),
        "3": (6, 1, 2, 1, 6), "4": (5, 5, 7, 1, 1), "5": (7, 4, 6, 1, 6),
        "6": (3, 4, 6, 5, 2), "7": (7, 1, 1, 2, 2), "8": (2, 5, 2, 5, 2),
        "9": (2, 5, 3, 1, 6), " ": (0, 0, 0, 0, 0), "-": (0, 0, 7, 0, 0),
        ".": (0, 0, 0, 0, 2), ",": (0, 0, 0, 2, 4), ":": (0, 2, 0, 2, 0),
        "'": (2, 2, 0, 0, 0), "/": (1, 1, 2, 4, 4), "(": (1, 2, 2, 2, 1),
        ")": (4, 2, 2, 2, 4), "+": (0, 2, 7, 2, 0), "%": (5, 1, 2, 4, 5),
        "$": (2, 7, 6, 3, 2),
    }

    def draw_text(x, y, text, col, s=2):
        cx = x
        for ch in text.upper():
            g = glyphs.get(ch, glyphs[" "])
            for r in range(5):
                for c in range(3):
                    if (g[r] >> (2 - c)) & 1:
                        for dx in range(s):
                            for dy in range(s):
                                set_px(cx + c * s + dx, y + r * s + dy, col)
            cx += 4 * s
        return cx

    draw_text(28, 24, "THE WORLD IN ONE PAGE", INK, 6)
    draw_text(28, 66, "Tuesday 24 November 2026 - 29 stories - 7 regions", GREY, 3)
    yy = 120
    for t in TOP:
        draw_text(28, yy, t["kicker"] + ": " + t["headline"], INK, 3)
        yy += 34
    yy += 10
    for region, headline, source, label in STORIES:
        draw_text(28, yy, headline + " (" + source + " - " + label + ")", INK, 2)
        yy += 24
        if yy > H - 140:
            break
    draw_text(28, H - 120, "Day in numbers: 2 dead 40 hurt - +31% Nvidia - 11 injured Riyadh", ACCENT, 2)
    draw_text(28, H - 90, "Labels: REPORTED sourced - CLAIM asserted - DENIAL disputed", GREY, 2)
    draw_text(28, H - 60, "Date check: only items reported on 24 Nov 2026 are included.", GREY, 2)

    raw = b""
    for row in px:
        raw += b"\x00" + b"".join(bytes(p) for p in row)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        img = render_pil()
        img.save(out_path, format="PNG", optimize=False)
    except ImportError:
        with open(out_path, "wb") as f:
            f.write(render_fallback())
    print("wrote", out_path)


if __name__ == "__main__":
    main()
