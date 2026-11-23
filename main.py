#!/usr/bin/env python3
"""Draw one newspaper front page summing up Monday 23 November 2026.

Standard library only, no network, deterministic output: two runs write
byte-identical PNG bytes. A hand-written 5x7 bitmap font and a hand-written
PNG encoder (zlib via stdlib) draw the whole page.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (25, 23, 19)
RED = (163, 31, 22)
BLUE = (29, 78, 121)
GOLD = (176, 130, 24)
GREY = (110, 104, 90)
LIGHT_BLUE = (158, 196, 222)
SEA = (52, 110, 138)
FLAME = (224, 110, 20)
DARK_GREEN = (46, 90, 60)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, rows top to bottom, "#" = on, "." = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "10010", "00100", "01000", "01001", "10011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, color)

    def hline(self, x0, x1, y, color, thick=1):
        for yy in range(y, y + thick):
            for xx in range(x0, x1 + 1):
                self.put(xx, yy, color)

    def vline(self, x, y0, y1, color, thick=1):
        for xx in range(x, x + thick):
            for yy in range(y0, y1 + 1):
                self.put(xx, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, color):
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            self.line(ax, ay, bx, by, color)

    def circle(self, cx, cy, r, color, fill=False):
        # Midpoint circle; filled by horizontal spans.
        x, y, d = 0, r, 1 - r
        spans = []
        while x <= y:
            if fill:
                spans.append((cx - x, cx + x, cy + y))
                spans.append((cx - x, cx + x, cy - y))
                spans.append((cx - y, cx + y, cy + x))
                spans.append((cx - y, cx + y, cy - x))
            else:
                for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                               (cx + x, cy - y), (cx - x, cy - y),
                               (cx + y, cy + x), (cx - y, cy + x),
                               (cx + y, cy - x), (cx - y, cy - x)):
                    self.put(px, py, color)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        if fill:
            for x0, x1, yy in spans:
                self.hline(x0, x1, yy, color)

    def fill_poly(self, points, color):
        # Scanline fill for a simple polygon.
        ys = [p[1] for p in points]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                ax, ay = points[i]
                bx, by = points[(i + 1) % n]
                if ay == by:
                    continue
                if (ay <= yy < by) or (by <= yy < ay):
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(round(xs[j])), int(round(xs[j + 1])), yy, color)

    def outline_poly(self, points, color):
        n = len(points)
        for i in range(n):
            ax, ay = points[i]
            bx, by = points[(i + 1) % n]
            self.line(ax, ay, bx, by, color)


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw uppercase text; anything outside the font is skipped."""
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph:
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        cv.rect(cx + col * scale, y + row * scale,
                                scale, scale, color)
        cx += 6 * scale
    return cx - x


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.upper().split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, lines, scale, color, leading=None):
    lh = leading if leading is not None else 7 * scale + scale
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * lh, ln, scale, color)
    return y + len(lines) * lh


# ------------------------------------------------------------- illustrations
# Every illustration draws only inside its (x, y, w, h) box.

