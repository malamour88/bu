#!/usr/bin/env python3
"""Inventory the measurable design values in a web project.

Scans CSS, SCSS, SASS, LESS, HTML, JSX, TSX, Vue, Svelte, and Astro files and
reports every font size, spacing value, transition, animation, and color
literal with file and line, so a design audit starts from data.

Usage:
  cssinventory.py PATH [PATH ...] [--rem 16] [--unit 4] [--max-ms 300] [--json]

Flags:
  --rem     px per rem/em for conversion (default 16)
  --unit    spacing base unit to check against (default 4)
  --max-ms  transitions longer than this are flagged (default 300)
  --json    emit machine readable output
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

EXTS = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".js", ".ts",
        ".vue", ".svelte", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "coverage",
             "vendor", ".svelte-kit", ".turbo", ".cache"}

LENGTH = r"(-?\d*\.?\d+)(px|rem|em|pt)"
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*" + LENGTH, re.IGNORECASE)
FONT_SHORT_RE = re.compile(r"\bfont\s*:\s*[^;{}]*?\b" + LENGTH + r"(?:/[\w.%]+)?\s+[\w\"', -]+", re.IGNORECASE)
TW_TEXT_RE = re.compile(r"\btext-\[" + LENGTH + r"\]")
SPACING_PROP_RE = re.compile(
    r"\b(margin(?:-(?:top|right|bottom|left|inline|block)(?:-(?:start|end))?)?|"
    r"padding(?:-(?:top|right|bottom|left|inline|block)(?:-(?:start|end))?)?|"
    r"gap|row-gap|column-gap|inset(?:-[a-z]+)?|top|right|bottom|left)\s*:\s*([^;{}]+)",
    re.IGNORECASE,
)
TW_SPACE_RE = re.compile(r"\b(?:[mp][trblxyse]?|gap(?:-[xy])?|space-[xy]|inset(?:-[xy])?)-\[" + LENGTH + r"\]")
LEN_IN_VALUE_RE = re.compile(LENGTH)
TRANSITION_RE = re.compile(r"\b(transition|animation)(?:-duration)?\s*:\s*([^;{}]+)", re.IGNORECASE)
DURATION_RE = re.compile(r"(-?\d*\.?\d+)(ms|s)\b")
EASING_RE = re.compile(r"(cubic-bezier\([^)]*\)|steps\([^)]*\)|linear|ease-in-out|ease-in|ease-out|ease)", re.IGNORECASE)
TW_DURATION_RE = re.compile(r"\bduration-(\d+|\[(\d*\.?\d+)(ms|s)\])")
TW_EASE_RE = re.compile(r"\bease-(linear|in-out|in|out|\[[^\]]+\])")
COLOR_RE = re.compile(
    r"(#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3,4}\b|"
    r"\b(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\([^)]*\))"
)
COLOR_PROP_RE = re.compile(
    r"(?:\b(color|background(?:-color)?|border(?:-[a-z]+)?(?:-color)?|fill|stroke|outline(?:-color)?|"
    r"box-shadow|text-shadow|backgroundColor|borderColor)|(?<![\w-])(--[\w-]+))\s*:\s*([^;{}]+)",
    re.IGNORECASE,
)
# React / JS style objects: fontSize: "44px", fontSize: 44, padding: "12px 24px", gap: 8
JS_FONT_RE = re.compile(r"\bfontSize\s*:\s*[\"']?(-?\d*\.?\d+)(px|rem|em|pt)?[\"']?")
JS_SPACE_RE = re.compile(
    r"\b(margin(?:Top|Right|Bottom|Left|Inline|Block)?|padding(?:Top|Right|Bottom|Left|Inline|Block)?|"
    r"gap|rowGap|columnGap)\s*:\s*([\"'][^\"']*[\"']|-?\d*\.?\d+(?=\s*(?:,|\}|$)))"
)


def to_px(num, unit, rem):
    v = float(num)
    if unit == "px":
        return v
    if unit in ("rem", "em"):
        return v * rem
    if unit == "pt":
        return v * 4 / 3
    return v


def fmt_px(v):
    return f"{v:g}px"


def iter_files(paths):
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() in EXTS:
                    yield os.path.join(dirpath, fn)


def scan(paths, rem, unit, max_ms):
    font_sizes = defaultdict(list)
    spacing = defaultdict(list)
    transitions = []
    colors = defaultdict(list)
    files_scanned = 0

    for path in iter_files(paths):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        files_scanned += 1
        for idx, line in enumerate(lines, 1):
            loc = f"{path}:{idx}"
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            for m in FONT_SIZE_RE.finditer(line):
                font_sizes[fmt_px(to_px(m.group(1), m.group(2), rem))].append(loc)
            for m in FONT_SHORT_RE.finditer(line):
                font_sizes[fmt_px(to_px(m.group(1), m.group(2), rem))].append(loc)
            for m in TW_TEXT_RE.finditer(line):
                font_sizes[fmt_px(to_px(m.group(1), m.group(2), rem))].append(loc)

            for m in SPACING_PROP_RE.finditer(line):
                prop, value = m.group(1), m.group(2)
                if "transition" in line.lower() and prop.lower() in ("top", "left", "right", "bottom"):
                    continue
                if value.lstrip().startswith(("\"", "'")):
                    continue  # JS style object; handled by JS_SPACE_RE below
                for lm in LEN_IN_VALUE_RE.finditer(value):
                    px = to_px(lm.group(1), lm.group(2), rem)
                    if px == 0:
                        continue
                    spacing[fmt_px(px)].append(f"{loc} ({prop})")
            for m in TW_SPACE_RE.finditer(line):
                spacing[fmt_px(to_px(m.group(1), m.group(2), rem))].append(f"{loc} (tailwind)")

            for m in TRANSITION_RE.finditer(line):
                kind, value = m.group(1).lower(), m.group(2).strip()
                durations = [float(d[0]) * (1000 if d[1] == "s" else 1) for d in DURATION_RE.findall(value)]
                easings = [e.lower() for e in EASING_RE.findall(value)]
                entry = {
                    "kind": kind,
                    "value": value,
                    "durations_ms": durations,
                    "easing": easings or ["(browser default: ease)"],
                    "location": loc,
                    "flags": [],
                }
                if kind == "transition" and re.match(r"^\s*all\b", value):
                    entry["flags"].append("transition: all")
                if durations and max(durations) > max_ms:
                    entry["flags"].append(f"over {max_ms}ms")
                if "linear" in easings:
                    entry["flags"].append("linear easing")
                transitions.append(entry)
            for m in TW_DURATION_RE.finditer(line):
                ms = float(m.group(2)) * (1000 if m.group(3) == "s" else 1) if m.group(2) else float(m.group(1))
                flags = [f"over {max_ms}ms"] if ms > max_ms else []
                transitions.append({"kind": "tailwind duration", "value": m.group(0), "durations_ms": [ms],
                                    "easing": ["(see ease-* class)"], "location": loc, "flags": flags})
            for m in TW_EASE_RE.finditer(line):
                if m.group(1) == "linear":
                    transitions.append({"kind": "tailwind easing", "value": m.group(0), "durations_ms": [],
                                        "easing": ["linear"], "location": loc, "flags": ["linear easing"]})

            for m in JS_FONT_RE.finditer(line):
                font_sizes[fmt_px(to_px(m.group(1), m.group(2) or "px", rem))].append(f"{loc} (js style)")
            for m in JS_SPACE_RE.finditer(line):
                prop, value = m.group(1), m.group(2).strip("\"'")
                if re.fullmatch(r"-?\d*\.?\d+", value):
                    px = float(value)
                    if px != 0:
                        spacing[fmt_px(px)].append(f"{loc} ({prop}, js style)")
                else:
                    for lm in LEN_IN_VALUE_RE.finditer(value):
                        px = to_px(lm.group(1), lm.group(2), rem)
                        if px != 0:
                            spacing[fmt_px(px)].append(f"{loc} ({prop}, js style)")

            for m in COLOR_PROP_RE.finditer(line):
                prop, value = (m.group(1) or m.group(2)), m.group(3)
                for cm in COLOR_RE.finditer(value):
                    colors[cm.group(1).upper() if cm.group(1).startswith("#") else cm.group(1)].append(f"{loc} ({prop})")

    return {
        "files_scanned": files_scanned,
        "font_sizes": font_sizes,
        "spacing": spacing,
        "transitions": transitions,
        "colors": colors,
    }


def sort_px(keys):
    return sorted(keys, key=lambda k: float(k[:-2]))


def report(data, unit, max_ms):
    out = []
    out.append(f"Files scanned: {data['files_scanned']}")

    fs = data["font_sizes"]
    out.append("")
    out.append(f"FONT SIZES ({len(fs)} distinct)")
    for k in sort_px(fs):
        locs = fs[k]
        out.append(f"  {k:>8}  x{len(locs):<3} {locs[0]}" + (f"  (+{len(locs)-1} more)" if len(locs) > 1 else ""))

    sp = data["spacing"]
    off = [k for k in sp if float(k[:-2]) % unit != 0]
    out.append("")
    out.append(f"SPACING ({len(sp)} distinct values, {len(off)} not on the {unit}px unit)")
    for k in sort_px(sp):
        locs = sp[k]
        mark = "  <-- off unit" if k in off else ""
        out.append(f"  {k:>8}  x{len(locs):<3} {locs[0]}" + (f"  (+{len(locs)-1} more)" if len(locs) > 1 else "") + mark)

    tr = data["transitions"]
    flagged = [t for t in tr if t["flags"]]
    out.append("")
    out.append(f"MOTION ({len(tr)} declarations, {len(flagged)} flagged: over {max_ms}ms, linear, or transition: all)")
    for t in tr:
        d = ", ".join(f"{x:g}ms" for x in t["durations_ms"]) or "no duration"
        flag = f"  <-- {'; '.join(t['flags'])}" if t["flags"] else ""
        out.append(f"  {t['location']}: {t['kind']}: {t['value']}  [{d}; {', '.join(t['easing'])}]{flag}")

    co = data["colors"]
    out.append("")
    out.append(f"COLORS ({len(co)} distinct literals)")
    for k in sorted(co, key=lambda c: (-len(co[c]), c)):
        locs = co[k]
        out.append(f"  {k:<28} x{len(locs):<3} {locs[0]}" + (f"  (+{len(locs)-1} more)" if len(locs) > 1 else ""))

    out.append("")
    out.append("Next: pair the text colors with their backgrounds and run contrast.py on each pair.")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("paths", nargs="+")
    p.add_argument("--rem", type=float, default=16.0)
    p.add_argument("--unit", type=float, default=4.0)
    p.add_argument("--max-ms", type=float, default=300.0)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    data = scan(args.paths, args.rem, args.unit, args.max_ms)
    if args.json:
        print(json.dumps(data, indent=2, default=list))
    else:
        print(report(data, args.unit, args.max_ms))
    return 0


if __name__ == "__main__":
    sys.exit(main())
