#!/usr/bin/env python3
"""WCAG 2.2 contrast ratio calculator for design audits.

Usage:
  contrast.py FG BG [--alpha A] [--size PX] [--bold] [--json]
  contrast.py --pairs FILE [--json]

Colors accept #RGB, #RRGGBB, #RRGGBBAA, rgb(), rgba(), hsl(), hsla().
--alpha blends the foreground onto the background at that opacity before
measuring, which is what text at 60% opacity actually looks like.
--pairs reads one "FG BG [alpha]" per line and reports all of them.
"""
import argparse
import colorsys
import json
import re
import sys

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
FUNC_RE = re.compile(r"^(rgba?|hsla?)\(([^)]*)\)$", re.IGNORECASE)


def parse_color(text):
    """Return (r, g, b, a) with channels 0..255 and alpha 0..1."""
    s = text.strip()
    m = HEX_RE.match(s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return r, g, b, a
    m = FUNC_RE.match(s)
    if not m:
        raise ValueError(f"unrecognized color: {text}")
    kind = m.group(1).lower()
    raw = re.split(r"[,\s/]+", m.group(2).strip())
    parts = [p for p in raw if p]
    if len(parts) < 3:
        raise ValueError(f"unrecognized color: {text}")

    def num(p, scale=255):
        p = p.strip()
        if p.endswith("%"):
            return float(p[:-1]) / 100 * scale
        return float(p)

    a = 1.0
    if len(parts) >= 4:
        a = num(parts[3], 1)
        if a > 1:
            a = a / 100
    if kind.startswith("rgb"):
        r, g, b = (num(parts[i]) for i in range(3))
        return r, g, b, a
    hue = float(parts[0].rstrip("deg")) % 360 / 360
    sat = num(parts[1], 1)
    lig = num(parts[2], 1)
    r, g, b = colorsys.hls_to_rgb(hue, lig, sat)
    return r * 255, g * 255, b * 255, a


def blend(fg, bg, alpha):
    """Composite fg over bg at the given alpha. Returns opaque rgb."""
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3))


def rel_luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg_rgb, bg_rgb):
    l1 = rel_luminance(fg_rgb)
    l2 = rel_luminance(bg_rgb)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def is_large_text(size_px, bold):
    """WCAG large text: 18pt (24px) or 14pt bold (18.66px)."""
    if size_px is None:
        return None
    return size_px >= 24 or (bold and size_px >= 18.66)


def to_hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(c)) for c in rgb)


def evaluate(fg_text, bg_text, alpha=None, size_px=None, bold=False):
    fg = parse_color(fg_text)
    bg = parse_color(bg_text)
    bg_rgb = bg[:3]
    if bg[3] < 1:
        bg_rgb = blend(bg[:3], (255, 255, 255), bg[3])
    effective_alpha = fg[3] if alpha is None else alpha
    fg_rgb = fg[:3]
    if effective_alpha < 1:
        fg_rgb = blend(fg[:3], bg_rgb, effective_alpha)
    r = ratio(fg_rgb, bg_rgb)
    large = is_large_text(size_px, bold)
    result = {
        "foreground": fg_text,
        "background": bg_text,
        "effective_foreground": to_hex(fg_rgb),
        "effective_background": to_hex(bg_rgb),
        "alpha": round(effective_alpha, 3),
        "ratio": round(r, 2),
        "passes_normal_text_4_5": r >= 4.5,
        "passes_large_text_3": r >= 3.0,
        "passes_ui_3": r >= 3.0,
        "passes_aaa_7": r >= 7.0,
    }
    if large is not None:
        result["text_size_px"] = size_px
        result["bold"] = bold
        result["classified_as"] = "large" if large else "normal"
        result["passes_for_this_text"] = r >= (3.0 if large else 4.5)
    return result


def fmt(res):
    lines = [
        f"{res['foreground']} on {res['background']}"
        + (f" at alpha {res['alpha']}" if res['alpha'] < 1 else ""),
        f"  effective: {res['effective_foreground']} on {res['effective_background']}",
        f"  ratio: {res['ratio']}:1",
        f"  normal text (4.5:1): {'PASS' if res['passes_normal_text_4_5'] else 'FAIL'}",
        f"  large text / UI (3:1): {'PASS' if res['passes_large_text_3'] else 'FAIL'}",
        f"  AAA (7:1): {'PASS' if res['passes_aaa_7'] else 'FAIL'}",
    ]
    if "classified_as" in res:
        lines.append(
            f"  this text ({res['text_size_px']}px{' bold' if res['bold'] else ''}, "
            f"{res['classified_as']}): {'PASS' if res['passes_for_this_text'] else 'FAIL'}"
        )
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fg", nargs="?", help="foreground (text) color")
    p.add_argument("bg", nargs="?", help="background color")
    p.add_argument("--alpha", type=float, help="foreground opacity 0..1, blended onto background first")
    p.add_argument("--size", type=float, help="text size in px, to classify normal vs large")
    p.add_argument("--bold", action="store_true", help="text is bold (700+)")
    p.add_argument("--pairs", help="file with one 'FG BG [alpha]' per line")
    p.add_argument("--json", action="store_true", help="emit JSON")
    args = p.parse_args(argv)

    results = []
    if args.pairs:
        with open(args.pairs, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#!") or line.startswith("//"):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                alpha = float(parts[2]) if len(parts) > 2 else None
                try:
                    results.append(evaluate(parts[0], parts[1], alpha))
                except ValueError as exc:
                    results.append({"error": str(exc), "line": line})
    elif args.fg and args.bg:
        results.append(evaluate(args.fg, args.bg, args.alpha, args.size, args.bold))
    else:
        p.print_help()
        return 2

    if args.json:
        print(json.dumps(results if len(results) > 1 or args.pairs else results[0], indent=2))
    else:
        for res in results:
            if "error" in res:
                print(f"ERROR {res['line']}: {res['error']}")
            else:
                print(fmt(res))
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