def ill_globe(cv, x, y, w, h):
    """Cracked globe over factory smoke: the COP31 lead art."""
    cx, cy, r = x + w // 2 - 20, y + h // 2 + 6, min(w, h) // 2 - 8
    cv.circle(cx, cy, r, BLUE)
    # latitude / longitude guides
    cv.circle(cx, cy, r // 2, LIGHT_BLUE)
    cv.line(cx - r, cy, cx + r, cy, LIGHT_BLUE)
    cv.line(cx, cy - r, cx, cy + r, LIGHT_BLUE)
    # rough continents
    cv.fill_poly([(cx - r + 12, cy - 18), (cx - 6, cy - 26), (cx + 2, cy - 10),
                  (cx - 8, cy - 2), (cx - r + 10, cy - 6)], DARK_GREEN)
    cv.fill_poly([(cx + 8, cy + 4), (cx + 26, cy - 2), (cx + r - 12, cy + 12),
                  (cx + 16, cy + 22), (cx + 4, cy + 16)], DARK_GREEN)
    cv.fill_poly([(cx - 20, cy + 16), (cx - 2, cy + 12), (cx + 2, cy + 26),
                  (cx - 14, cy + 30)], DARK_GREEN)
    # crack across the globe (all points kept inside the circle)
    cv.polyline([(cx - 40, cy - 78), (cx - 14, cy - 40), (cx + 8, cy - 8),
                 (cx - 8, cy + 30), (cx + 22, cy + 78)], RED)
    cv.polyline([(cx - 14, cy - 40), (cx - 44, cy - 18)], RED)
    # factory with smoke at the right edge of the box
    fx = x + w - 78
    fy = y + h - 46
    cv.rect(fx, fy, 66, 40, INK)
    cv.rect(fx + 8, fy - 26, 10, 26, INK)
    cv.rect(fx + 30, fy - 18, 10, 18, INK)
    cv.circle(fx + 13, fy - 34, 7, GREY, fill=True)
    cv.circle(fx + 22, fy - 44, 9, GREY, fill=True)
    cv.circle(fx + 35, fy - 28, 7, GREY, fill=True)
    cv.rect(fx + 4, fy + 12, 10, 8, GOLD)
    cv.rect(fx + 24, fy + 12, 10, 8, GOLD)
    cv.rect(fx + 44, fy + 12, 10, 8, GOLD)


def ill_tanker(cv, x, y, w, h):
    """Oil tanker on fire with a naval mine."""
    wy = y + h - 26  # waterline
    cv.hline(x + 6, x + w - 6, wy, SEA, 3)
    cv.hline(x + 14, x + w - 14, wy + 8, SEA, 3)
    # hull
    cv.fill_poly([(x + 20, wy - 22), (x + w - 90, wy - 22),
                  (x + w - 74, wy - 2), (x + 34, wy - 2)], INK)
    cv.rect(x + w - 88, wy - 44, 26, 24, INK)  # bridge
    cv.rect(x + w - 96, wy - 52, 8, 10, RED)   # funnel
    cv.hline(x + 20, x + w - 90, wy - 22, RED, 3)
    # flames mid-ship
    fx = x + w // 2 - 40
    cv.fill_poly([(fx, wy - 22), (fx + 14, wy - 52), (fx + 26, wy - 22)], FLAME)
    cv.fill_poly([(fx + 18, wy - 22), (fx + 30, wy - 44), (fx + 42, wy - 22)], RED)
    cv.circle(fx + 12, wy - 58, 6, GREY, fill=True)
    cv.circle(fx + 26, wy - 66, 8, GREY, fill=True)
    # naval mine, top right: spiked ball with knobs on the spikes
    mx, my, mr = x + w - 34, y + 26, 11
    cv.circle(mx, my, mr, INK, fill=True)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1),
                   (-1, 1), (1, 1)):
        cv.line(mx + dx * mr, my + dy * mr,
                mx + dx * (mr + 8), my + dy * (mr + 8), INK)
        cv.circle(mx + dx * (mr + 9), my + dy * (mr + 9), 2, INK, fill=True)


def ill_ship_sunk(cv, x, y, w, h):
    """Warship capsized in harbour, bow above water."""
    wy = y + h - 30
    cv.hline(x + 6, x + w - 6, wy, SEA, 3)
    cv.hline(x + 14, x + w - 14, wy + 8, SEA, 3)
    # capsized hull: mostly submerged, tilted
    cv.fill_poly([(x + 30, wy - 6), (x + w - 60, wy - 34),
                  (x + w - 30, wy - 20), (x + w - 24, wy - 2),
                  (x + 60, wy - 2)], INK)
    # bow sticking up
    cv.fill_poly([(x + w - 60, wy - 34), (x + w - 34, wy - 62),
                  (x + w - 22, wy - 40), (x + w - 30, wy - 20)], RED)
    # broken mast in the water
    cv.line(x + 60, wy - 8, x + 96, wy - 34, INK)
    cv.line(x + 96, wy - 34, x + 104, wy - 26, INK)
    # smoke and fire
    cv.fill_poly([(x + w - 70, wy - 40), (x + w - 58, wy - 66),
                  (x + w - 44, wy - 40)], FLAME)
    cv.circle(x + w - 58, wy - 74, 7, GREY, fill=True)
    cv.circle(x + w - 44, wy - 82, 9, GREY, fill=True)
    # small drone boat approaching
    cv.fill_poly([(x + 18, wy - 12), (x + 44, wy - 12),
                  (x + 50, wy - 4), (x + 14, wy - 4)], BLUE)
    cv.line(x + 30, wy - 12, x + 30, wy - 22, BLUE)


