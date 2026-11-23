#!/usr/bin/env python3
"""Deterministic, standard-library-only front page for 23 NOVEMBER 2026.

Renders a single PNG to $OUT_DIR/entry.png (default /output/entry.png).
No randomness, no clock reads, no network access: identical bytes every run.
"""

from __future__ import annotations

import os
import struct
import zlib

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

W, H = 1000, 1000

PAPER = (247, 244, 235)
CARD = (253, 252, 247)
INK = (25, 29, 38)
NAVY = (29, 41, 61)
RED = (176, 38, 44)
MUTED = (92, 96, 103)
RULE = (207, 202, 190)
WHITE = (255, 255, 255)
CREAM = (255, 239, 196)

CATS = [
    (176, 38, 44),    # 1 mideast war
    (26, 82, 120),    # 2 iran-us talks
    (166, 91, 26),    # 3 yemen / saudi
    (62, 62, 104),    # 4 europe / ukraine
    (31, 111, 80),    # 5 climate
    (132, 40, 52),    # 6 israel
    (30, 99, 115),    # 7 asia
    (143, 90, 21),    # 8 sports
]

# ---------------------------------------------------------------------------
# Embedded 5x7 bitmap font.  Each glyph is exactly seven rows of five pixels.
# Digit zero carries a diagonal stroke so it never reads as the letter O.
# ---------------------------------------------------------------------------

FONT: dict[str, tuple[str, ...]] = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "....#", "....#", "....#", "#...#", "#...#", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}

for _glyph, _rows in FONT.items():
    assert len(_rows) == 7, _glyph
    assert all(len(_row) == 5 for _row in _rows), _glyph


def text_width(text: str, scale: int) -> int:
    """Pixel width of a rendered string (the trailing inter-glyph gap is omitted)."""
    if not text:
        return 0
    return (len(text) * 6 - 1) * scale