def ill_building(cv, x, y, w, h):
    """Apartment block with a collapsed middle section."""
    bx, by, bw, bh = x + 30, y + 8, w - 60, h - 34
    cv.rect(bx, by, bw, bh, INK)
    # windows, skipping the collapsed middle column band
    for row in range(4):
        wyy = by + 10 + row * 18
        for col in range(6):
            wx = bx + 8 + col * 22
            if 2 <= col <= 3 and row >= 1:
                continue  # collapsed section
            cv.rect(wx, wyy, 12, 12, GOLD)
    # collapsed section: jagged rubble
    cv.fill_poly([(bx + 44, by + 28), (bx + 92, by + 28), (bx + 96, by + 62),
                  (bx + 78, by + 52), (bx + 66, by + 66), (bx + 52, by + 50),
                  (bx + 40, by + 62)], GREY)
    cv.line(bx + 44, by + 28, bx + 66, by + 46, INK)
    cv.line(bx + 92, by + 28, bx + 74, by + 50, INK)
    # rubble pile at the base
    cv.fill_poly([(bx + 30, by + bh), (bx + 52, by + bh - 16),
                  (bx + 74, by + bh - 6), (bx + 96, by + bh - 14),
                  (bx + 112, by + bh)], GREY)
    # smoke
    cv.circle(bx + 68, by - 2, 6, GREY, fill=True)
    cv.circle(bx + 78, by - 10, 8, GREY, fill=True)
    # ground line
    cv.hline(x + 6, x + w - 6, by + bh + 4, INK, 2)