# ---------------------------------------------------------------------------
# Canvas: flat RGB framebuffer and tiny drawing primitives
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, width: int, height: int, background: tuple[int, int, int]) -> None:
        self.w = width
        self.h = height
        self.px = bytearray(bytes(background) * (width * height))

    def rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
        if w <= 0 or h <= 0:
            return
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        run = bytes(color) * (x1 - x0)
        stride = self.w * 3
        for yy in range(y0, y1):
            off = yy * stride + x0 * 3
            self.px[off:off + len(run)] = run

    def hline(self, x1: int, x2: int, y: int, color: tuple[int, int, int],
              thickness: int = 1) -> None:
        self.rect(x1, y, x2 - x1 + 1, thickness, color)

    def vline(self, x: int, y1: int, y2: int, color: tuple[int, int, int],
              thickness: int = 1) -> None:
        self.rect(x, y1, thickness, y2 - y1 + 1, color)

    def line(self, x1: int, y1: int, x2: int, y2: int,
             color: tuple[int, int, int]) -> None:
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self.rect(x1, y1, 1, 1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def circle(self, cx: int, cy: int, r: int, color: tuple[int, int, int],
               filled: bool = True) -> None:
        rr = r * r
        for yy in range(-r, r + 1):
            for xx in range(-r, r + 1):
                d = xx * xx + yy * yy
                inside = d <= rr
                on_edge = rr - 2 * r <= d <= rr + 2 * r
                if inside if filled else on_edge:
                    self.rect(cx + xx, cy + yy, 1, 1, color)

    def polygon(self, points: list[tuple[int, int]],
                color: tuple[int, int, int]) -> None:
        ys = [p[1] for p in points]
        edges = list(zip(points, points[1:] + points[:1]))
        for yy in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            crossings: list[float] = []
            for (ax, ay), (bx, by) in edges:
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    crossings.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if crossings:
                left = round(min(crossings))
                right = round(max(crossings))
                self.rect(left, yy, right - left + 1, 1, color)

    def text(self, x: int, y: int, string: str, scale: int,
             color: tuple[int, int, int]) -> None:
        for index, char in enumerate(string):
            glyph = FONT[char]
            gx = x + index * 6 * scale
            for gy, row in enumerate(glyph):
                for gxx, bit in enumerate(row):
                    if bit == "#":
                        self.rect(gx + gxx * scale, y + gy * scale, scale, scale, color)

    def fitted(self, x: int, y: int, string: str, scale: int,
               color: tuple[int, int, int], right: int, bottom: int,
               label: str) -> None:
        """Draw text only after proving it fits its container."""
        for char in string:
            if char not in FONT:
                raise ValueError(f"missing glyph {char!r} in {label!r}")
        width = text_width(string, scale)
        height = 7 * scale
        if x < 0 or x + width > right or y < 0 or y + height > bottom:
            raise ValueError(
                f"overflow in {label!r}: {string!r} is {width}x{height} at "
                f"({x},{y}), container right={right} bottom={bottom}"
            )
        self.text(x, y, string, scale, color)


# ---------------------------------------------------------------------------
# Flat pictograms: 40x24 white/colour geometry inside each card's header bar
# ---------------------------------------------------------------------------


def icon(c: Canvas, kind: int, ox: int, oy: int, bg: tuple[int, int, int]) -> None:
    ink, glow = WHITE, CREAM

    def r(dx: int, dy: int, dw: int, dh: int, col: tuple[int, int, int] = ink) -> None:
        c.rect(ox + dx, oy + dy, dw, dh, col)

    def p(points: list[tuple[int, int]], col: tuple[int, int, int] = ink) -> None:
        c.polygon([(ox + a, oy + b) for a, b in points], col)

    def ln(x1: int, y1: int, x2: int, y2: int,
           col: tuple[int, int, int] = ink) -> None:
        c.line(ox + x1, oy + y1, ox + x2, oy + y2, col)

    def dot(cx: int, cy: int, rad: int, col: tuple[int, int, int] = ink,
            filled: bool = True) -> None:
        c.circle(ox + cx, oy + cy, rad, col, filled)

    if kind == 0:  # industrial plant under strike
        r(0, 14, 15, 10)
        p([(0, 14), (4, 9), (11, 9), (15, 14)])
        r(17, 4, 5, 20)
        r(25, 11, 5, 13)
        r(32, 8, 4, 16)
        dot(34, 3, 2, glow)
        ln(34, 0, 34, 1, glow)
        ln(27, 2, 29, 4, glow)
        ln(39, 4, 37, 6, glow)
    elif kind == 1:  # handshake: two sleeves and interlaced fingers
        p([(0, 12), (9, 12), (13, 15), (13, 19), (9, 21), (0, 21)], ink)
        p([(40, 12), (31, 12), (27, 15), (27, 19), (31, 21), (40, 21)], glow)
        r(9, 12, 2, 9, bg)
        r(29, 12, 2, 9, bg)
        # fingers from each hand alternate as they clasp
        r(12, 9, 12, 3, ink)
        r(12, 14, 12, 3, ink)
        r(12, 19, 11, 3, ink)
        r(16, 12, 12, 3, glow)
        r(16, 17, 12, 3, glow)
        for yy in (12, 17, 22):
            r(12, yy, 17, 1, bg)
    elif kind == 2:  # refinery tanks, flame and tanker
        r(0, 11, 9, 13)
        dot(4, 11, 4)
        r(11, 14, 8, 10)
        p([(22, 23), (26, 10), (30, 23)], glow)
        p([(32, 17), (40, 17), (38, 22), (34, 22)])
        ln(31, 23, 39, 23)
    elif kind == 3:  # warship, sea drones, waves
        p([(1, 16), (35, 16), (30, 22), (7, 22)])
        r(18, 5, 2, 11)
        r(12, 9, 14, 2)
        ln(18, 5, 25, 8)
        dot(6, 5, 2, glow)
        ln(3, 5, 9, 5, glow)
        dot(34, 7, 2, glow)
        ln(31, 7, 37, 7, glow)
        ln(5, 23, 17, 23)
        ln(24, 23, 38, 23)
    elif kind == 4:  # globe, smokestack, climate rift
        dot(12, 12, 9, ink, False)
        ln(12, 3, 12, 21)
        ln(3, 12, 21, 12)
        r(26, 6, 5, 18)
        r(34, 12, 4, 12)
        ln(27, 5, 30, 2, glow)
        ln(35, 11, 38, 8, glow)
        ln(5, 20, 19, 4, glow)
    elif kind == 5:  # two broken coalition links
        dot(11, 12, 8, ink, False)
        dot(29, 12, 8, ink, False)
        r(19, 11, 3, 2, bg)
        ln(18, 7, 22, 4, glow)
        ln(22, 4, 20, 1, glow)
        ln(24, 17, 20, 20, glow)
    elif kind == 6:  # Himalaya and two meeting delegations
        p([(0, 22), (10, 6), (20, 22)])
        p([(15, 22), (26, 9), (38, 22)])
        p([(5, 11), (10, 6), (15, 11)], bg)
        r(8, 1, 2, 5)
        r(10, 1, 6, 4, glow)
        r(29, 2, 2, 5)
        r(27, 2, 6, 4, glow)
        ln(16, 23, 24, 23)
    elif kind == 7:  # basketball and scoring hoop
        dot(12, 12, 10, ink, False)
        ln(12, 2, 12, 22)
        ln(2, 12, 22, 12)
        ln(5, 5, 19, 19)
        ln(19, 5, 5, 19)
        r(28, 3, 2, 18)
        r(30, 9, 10, 2, glow)
        ln(31, 11, 33, 20, glow)
        ln(35, 11, 36, 20, glow)
        ln(39, 11, 38, 20, glow)


# ---------------------------------------------------------------------------
# Story copy.  Every line is upper-case and width-checked at draw time.
# ---------------------------------------------------------------------------

# Scores and counts are spelled with digit glyphs, never letter look-alikes.
SCORE = "116-114"
FLAGG_POINTS = "28"
assert all(ch in FONT for ch in SCORE + FLAGG_POINTS)
assert FONT["0"] != FONT["O"]  # the slashed zero must not read as the letter O

STORIES = [
    {
        "cat": "MIDEAST WAR",
        "status": "IRAN STRIKES BAHRAIN",
        "lines": [
            "IRAN HITS AN INDUSTRIAL SITE",
            "IN BAHRAIN. WHITE HOUSE SAYS",
            "RENEWED US STRIKES ON IRAN",
            "DECISION DUE WITHIN A WEEK",
        ],
        "sub": ["US STRIKE CALL DUE WITHIN SEVEN DAYS"],
    },
    {
        "cat": "IRAN-US TALKS",
        "status": "DEAL PUSH, WAR WARNING",
        "lines": [
            "TRUMP WANTS A PERMANENT DEAL",
            "WITH IRAN; INCLINED TO RESUME",
            "WAR IF NO DEAL BY NEW YEAR",
            "IRAN FM: HORMUZ CAN REOPEN",
        ],
        "sub": ["IF US ACCEPTS REASONABLE TERMS"],
    },
    {
        "cat": "YEMEN / SAUDI",
        "status": "RABIGH REFINERY ATTACKED",
        "lines": [
            "HOUTHIS SAY THEY ATTACKED THE",
            "RABIGH OIL REFINERY IN SAUDI ARABIA;",
            "TWO TANKERS CATCH FIRE. SAUDI",
            "INTERCEPTS A HOUTHI DRONE",
        ],
        "sub": ["ATTACK CLAIM AND INTERCEPTION"],
    },
    {
        "cat": "EUROPE / UKRAINE",
        "status": "WARSHIP HIT AT BENGHAZI",
        "lines": [
            "RUSSIAN WARSHIP HIT BY SUSPECTED",
            "UKRAINIAN SEA DRONES AT BENGHAZI",
            "NAVAL BASE, LIBYAN OFFICIALS SAY",
        ],
        "sub": [
            "LIBYAN OFFICIALS REPORT THE STRIKE",
            "REPORT FROM BENGHAZI NAVAL BASE",
        ],
    },
    {
        "cat": "CLIMATE",
        "status": "COP31 ENDS WITH NO DEAL",
        "lines": [
            "COP31 IN TURKIYE CONCLUDES",
            "WITHOUT AN OVERARCHING DEAL",
            "EU REFUSES TO BACK A DRAFT",
            "THAT OMITS FOSSIL FUELS",
        ],
        "sub": ["NO OVERARCHING CLIMATE AGREEMENT"],
    },
    {
        "cat": "ISRAEL",
        "status": "COALITION TALKS COLLAPSE",
        "lines": [
            "NETANYAHU AND EISENKOT END",
            "COALITION TALKS WITH NO DEAL",
            "ON FORMING ISRAEL'S GOVERNMENT",
        ],
        "sub": [
            "NO NEW GOVERNMENT AGREED",
            "TALKS COLLAPSE WITHOUT A DEAL",
        ],
    },
    {
        "cat": "ASIA",
        "status": "LAC TALKS; SEKI SCANDAL",
        "lines": [
            "INDIA, CHINA HOLD 10-DAY TALKS",
            "TO EASE LAC TENSIONS IN ARUNACHAL",
            "JAPAN: EDUCATION MINISTER SEKI",
            "FACES CALLS TO RESIGN OVER SCANDALS",
        ],
        "sub": ["BORDER TALKS AND RESIGNATION CALLS"],
    },
    {
        "cat": "SPORTS",
        "status": f"MAVERICKS {SCORE} JAZZ",
        "lines": [
            f"MAVERICKS EDGE JAZZ {SCORE}",
            f"IN UTAH; COOPER FLAGG: {FLAGG_POINTS} POINTS",
        ],
        "sub": [
            "ALSO: TRUMP V CONGRESS",
            "WHITE HOUSE MOVES TO LIMIT",
            "DEMOCRATS' INCOMING INVESTIGATIONS",
        ],
    },
]


# ---------------------------------------------------------------------------
# Page composition
# ---------------------------------------------------------------------------


def diamond(c: Canvas, cx: int, cy: int, rad: int,
            color: tuple[int, int, int]) -> None:
    c.polygon([(cx, cy - rad), (cx + rad, cy), (cx, cy + rad), (cx - rad, cy)], color)


def draw_masthead(c: Canvas) -> None:
    c.rect(0, 0, W, 6, RED)
    c.hline(0, W - 1, 10, NAVY, 2)

    c.fitted(14, 30, "GLOBAL EDITION", 2, MUTED, W, H, "masthead kicker")
    c.fitted(W - 14 - text_width("FRONT PAGE", 2), 30, "FRONT PAGE", 2,
             MUTED, W, H, "masthead kicker")

    title = "WORLD NEWS"
    c.fitted((W - text_width(title, 7)) // 2, 18, title, 7, INK, W, H, "masthead title")
    diamond(c, 248, 42, 7, RED)
    diamond(c, 752, 42, 7, RED)
    c.hline(0, W - 1, 70, NAVY, 2)

    c.rect(0, 76, W, 36, RED)
    c.hline(0, W - 1, 76, WHITE)
    c.hline(0, W - 1, 111, WHITE)
    date = "23 NOVEMBER 2026"
    c.fitted((W - text_width(date, 4)) // 2, 80, date, 4, WHITE, W, H, "date band")
    diamond(c, 288, 94, 4, CREAM)
    diamond(c, 712, 94, 4, CREAM)
    c.hline(0, W - 1, 118, NAVY, 2)


CARD_TOP = 126
CARD_H = 198
CARD_GAP_Y = 8
MARGIN = 14
CARD_GAP_X = 12
CARD_W = (W - 2 * MARGIN - CARD_GAP_X) // 2
HEAD_H = 32
TEXT_X_PAD = 12
TEXT_W = CARD_W - 2 * TEXT_X_PAD


def draw_card(c: Canvas, story: dict, index: int) -> None:
    col, row = index % 2, index // 2
    x = MARGIN + col * (CARD_W + CARD_GAP_X)
    y = CARD_TOP + row * (CARD_H + CARD_GAP_Y)
    color = CATS[index]

    c.rect(x, y, CARD_W, CARD_H, CARD)
    c.hline(x, x + CARD_W - 1, y, RULE)
    c.hline(x, x + CARD_W - 1, y + CARD_H - 1, RULE)
    c.vline(x, y, y + CARD_H - 1, RULE)
    c.vline(x + CARD_W - 1, y, y + CARD_H - 1, RULE)

    c.rect(x + 1, y + 1, CARD_W - 2, HEAD_H - 1, color)
    c.fitted(x + TEXT_X_PAD, y + 9, story["cat"], 2, WHITE,
             x + CARD_W - 56, y + HEAD_H, f"card {index + 1} category")
    icon(c, index, x + CARD_W - TEXT_X_PAD - 40, y + 4, color)

    tx = x + TEXT_X_PAD
    right = x + CARD_W - TEXT_X_PAD
    bottom = y + CARD_H - 8
    c.fitted(tx, y + 40, story["status"], 3, color, right, bottom,
             f"card {index + 1} status")

    for line_no, line in enumerate(story["lines"]):
        c.fitted(tx, y + 69 + 19 * line_no, line, 2, INK, right, bottom,
                 f"card {index + 1} line {line_no + 1}")

    sub_first = y + 69 + 19 * len(story["lines"]) + 6
    for sub_no, line in enumerate(story["sub"]):
        c.fitted(tx, sub_first + 17 * sub_no, line, 2, MUTED, right, bottom,
                 f"card {index + 1} sub-line {sub_no + 1}")

    c.hline(x + TEXT_X_PAD, x + CARD_W - TEXT_X_PAD - 1,
            y + CARD_H - 10, RULE)


def draw_ticker(c: Canvas) -> None:
    top = 950
    c.rect(0, top, W, 42, NAVY)
    c.rect(0, top, 150, 42, RED)
    c.fitted(16, top + 14, "WORLD WIRE", 2, WHITE, 150, H, "ticker label")
    wire = f"STRIKES | TALKS | REFINERY | WARSHIP | CLIMATE | NBA {SCORE}"
    c.fitted(166, top + 14, wire, 2, CREAM, W - 14, H, "ticker wire")
    c.vline(158, top + 7, top + 34, RULE)


def render() -> bytes:
    c = Canvas(W, H, PAPER)
    draw_masthead(c)
    for i, story in enumerate(STORIES):
        draw_card(c, story, i)
    draw_ticker(c)
    return encode_png(c)


def encode_png(c: Canvas) -> bytes:
    stride = c.w * 3
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # PNG filter type 0: None
        raw.extend(c.px[y * stride:(y + 1) * stride])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main() -> None:
    out_dir = os.environ.get("OUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(render())


if __name__ == "__main__":
    main()