def ill_factory(cv, x, y, w, h):
    """Burning factory with smoke column."""
    bx, by, bw, bh = x + 40, y + 26, w - 80, h - 52
    cv.rect(bx, by, bw, bh, INK)
    cv.fill_poly([(bx - 6, by), (bx + bw // 2, by - 18),
                  (bx + bw + 6, by)], RED)  # roofline
    for col in range(4):
        cv.rect(bx + 12 + col * 34, by + 16, 20, 14, GOLD)
    cv.rect(bx + bw - 26, by + bh - 26, 16, 26, PAPER)  # door
    # flames from the roof
    fx = bx + bw // 2 - 30
    cv.fill_poly([(fx, by - 16), (fx + 16, by - 44), (fx + 32, by - 16)], FLAME)
    cv.fill_poly([(fx + 26, by - 16), (fx + 40, by - 36), (fx + 54, by - 16)], RED)
    # tall smoke column
    cv.circle(bx + bw // 2, y + 2, 7, GREY, fill=True)
    cv.circle(bx + bw // 2 + 10, y + 10, 9, GREY, fill=True)
    cv.circle(bx + bw // 2 - 8, y + 12, 6, GREY, fill=True)
    cv.hline(x + 6, x + w - 6, by + bh + 4, INK, 2)


def ill_missile(cv, x, y, w, h):
    """Cruise missile over a NATO compass star."""
    # compass star, left
    sx, sy, r = x + 52, y + h // 2, 34
    star = []
    for i in range(8):
        ang = i * 3.14159265 / 4 - 3.14159265 / 2
        rr = r if i % 2 == 0 else r // 3
        star.append((int(sx + rr * math.cos(ang)),
                     int(sy + rr * math.sin(ang))))
    cv.fill_poly(star, BLUE)
    cv.circle(sx, sy, 6, PAPER, fill=True)
    # missile, right, angled up
    mx, my = x + 108, y + h // 2 + 18
    cv.fill_poly([(mx, my - 8), (mx + 96, my - 8), (mx + 118, my),
                  (mx + 96, my + 8), (mx, my + 8)], INK)
    cv.fill_poly([(mx + 118, my), (mx + 128, my - 4), (mx + 128, my + 4)], RED)
    cv.fill_poly([(mx + 10, my - 8), (mx + 26, my - 24), (mx + 34, my - 8)], INK)
    cv.fill_poly([(mx + 10, my + 8), (mx + 26, my + 24), (mx + 34, my + 8)], INK)
    cv.line(mx + 128, my, mx + 148, my - 14, GREY)
    cv.line(mx + 128, my, mx + 148, my + 14, GREY)


def ill_capitol(cv, x, y, w, h):
    """Capitol dome beside a bar chart showing 258 seats."""
    # dome, left: wider base, taller dome, clearer columns
    dx, dy = x + 56, y + h - 24
    cv.rect(dx - 38, dy - 36, 76, 36, INK)
    for i in range(5):
        cv.vline(dx - 28 + i * 14, dy - 34, dy - 4, PAPER, 3)
    cv.circle(dx, dy - 36, 30, INK, fill=True)
    cv.rect(dx - 30, dy - 38, 60, 6, INK)
    cv.rect(dx - 3, dy - 56, 6, 12, INK)
    cv.circle(dx, dy - 58, 4, GOLD, fill=True)
    # bars, right: 258 of 435
    bx = x + 128
    base = y + h - 24
    cv.hline(bx - 8, x + w - 10, base, INK, 2)
    cv.rect(bx, base - 78, 26, 78, BLUE)       # democrats
    cv.rect(bx + 34, base - 52, 26, 52, RED)   # republicans
    cv.rect(bx + 68, base - 12, 26, 12, GREY)  # uncalled
    draw_text(cv, bx - 2, base - 96, "258", 2, BLUE)


def ill_tennis(cv, x, y, w, h):
    """Tennis court, ball and trophy."""
    # court, left two thirds
    cx, cy, cw, chh = x + 8, y + 10, w - 110, h - 20
    cv.rect(cx, cy, cw, chh, DARK_GREEN)
    cv.rect(cx + 6, cy + 6, cw - 12, chh - 12, PAPER)
    cv.rect(cx + 10, cy + 10, cw - 20, chh - 20, DARK_GREEN)
    cv.line(cx + cw // 2, cy + 10, cx + cw // 2, cy + chh - 10, PAPER)
    cv.line(cx + 10, cy + chh // 2, cx + cw - 10, cy + chh // 2, PAPER)
    cv.circle(cx + cw // 2, cy + chh // 2, 8, GOLD, fill=True)
    # trophy, right
    tx = x + w - 78
    ty = y + 14
    cv.fill_poly([(tx, ty), (tx + 34, ty), (tx + 28, ty + 34),
                  (tx + 6, ty + 34)], GOLD)
    cv.line(tx - 4, ty + 6, tx - 14, ty + 18, GOLD)
    cv.line(tx + 38, ty + 6, tx + 48, ty + 18, GOLD)
    cv.rect(tx + 14, ty + 34, 6, 16, GOLD)
    cv.rect(tx + 4, ty + 50, 26, 8, GOLD)
    cv.rect(tx, ty + 58, 34, 6, INK)


# ---------------------------------------------------------------- layout

def draw_panel(cv, x, y, w, h, kicker, headline, deck, ill):
    cv.rect(x, y, w, h, PAPER)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    pad = 14
    ix, iy = x + pad, y + 12
    draw_text(cv, ix, iy, kicker, 2, RED)
    iy += 22
    hl = wrap_text(headline, 3, w - 2 * pad)
    iy = draw_block(cv, ix, iy, hl[:2], 3, INK, leading=24)
    iy += 8
    dk = wrap_text(deck, 2, w - 2 * pad)
    iy = draw_block(cv, ix, iy, dk[:4], 2, INK, leading=17)
    iy += 10
    ill_h = y + h - 12 - iy
    if ill_h > 40:
        ill(cv, x + pad, iy, w - 2 * pad, ill_h)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)

    # masthead
    title = "THE WORLD TODAY"
    tw = text_width(title, 8)
    draw_text(cv, (W - tw) // 2, 26, title, 8, INK)
    cv.hline(28, 996, 92, INK, 4)
    cv.hline(28, 996, 100, INK, 1)
    date = "MONDAY 23 NOVEMBER 2026"
    dw = text_width(date, 3)
    draw_text(cv, (W - dw) // 2, 110, date, 3, RED)
    cv.hline(28, 996, 138, INK, 1)

    # ---- lead story: COP31
    lx, ly, lw, lh = 28, 150, 968, 244
    cv.rect(lx, ly, lw, lh, PAPER)
    cv.rect(lx, ly, lw, 2, INK)
    cv.rect(lx, ly + lh - 2, lw, 2, INK)
    cv.rect(lx, ly, 2, lh, INK)
    cv.rect(lx + lw - 2, ly, 2, lh, INK)
    tx = lx + 18
    ty = ly + 14
    draw_text(cv, tx, ty, "CLIMATE - FIRST COLLAPSE SINCE 2009", 2, RED)
    ty += 24
    lead_head = wrap_text(
        "COP31 COLLAPSES AS EU REJECTS DEAL WITH NO FOSSIL FUEL PHASE-OUT",
        4, 560)
    ty = draw_block(cv, tx, ty, lead_head[:3], 4, INK, leading=30)
    ty += 8
    lead_deck = wrap_text(
        "TALKS IN ANTALYA END WITH NO DEAL AFTER TWO WEEKS. THE EU AND UK "
        "REFUSED A TEXT THAT NEVER MENTIONED FOSSIL FUELS.", 3, 560)
    draw_block(cv, tx, ty, lead_deck[:4], 3, INK, leading=24)
    ill_globe(cv, lx + 600, ly + 14, 350, lh - 28)

    # ---- grid: 2 rows x 3 columns
    gx, gy = 28, 406
    gw, gh, gap = 312, 286, 14
    panels = [
        ("THE GULF", "TANKERS ABLAZE IN HORMUZ",
         "IRAN SAYS TWO SUPERTANKERS HIT MINES ON SUNDAY. A SIXTH WAS "
         "REPORTED HIT ON MONDAY.", ill_tanker),
        ("LIBYA", "RUSSIAN WARSHIP SUNK IN BENGHAZI",
         "SEA DRONES HIT THE CORVETTE MERKURY AT DAWN. IT CAPSIZED. TEN "
         "PEOPLE WERE HURT.", ill_ship_sunk),
        ("UKRAINE", "DRONE FLATTENS FLATS NEAR KYIV",
         "NINE KILLED IN DYMER AS RESCUERS DIG ON. ELEVEN STILL MISSING, "
         "TWO OF THEM CHILDREN.", ill_building),
        ("EUROPE", "ALL THREE WERE RUSSIAN MISSILES",
         "PROSECUTORS CONFIRM ALL THREE WERE KH-101 MISSILES. NATO "
         "COUNCIL MEETS TODAY.", ill_missile),
        ("UNITED STATES", "DEMOCRATS TAKE 258 HOUSE SEATS",
         "CHUCK HUBBARD'S WIN IN NORTH CAROLINA GIVES DEMOCRATS 258 "
         "SEATS, THE MOST SINCE 1992.", ill_capitol),
        ("SPORT", "ALCARAZ WINS FIRST ATP FINALS",
         "BEATS WORLD NO. 1 ZVEREV 6-2, 7-6 IN TURIN. FOURTH MAN TO HOLD "
         "ALL FOUR SLAMS AND THIS CROWN.", ill_tennis),
    ]
    for i, (kicker, head, deck, ill) in enumerate(panels):
        px = gx + (i % 3) * (gw + gap)
        py = gy + (i // 3) * (gh + gap)
        draw_panel(cv, px, py, gw, gh, kicker, head, deck, ill)

    # footer
    foot = "SOURCES: CNN, REUTERS, AP, ATP TOUR. STORIES VERIFIED FOR 23 NOVEMBER 2026"
    fw = text_width(foot, 2)
    draw_text(cv, (W - fw) // 2, 1000, foot, 2, GREY)

    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += cv.px[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png)} bytes)")


if __name__ == "__main__":
    main()
