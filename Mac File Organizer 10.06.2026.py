#!/usr/bin/env python3
# Mac File Organizer
# Version 10.06.2026
#
# Scans folders on a Mac, builds an approval spreadsheet, applies the approved plan,
# verifies the result, and can undo a run. Standard library only. The openpyxl package
# is optional and is used only for the .xlsx spreadsheet.
#
# Subcommands
#   scan     Inventory one or more folders. Writes Inventory JSON and Plan CSV.
#   check    Validate a filled plan. Touches no file.
#   sheet    Convert Plan CSV to .xlsx for approval, or an approved .xlsx back to CSV.
#   apply    Execute an approved plan. Dry run by default. Add --execute to move files.
#   verify   Audit the organized root for naming and placement violations.
#   undo     Reverse a change log written by apply.
#
# Rules enforced
#   Main folders are 001 Inbox, 002 Personal, 003 Work, 004 Reference, 005 To Be Printed, 006 Trash.
#   Every file name starts with the three digit code of its main folder.
#   Work files carry the company name right after the code.
#   Every file name ends with the last modified date as MM.DD.YYYY before the extension.
#   No dashes and no underscores anywhere in a folder or file name.
#   Nothing is deleted. Unwanted files move to 006 Trash.

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

VERSION = "10.06.2026"

MAIN_FOLDERS = [
    "001 Inbox",
    "002 Personal",
    "003 Work",
    "004 Reference",
    "005 To Be Printed",
    "006 Trash",
]
WORK_FOLDERS = [
    "001 Bukrah Foundation",
    "002 Stories from Long Ago",
    "003 VampireTools",
    "004 Houston Apartments",
    "005 Safi Uncle",
    "006 Lubna",
    "007 Other Work",
]
COMPANY_SUBFOLDERS = [
    "001 Admin and Legal",
    "002 Finance",
    "003 Clients and Partners",
    "004 Build",
    "005 Marketing",
]
TRASH_FOLDER = "006 Trash"
PRINT_FOLDER = "005 To Be Printed"
INBOX_FOLDER = "001 Inbox"
WORK_FOLDER = "003 Work"
OTHER_WORK_FOLDER = "007 Other Work"
DUPLICATES_FOLDER = TRASH_FOLDER + "/001 Duplicates"

ACTIONS = ["move", "trash", "print", "skip"]

PLAN_COLUMNS = [
    "id", "action", "new folder", "new name", "current name", "current path", "kind",
    "ext", "size kb", "modified", "stamp", "duplicate of", "flags", "snippet", "notes",
]
LOG_COLUMNS = ["id", "action", "old path", "new path", "status", "note"]

SKIP_NAMES = {".DS_Store", ".localized", "Icon\r", "Thumbs.db", "desktop.ini"}
SKIP_DIR_NAMES = {"Library", "Applications", "node_modules", ".Trash", ".tmp.driveupload", "ScanSnap Home folder"}
BUNDLE_EXTS = {
    ".app", ".photoslibrary", ".musiclibrary", ".tvlibrary", ".aplibrary", ".bundle",
    ".framework", ".xcodeproj", ".xcworkspace", ".playground", ".pages", ".numbers",
    ".key", ".sketch", ".logicx", ".band", ".fcpbundle", ".imovielibrary", ".pkg",
    ".mpkg", ".workflow", ".scptd", ".rtfd", ".download", ".keynote", ".pxd",
    ".afdesign", ".afphoto", ".procreate", ".textbundle",
}
PROJECT_MARKERS = {
    ".git", ".hg", ".svn", "package.json", "pyproject.toml", "setup.py", "Package.swift",
    "Cargo.toml", "go.mod", "Gemfile", "composer.json", "requirements.txt", "Makefile",
    "CMakeLists.txt", "build.gradle", "pom.xml", ".xcodeproj", "Podfile", "pubspec.yaml",
    "mix.exs", "deno.json", "bun.lockb", "yarn.lock", "pnpm-lock.yaml",
}
INSTALLER_EXTS = {".dmg", ".pkg", ".mpkg", ".exe", ".msi", ".iso", ".xip"}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".bz2", ".xz"}
TEMP_EXTS = {".tmp", ".part", ".crdownload", ".download", ".partial", ".bak", ".swp"}
PLAIN_TEXT_EXTS = {
    ".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".log", ".xml", ".yaml", ".yml",
    ".ini", ".cfg", ".tex", ".eml", ".vcf", ".ics",
}
TEXTUTIL_EXTS = {".rtf", ".doc", ".docx", ".odt", ".html", ".htm", ".webarchive"}
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".tif", ".tiff", ".bmp", ".webp",
    ".svg", ".psd", ".ai", ".raw", ".cr2", ".dng",
}
MEDIA_EXTS = {".mov", ".mp4", ".m4v", ".avi", ".mkv", ".mp3", ".m4a", ".wav", ".aac", ".flac"}
SCREENSHOT_RE = re.compile(r"^(Screen ?Shot|Screenshot|Screen Recording|Simulator Screenshot|CleanShot|Capture d.écran)", re.I)
OFFICE_LOCK_RE = re.compile(r"^~\$")

STAMP_RE = re.compile(r"(^|\s)\d{2}\.\d{2}\.\d{4}$")
UNIT_NAME_RE = re.compile(r"^\d{3} .+ \d{2}\.\d{2}\.\d{4}$")
CONTAINER_NAME_RE = re.compile(r"^\d{3} \S.*$")
FOLDER_COMPONENT_RE = re.compile(r"^\d{3} [^-_/\\:*?\"<>|\x00-\x1f]+$")
BAD_CHARS_RE = re.compile(r"[-_/\\:*?\"<>|\x00-\x1f]")
MAX_NAME_LEN = 200
FULL_HASH_LIMIT = 256 * 1024 * 1024
SNIPPET_CSV_LEN = 400
SNIPPET_JSON_LEN = 3000


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def norm(s):
    return unicodedata.normalize("NFC", s or "")


CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_spaces(s):
    return re.sub(r"\s+", " ", CONTROL_RE.sub(" ", s)).strip()


def today_stamp():
    return dt.date.today().strftime("%m.%d.%Y")


def now_tag():
    return dt.datetime.now().strftime("%m.%d.%Y %H%M")


def stamp_from_mtime(mtime):
    return dt.datetime.fromtimestamp(mtime).strftime("%m.%d.%Y")


def iso_from_time(t):
    if t is None:
        return ""
    return dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def unique_path(path):
    """Return path, or path with a run number inserted before the extension if it exists."""
    path = Path(path)
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem} {n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def say(msg):
    print(msg, flush=True)


def warn(msg):
    print("WARNING: " + msg, file=sys.stderr, flush=True)


def die(msg, code=1):
    print("ERROR: " + msg, file=sys.stderr, flush=True)
    sys.exit(code)


def run_cmd(args, timeout=30):
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=timeout, errors="replace")
        if out.returncode != 0:
            return ""
        return out.stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def main_code(folder_name):
    return folder_name[:3]


def folder_code_and_label(component):
    return component[:3], component[4:]


# ---------------------------------------------------------------------------
# Hashing and text extraction
# ---------------------------------------------------------------------------

def hash_file(path, size):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if size <= FULL_HASH_LIMIT:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
                return h.hexdigest()
            h.update(str(size).encode())
            h.update(f.read(4 * 1024 * 1024))
            f.seek(max(0, size - 4 * 1024 * 1024))
            h.update(f.read(4 * 1024 * 1024))
            return "partial:" + h.hexdigest()
    except OSError:
        return ""


def strip_tags(xml_text):
    text = re.sub(r"<[^>]+>", " ", xml_text)
    return clean_spaces(html.unescape(text))


def text_from_zip_member(path, member_patterns, limit):
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            out = []
            for pattern in member_patterns:
                rx = re.compile(pattern)
                for name in sorted(names):
                    if rx.match(name):
                        with z.open(name) as fh:
                            raw = fh.read(2 * 1024 * 1024).decode("utf-8", errors="ignore")
                        out.append(strip_tags(raw))
                        if sum(len(x) for x in out) > limit:
                            return " ".join(out)[:limit]
            return " ".join(out)[:limit]
    except (zipfile.BadZipFile, OSError, RuntimeError):
        return ""


def text_from_pdf(path, limit):
    reader_cls = None
    import logging
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    logging.getLogger("PyPDF2").setLevel(logging.ERROR)
    try:
        from pypdf import PdfReader as reader_cls  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader as reader_cls  # type: ignore
        except ImportError:
            reader_cls = None
    if reader_cls is not None:
        try:
            reader = reader_cls(str(path))
            parts = []
            for page in reader.pages[:3]:
                parts.append(page.extract_text() or "")
                if sum(len(p) for p in parts) > limit:
                    break
            text = clean_spaces(" ".join(parts))
            if text:
                return text[:limit]
        except Exception:
            pass
    if shutil.which("pdftotext"):
        text = run_cmd(["pdftotext", "-l", "3", "-layout", str(path), "-"], timeout=60)
        return clean_spaces(text)[:limit]
    return ""


def text_from_textutil(path, limit):
    if shutil.which("textutil"):
        text = run_cmd(["textutil", "-convert", "txt", "-stdout", str(path)], timeout=60)
        if text.strip():
            return clean_spaces(text)[:limit]
    return ""


def extract_text(path, ext, limit):
    try:
        if ext in PLAIN_TEXT_EXTS:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return clean_spaces(f.read(limit * 2))[:limit]
        if ext == ".pdf":
            return text_from_pdf(path, limit)
        if ext in TEXTUTIL_EXTS:
            text = text_from_textutil(path, limit)
            if text:
                return text
            if ext == ".docx":
                return text_from_zip_member(path, [r"word/document\.xml$"], limit)
            if ext == ".odt":
                return text_from_zip_member(path, [r"content\.xml$"], limit)
            if ext in (".html", ".htm"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return strip_tags(f.read(limit * 4))[:limit]
            return ""
        if ext == ".xlsx":
            return text_from_zip_member(path, [r"xl/sharedStrings\.xml$"], limit)
        if ext == ".pptx":
            return text_from_zip_member(path, [r"ppt/slides/slide\d+\.xml$"], limit)
    except OSError:
        return ""
    return ""


def spotlight_metadata(path):
    if not shutil.which("mdls"):
        return {}
    out = run_cmd([
        "mdls", "-name", "kMDItemKind", "-name", "kMDItemTitle", "-name", "kMDItemAuthors",
        "-name", "kMDItemContentCreationDate", "-name", "kMDItemWhereFroms", str(path),
    ], timeout=20)
    meta = {}
    for line in out.splitlines():
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if value in ("(null)", ""):
            continue
        value = value.strip('"')
        meta[key] = value[:300]
    return meta


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

def is_bundle(path):
    return path.suffix.lower() in BUNDLE_EXTS


def inside_new_structure(path, roots):
    """True when path is one of the six main folders under a scanned root, or sits inside one."""
    root, rel = relative_to_any(path, roots)
    return rel is not None and len(rel.parts) >= 1 and rel.parts[0] in MAIN_FOLDERS


def folder_is_empty(path):
    """True when a folder holds nothing but system junk, at any depth."""
    for root, dirs, files in os.walk(path):
        if any(f not in SKIP_NAMES and not f.startswith(".") for f in files):
            return False
    return True


def is_project(path):
    try:
        names = set(os.listdir(path))
    except OSError:
        return False
    for marker in PROJECT_MARKERS:
        if marker in names:
            return True
    for name in names:
        if name.endswith(".xcodeproj") or name.endswith(".xcworkspace"):
            return True
    return False


def folder_stats(path, limit=50000):
    """Total size and newest mtime inside a folder, bounded."""
    total = 0
    newest = 0.0
    count = 0
    top = []
    try:
        top = sorted(os.listdir(path))[:40]
    except OSError:
        pass
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "venv", ".venv", "build", "dist", "DerivedData")]
        for name in files:
            try:
                st = os.lstat(os.path.join(root, name))
            except OSError:
                continue
            total += st.st_size
            newest = max(newest, st.st_mtime)
            count += 1
            if count >= limit:
                return total, newest, count, top
    return total, newest, count, top


def readme_snippet(path, limit):
    for name in ("README.md", "README.txt", "README", "readme.md", "Readme.md"):
        candidate = Path(path) / name
        if candidate.is_file():
            try:
                with open(candidate, "r", encoding="utf-8", errors="ignore") as f:
                    return clean_spaces(f.read(limit * 2))[:limit]
            except OSError:
                return ""
    return ""


def relative_to_any(path, roots):
    for root in roots:
        try:
            return root, path.relative_to(root)
        except ValueError:
            continue
    return None, None


def scan_tree(root, excluded, items, roots, use_spotlight):
    """Walk root, appending items. Bundles and project folders are single items."""
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda e: e.name)
        except OSError as e:
            warn(f"cannot read {current}: {e}")
            continue
        for entry in entries:
            p = Path(entry.path)
            name = entry.name
            if any(p == ex or ex in p.parents for ex in excluded):
                continue
            if name in SKIP_NAMES or name.startswith("."):
                if name.endswith(".icloud") and name.startswith("."):
                    items.append(make_item(p, "icloud placeholder", roots, use_spotlight))
                continue
            try:
                is_link = entry.is_symlink()
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                continue
            if is_link:
                items.append(make_item(p, "symlink", roots, use_spotlight))
                continue
            if is_dir:
                if name in SKIP_DIR_NAMES:
                    continue
                if inside_new_structure(p, roots):
                    # Folders of the new structure are containers, never items. A container is
                    # named "001 Name" without a date stamp. A unit placed inside the structure
                    # (a bundle, a dated unit folder, or an unnamed project folder) is an item.
                    if is_bundle(p):
                        items.append(make_item(p, "bundle", roots, use_spotlight))
                    elif CONTAINER_NAME_RE.match(name) and not UNIT_NAME_RE.match(name):
                        stack.append(p)
                    elif UNIT_NAME_RE.match(name) or is_project(p):
                        items.append(make_item(p, "project folder", roots, use_spotlight))
                    else:
                        stack.append(p)
                    continue
                if is_bundle(p):
                    items.append(make_item(p, "bundle", roots, use_spotlight))
                    continue
                if is_project(p):
                    items.append(make_item(p, "project folder", roots, use_spotlight))
                    continue
                if folder_is_empty(p):
                    items.append(make_item(p, "empty folder", roots, use_spotlight))
                    continue
                stack.append(p)
                continue
            if OFFICE_LOCK_RE.match(name):
                items.append(make_item(p, "file", roots, use_spotlight, extra_flags=["temp file"]))
                continue
            items.append(make_item(p, "file", roots, use_spotlight))


def make_item(path, kind, roots, use_spotlight, extra_flags=None):
    flags = list(extra_flags or [])
    try:
        st = os.lstat(path)
    except OSError as e:
        return {"path": str(path), "name": path.name, "kind": kind, "flags": ["unreadable"], "error": str(e)}
    ext = path.suffix.lower() if kind in ("file", "bundle", "icloud placeholder") else ""
    if kind == "icloud placeholder":
        real_name = path.name[1:-len(".icloud")] if path.name.endswith(".icloud") else path.name
        ext = Path(real_name).suffix.lower()
    size = st.st_size
    mtime = st.st_mtime
    birth = getattr(st, "st_birthtime", None)
    digest = ""
    snippet = ""
    meta = {}
    if kind == "file":
        digest = hash_file(path, size)
        snippet = extract_text(path, ext, SNIPPET_JSON_LEN)
        if use_spotlight:
            meta = spotlight_metadata(path)
    elif kind == "project folder":
        size, newest, count, top = folder_stats(path)
        if newest:
            mtime = newest
        snippet = clean_spaces(f"Project folder with {count} files. Top level: " + ", ".join(top) + ". " + readme_snippet(path, 800))[:SNIPPET_JSON_LEN]
        flags.append("project folder")
    elif kind == "bundle":
        size, newest, count, top = folder_stats(path)
        if newest:
            mtime = newest
        snippet = f"Package with {count} inner files."
        flags.append("bundle")
        if ext in (".pkg", ".mpkg"):
            flags.append("installer")
        if use_spotlight:
            meta = spotlight_metadata(path)
    elif kind == "empty folder":
        flags.append("empty folder")
        snippet = "Folder with no files inside."
    elif kind == "icloud placeholder":
        flags.append("needs download")
    elif kind == "symlink":
        flags.append("symlink")

    name = path.name
    if kind == "file":
        if size == 0:
            flags.append("zero bytes")
        if ext in INSTALLER_EXTS:
            flags.append("installer")
        if ext in ARCHIVE_EXTS:
            flags.append("archive")
            stem = re.sub(r"\.(tar|zip|gz|tgz|rar|7z|bz2|xz)$", "", path.stem, flags=re.I)
            if stem and (path.parent / stem).is_dir():
                flags.append("archive extracted")
        if ext in TEMP_EXTS:
            flags.append("temp file")
        if SCREENSHOT_RE.match(name):
            flags.append("screenshot")
        if size > 500 * 1024 * 1024:
            flags.append("large")
        if ext in IMAGE_EXTS:
            flags.append("image")
        if ext in MEDIA_EXTS:
            flags.append("media")
        if not snippet and ext not in IMAGE_EXTS and ext not in MEDIA_EXTS:
            flags.append("needs read")

    root, rel = relative_to_any(path, roots)
    if rel is not None and len(rel.parts) >= 2:
        top = rel.parts[0]
        if top in MAIN_FOLDERS:
            folder = "/".join(rel.parts[:-1])
            errors, _ = validate_name(folder, path.name, stamp_from_mtime(mtime), ext, kind, action_for_top(top))
            if not errors:
                flags.append("already organized")
            else:
                flags.append("in new structure but misnamed")
        elif re.match(r"^\d{2,3}\s", top):
            flags.append("old structure")

    return {
        "path": str(path),
        "name": name,
        "kind": kind,
        "ext": ext,
        "size": size,
        "modified": iso_from_time(mtime),
        "mtime": mtime,
        "stamp": stamp_from_mtime(mtime),
        "created": iso_from_time(birth),
        "hash": digest,
        "snippet": snippet,
        "spotlight": meta,
        "flags": flags,
    }


def mark_duplicates(items):
    groups = {}
    for it in items:
        h = it.get("hash")
        if h and it["kind"] == "file" and it.get("size", 0) > 0:
            groups.setdefault(h, []).append(it)
    for h, group in groups.items():
        if len(group) < 2:
            continue

        def keeper_key(it):
            p = it["path"]
            in_downloads = "/Downloads/" in p
            return (in_downloads, "already organized" not in it["flags"], it["mtime"], len(p))

        group.sort(key=keeper_key)
        keeper = group[0]
        keeper["flags"].append("has duplicates")
        for other in group[1:]:
            other["flags"].append("duplicate")
            other["duplicate of"] = keeper["id"]


def suggest_action(it):
    f = set(it["flags"])
    if "already organized" in f:
        return "skip"
    if "needs download" in f or "symlink" in f or "unreadable" in f:
        return "skip"
    if f & {"duplicate", "installer", "zero bytes", "temp file", "archive extracted", "empty folder"}:
        return "trash"
    return ""


def cmd_scan(args):
    roots = []
    for r in args.folders:
        p = Path(os.path.expanduser(r)).resolve()
        if not p.is_dir():
            die(f"not a folder: {r}")
        roots.append(p)
    out_dir = Path(os.path.expanduser(args.out)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    excluded = {out_dir, Path(__file__).resolve().parent}
    for ex in args.exclude or []:
        excluded.add(Path(os.path.expanduser(ex)).resolve())

    items = []
    for root in roots:
        say(f"Scanning {root}")
        scan_tree(root, excluded, items, roots, not args.no_spotlight)
    items.sort(key=lambda it: it["path"])
    for i, it in enumerate(items, 1):
        it["id"] = f"F{i:05d}"
    mark_duplicates(items)
    for it in items:
        it["suggested action"] = suggest_action(it)

    stamp = today_stamp()
    inv_path = unique_path(out_dir / f"Inventory {stamp}.json")
    plan_path = unique_path(out_dir / f"Plan {stamp}.csv")
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": VERSION,
            "scanned": iso_from_time(dt.datetime.now().timestamp()),
            "roots": [str(r) for r in roots],
            "main folders": MAIN_FOLDERS,
            "work folders": WORK_FOLDERS,
            "company subfolders": COMPANY_SUBFOLDERS,
            "items": items,
        }, f, ensure_ascii=False, indent=1)
    with open(plan_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PLAN_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for it in items:
            w.writerow({
                "id": it["id"],
                "action": it.get("suggested action", ""),
                "new folder": "",
                "new name": "",
                "current name": it["name"],
                "current path": it["path"],
                "kind": it["kind"],
                "ext": it.get("ext", ""),
                "size kb": round(it.get("size", 0) / 1024, 1),
                "modified": it.get("modified", ""),
                "stamp": it.get("stamp", ""),
                "duplicate of": it.get("duplicate of", ""),
                "flags": ", ".join(it["flags"]),
                "snippet": (it.get("snippet") or "")[:SNIPPET_CSV_LEN],
                "notes": "",
            })

    kinds = {}
    flag_counts = {}
    for it in items:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
        for fl in it["flags"]:
            flag_counts[fl] = flag_counts.get(fl, 0) + 1
    say(f"Items found: {len(items)}")
    for k, v in sorted(kinds.items()):
        say(f"  {k}: {v}")
    say("Flags:")
    for k, v in sorted(flag_counts.items(), key=lambda kv: -kv[1]):
        say(f"  {k}: {v}")
    say(f"Inventory: {inv_path}")
    say(f"Plan: {plan_path}")


# ---------------------------------------------------------------------------
# Naming rules
# ---------------------------------------------------------------------------

def action_for_top(top):
    if top == TRASH_FOLDER:
        return "trash"
    if top == PRINT_FOLDER:
        return "print"
    return "move"


def parse_folder(folder):
    parts = [clean_spaces(norm(p)) for p in str(folder or "").replace("\\", "/").split("/")]
    return [p for p in parts if p]


def company_for(parts):
    """Company label for a Work path, or empty string."""
    if len(parts) >= 2 and parts[0] == WORK_FOLDER and parts[1] in WORK_FOLDERS and parts[1] != OTHER_WORK_FOLDER:
        return folder_code_and_label(parts[1])[1]
    return ""


def validate_folder(folder, action):
    parts = parse_folder(folder)
    errors = []
    warnings = []
    if not parts:
        return parts, ["new folder is empty"], warnings
    if str(folder or "").strip()[:1] in ("/", "\\", "~"):
        errors.append("new folder must be relative to the root, for example 002 Personal/001 Finance")
    for p in parts:
        if not FOLDER_COMPONENT_RE.match(p):
            errors.append(f"folder part '{p}' must look like '001 Name' with no dashes or underscores")
        if BAD_CHARS_RE.search(p):
            errors.append(f"folder part '{p}' has a forbidden character")
    if parts[0] not in MAIN_FOLDERS:
        errors.append(f"top folder '{parts[0]}' is not one of: " + ", ".join(MAIN_FOLDERS))
    if action == "trash" and parts[0] != TRASH_FOLDER:
        errors.append(f"action trash must go under {TRASH_FOLDER}")
    if action == "print" and parts[0] != PRINT_FOLDER:
        errors.append(f"action print must go under {PRINT_FOLDER}")
    if action == "move" and parts[0] == TRASH_FOLDER:
        errors.append("use action trash for files going to 006 Trash")
    if action == "move" and parts[0] == PRINT_FOLDER:
        errors.append("use action print for files going to 005 To Be Printed")
    if parts[0] == WORK_FOLDER:
        if len(parts) < 2:
            errors.append("Work files need a company folder, for example 003 Work/003 VampireTools/002 Finance")
        elif parts[1] not in WORK_FOLDERS:
            errors.append(f"company folder '{parts[1]}' is not one of: " + ", ".join(WORK_FOLDERS))
        elif len(parts) >= 3 and parts[1] != OTHER_WORK_FOLDER and parts[2] not in COMPANY_SUBFOLDERS:
            warnings.append(f"company subfolder '{parts[2]}' is not one of the standard five: " + ", ".join(COMPANY_SUBFOLDERS))
    return parts, errors, warnings


def normalize_description(raw, code, company, ext, stamp=""):
    """Strip code, company, stamp and extension if present, and clean forbidden characters.

    A trailing MM.DD.YYYY is removed only when it equals the row's stamp or when the name was
    typed in its full form starting with a code, so a description that ends in a real date keeps it.
    """
    s = clean_spaces(norm(raw))
    if ext and s.lower().endswith(ext.lower()):
        s = s[: -len(ext)]
    s = BAD_CHARS_RE.sub(" ", s)
    s = clean_spaces(s)
    all_codes = [main_code(m) for m in MAIN_FOLDERS]
    typed_in_full = any(s.startswith(c + " ") for c in all_codes)
    changed = True
    while changed and s:
        changed = False
        for c in all_codes:
            if s.startswith(c + " "):
                s, changed = s[len(c) + 1:].strip(), True
            elif s == c:
                s, changed = "", True
        if company and s.lower().startswith(company.lower() + " "):
            s, changed = s[len(company) + 1:].strip(), True
        elif company and s.lower() == company.lower():
            s, changed = "", True
    m = STAMP_RE.search(s)
    if m and (typed_in_full or m.group(0).strip() == stamp):
        s = s[: m.start()].strip()
    return clean_spaces(s)


def compose_name(folder_parts, raw_name, stamp, ext):
    code = main_code(folder_parts[0])
    company = company_for(folder_parts)
    desc = normalize_description(raw_name, code, company, ext, stamp)
    if not desc:
        return "", "new name has no description"
    pieces = [code]
    if company:
        pieces.append(company)
    pieces.append(desc)
    pieces.append(stamp)
    final = " ".join(pieces) + ext
    if len(final) > MAX_NAME_LEN:
        return final, f"name is longer than {MAX_NAME_LEN} characters"
    return final, ""


def validate_name(folder, name, stamp, ext, kind, action):
    """Validate an existing name against its folder. Returns (errors, warnings)."""
    errors = []
    warnings = []
    parts, folder_errors, folder_warnings = validate_folder(folder, action)
    errors.extend(folder_errors)
    warnings.extend(folder_warnings)
    if not parts or folder_errors:
        return errors, warnings
    name = norm(name)
    if BAD_CHARS_RE.search(name):
        errors.append("name has a dash, underscore, or other forbidden character")
    code = main_code(parts[0])
    if not name.startswith(code + " "):
        errors.append(f"name must start with '{code} '")
    company = company_for(parts)
    if company and not name.startswith(f"{code} {company} "):
        errors.append(f"Work file name must start with '{code} {company} '")
    base = name[: -len(ext)] if ext and name.lower().endswith(ext.lower()) else name
    if ext and not name.lower().endswith(ext.lower()):
        errors.append(f"name must keep the extension {ext}")
    if not re.search(r"\s" + re.escape(stamp) + r"$", base):
        errors.append(f"name must end with the modified date stamp {stamp}")
    if "  " in name or name != name.strip():
        errors.append("name has double or edge spaces")
    if len(name) > MAX_NAME_LEN:
        errors.append(f"name is longer than {MAX_NAME_LEN} characters")
    return errors, warnings


# ---------------------------------------------------------------------------
# Plan loading and checking
# ---------------------------------------------------------------------------

def load_plan(path):
    path = Path(os.path.expanduser(path))
    if not path.exists():
        die(f"plan not found: {path}")
    rows = []
    if path.suffix.lower() == ".xlsx":
        try:
            import openpyxl  # type: ignore
        except ImportError:
            die("reading .xlsx needs openpyxl. Install with: python3 -m pip install --user openpyxl  (or run: sheet --to-csv on a Mac that has it)")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb["Plan"] if "Plan" in wb.sheetnames else wb.worksheets[0]
        header = None
        for row in ws.iter_rows(values_only=True):
            if header is None:
                header = [str(c).strip() if c is not None else "" for c in row]
                continue
            rec = {}
            for key, val in zip(header, row):
                if not key:
                    continue
                rec[key] = "" if val is None else str(val)
            if any(v.strip() for v in rec.values()):
                rows.append(rec)
    else:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            for rec in csv.DictReader(f):
                rows.append({k: (v or "") for k, v in rec.items() if k is not None})
    for rec in rows:
        for col in PLAN_COLUMNS:
            rec.setdefault(col, "")
        rec["action"] = rec["action"].strip().lower()
        rec["new folder"] = clean_spaces(norm(rec["new folder"]))
        rec["new name"] = clean_spaces(norm(rec["new name"]))
        rec["stamp"] = normalize_stamp(rec["stamp"])
        rec["id"] = rec["id"].strip()
    return rows


def normalize_stamp(value):
    """Accept MM.DD.YYYY, or a date a spreadsheet app rewrote as YYYY-MM-DD or MM/DD/YYYY, with or without a time."""
    v = str(value or "").strip()
    if re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
        return v
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", v)
    if m:
        return f"{m.group(2)}.{m.group(3)}.{m.group(1)}"
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", v)
    if m:
        return f"{int(m.group(1)):02d}.{int(m.group(2)):02d}.{m.group(3)}"
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})", v)
    if m:
        return f"{int(m.group(1)):02d}.{int(m.group(2)):02d}.{m.group(3)}"
    return v


def plan_row_result(rec):
    """Compute the final destination for a plan row. Returns dict with errors and warnings."""
    res = {"errors": [], "warnings": [], "folder": "", "name": ""}
    action = rec["action"]
    if action == "" or action == "skip":
        return res
    if action not in ACTIONS:
        res["errors"].append(f"action '{action}' must be one of: " + ", ".join(ACTIONS))
        return res
    folder = rec["new folder"]
    if not folder:
        if action == "trash":
            folder = TRASH_FOLDER
        elif action == "print":
            folder = PRINT_FOLDER
    parts, errors, warnings = validate_folder(folder, action)
    res["errors"].extend(errors)
    res["warnings"].extend(warnings)
    if errors:
        return res
    kind = rec.get("kind", "file")
    ext = rec.get("ext", "")
    if kind in ("project folder", "empty folder"):
        ext = ""
    stamp = rec.get("stamp", "")
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", stamp or ""):
        res["errors"].append("stamp column is missing or not MM.DD.YYYY")
        return res
    raw = rec["new name"] or (Path(rec["current name"]).stem if action in ("trash", "print") else "")
    name, err = compose_name(parts, raw, stamp, ext)
    if err:
        res["errors"].append(err)
        return res
    res["folder"] = "/".join(parts)
    res["name"] = name
    return res


def check_plan(rows, quiet=False):
    """Validate all rows. Returns (results, error_count, warning_count, undecided_count)."""
    results = []
    destinations = {}
    errors = 0
    warnings = 0
    undecided = 0
    for rec in rows:
        res = plan_row_result(rec)
        if rec["action"] == "":
            undecided += 1
        if res["name"]:
            key = (res["folder"] + "/" + res["name"]).lower()
            if key in destinations:
                res["errors"].append(f"same destination as {destinations[key]}")
            else:
                destinations[key] = rec["id"]
        errors += len(res["errors"])
        warnings += len(res["warnings"])
        results.append(res)
        if not quiet:
            for e in res["errors"]:
                say(f"ERROR   {rec['id']}  {rec['current name']}  ->  {e}")
            for w in res["warnings"]:
                say(f"WARNING {rec['id']}  {rec['current name']}  ->  {w}")
    return results, errors, warnings, undecided


def cmd_check(args):
    rows = load_plan(args.plan)
    results, errors, warnings, undecided = check_plan(rows)
    counts = {}
    for rec, res in zip(rows, results):
        if res["name"]:
            top = res["folder"].split("/")[0]
            counts[top] = counts.get(top, 0) + 1
    say("")
    say(f"Rows: {len(rows)}   errors: {errors}   warnings: {warnings}   undecided: {undecided}   skip: {sum(1 for r in rows if r['action']=='skip')}")
    for k in MAIN_FOLDERS:
        if k in counts:
            say(f"  {k}: {counts[k]}")
    if errors:
        say("Fix every error before building the spreadsheet or applying.")
        sys.exit(1)
    say("Plan is valid.")


# ---------------------------------------------------------------------------
# Spreadsheet
# ---------------------------------------------------------------------------

def finalize_rows(rows):
    """Rewrite new folder and new name in place to their final composed form where valid."""
    results, errors, warnings, undecided = check_plan(rows, quiet=True)
    for rec, res in zip(rows, results):
        if res["name"]:
            rec["new folder"] = res["folder"]
            rec["new name"] = res["name"]
        if res["errors"]:
            rec["notes"] = clean_spaces((rec.get("notes", "") + " | " if rec.get("notes") else "") + "CHECK: " + "; ".join(res["errors"]))
    return errors, warnings, undecided


def write_plan_csv(rows, path):
    fieldnames = list(PLAN_COLUMNS)
    for rec in rows:
        for k in rec.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in rows:
            w.writerow(rec)


def cmd_sheet(args):
    src = Path(os.path.expanduser(args.plan))
    rows = load_plan(src)
    errors, warnings, undecided = finalize_rows(rows)
    if errors:
        warn(f"{errors} rows have errors. They are marked in the notes column. Fix them and run check.")
    if args.to_csv:
        out = Path(os.path.expanduser(args.out)) if args.out else src.with_suffix(".csv")
        out = unique_path(out) if out.resolve() != src.resolve() else out
        write_plan_csv(rows, out)
        say(f"CSV written: {out}")
        return
    try:
        import openpyxl  # type: ignore
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        die("building the .xlsx needs openpyxl. Install with: python3 -m pip install --user openpyxl")
    out = Path(os.path.expanduser(args.out)) if args.out else src.with_suffix(".xlsx")
    out = unique_path(out)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Plan"
    ws.append(PLAN_COLUMNS)
    for rec in rows:
        ws.append([CONTROL_RE.sub(" ", str(rec.get(c, ""))) for c in PLAN_COLUMNS])
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            if isinstance(cell.value, str):
                cell.data_type = "s"
    widths = {"id": 9, "action": 9, "new folder": 42, "new name": 70, "current name": 40, "current path": 50,
              "kind": 12, "ext": 7, "size kb": 9, "modified": 18, "stamp": 11, "duplicate of": 11,
              "flags": 24, "snippet": 60, "notes": 40}
    for i, col in enumerate(PLAN_COLUMNS, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(col, 14)
    head_font = Font(name="Arial", bold=True, size=11)
    body_font = Font(name="Arial", size=11)
    fill = PatternFill("solid", fgColor="DDEBF7")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = fill
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = body_font
            cell.alignment = Alignment(vertical="top", wrap_text=cell.column_letter in ("N", "O"))
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    dv = DataValidation(type="list", formula1='"' + ",".join(ACTIONS) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"B2:B{max(2, len(rows) + 1)}")

    rules = wb.create_sheet("Rules")
    rules.append(["Mac File Organizer rules " + VERSION])
    rules.append([])
    rules.append(["Main folders"])
    for m in MAIN_FOLDERS:
        rules.append([m])
    rules.append([])
    rules.append(["Work company folders under 003 Work"])
    for m in WORK_FOLDERS:
        rules.append([m])
    rules.append([])
    rules.append(["Standard subfolders inside every company"])
    for m in COMPANY_SUBFOLDERS:
        rules.append([m])
    rules.append([])
    rules.append(["Actions: move, trash, print, skip. Blank means not decided yet."])
    rules.append(["File names: code, company for Work, description with person and last 4 digits, period, modified date MM.DD.YYYY, extension."])
    rules.append(["No dashes and no underscores anywhere. Nothing is deleted, trash means moved to 006 Trash."])
    rules.column_dimensions["A"].width = 110
    for row in rules.iter_rows():
        for cell in row:
            cell.font = body_font
    wb.save(out)
    say(f"Spreadsheet written: {out}")
    say(f"Rows: {len(rows)}   errors: {errors}   warnings: {warnings}   undecided: {undecided}")


# ---------------------------------------------------------------------------
# Apply and undo
# ---------------------------------------------------------------------------

def same_content(a, b):
    try:
        sa, sb = os.stat(a), os.stat(b)
    except OSError:
        return False
    if sa.st_size != sb.st_size:
        return False
    return hash_file(a, sa.st_size) == hash_file(b, sb.st_size) != ""


def with_suffix_before_stamp(name, n, ext):
    base = name[: -len(ext)] if ext and name.lower().endswith(ext.lower()) else name
    m = re.search(r"\s(\d{2}\.\d{2}\.\d{4})$", base)
    if m:
        return f"{base[:m.start()]} {n} {m.group(1)}{ext}"
    return f"{base} {n}{ext}"


def write_log(path, entries):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        w.writeheader()
        for e in entries:
            w.writerow(e)


def prune_empty_dirs(dirs, protected, entries, root=None):
    """Remove directories that became empty, deepest first. Never removes protected paths or the new structure."""
    for d in sorted(set(dirs), key=lambda p: len(str(p)), reverse=True):
        current = d
        while current and current not in protected and current.is_dir():
            if root is not None and inside_new_structure(current, [root]):
                break
            if current.name in MAIN_FOLDERS:
                break
            try:
                names = os.listdir(current)
            except OSError:
                break
            junk = [n for n in names if n in SKIP_NAMES]
            if len(junk) != len(names):
                break
            for n in junk:
                try:
                    os.remove(current / n)
                except OSError:
                    pass
            try:
                os.rmdir(current)
                entries.append({"id": "", "action": "prune", "old path": str(current), "new path": "", "status": "removed empty folder", "note": ""})
            except OSError:
                break
            current = current.parent


def protected_folders(root):
    """Folders that prune must never remove: the root, its main folders, home and its direct children, iCloud Drive."""
    protected = {root, root.parent}
    for m in MAIN_FOLDERS:
        protected.add(root / m)
    home = Path(os.path.expanduser("~")).resolve()
    protected.add(home)
    try:
        for child in home.iterdir():
            if child.is_dir():
                protected.add(child.resolve())
    except OSError:
        pass
    icloud = home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
    if icloud.is_dir():
        protected.add(icloud.resolve())
        try:
            for child in icloud.iterdir():
                if child.is_dir():
                    protected.add(child.resolve())
        except OSError:
            pass
    return protected


def row_order(rec):
    """Trash and print rows run first so a slot vacated by them is free for the moves that follow."""
    return {"trash": 0, "print": 1}.get(rec["action"], 2)


def same_file(a, b):
    try:
        return os.path.samefile(a, b)
    except OSError:
        return False


def cmd_apply(args):
    root = Path(os.path.expanduser(args.root)).resolve()
    if not root.is_dir():
        die(f"root is not a folder: {root}")
    out_dir = Path(os.path.expanduser(args.out)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_plan(args.plan)
    results, errors, warnings, undecided = check_plan(rows, quiet=True)
    if errors:
        check_plan(rows)
        die(f"{errors} errors in the plan. Run check and fix them first.")
    if undecided and not args.allow_undecided:
        die(f"{undecided} rows still have a blank action. Decide them, or pass --allow-undecided to leave them where they are.")

    protected = protected_folders(root)
    for src_folder in args.source or []:
        protected.add(Path(os.path.expanduser(src_folder)).resolve())

    tag = now_tag()
    log_path = unique_path(out_dir / (f"Change Log {tag}.csv" if args.execute else f"Apply Preview {tag}.csv"))
    log_file = open(log_path, "w", encoding="utf-8", newline="")
    log_writer = csv.DictWriter(log_file, fieldnames=LOG_COLUMNS)
    log_writer.writeheader()
    log_file.flush()

    entries = []
    source_dirs = []
    moved = 0

    def record(entry):
        entries.append(entry)
        log_writer.writerow(entry)
        log_file.flush()

    ordered = sorted(zip(rows, results), key=lambda pair: row_order(pair[0]))
    try:
        for rec, res in ordered:
            if not res["name"]:
                continue
            src = Path(rec["current path"])
            entry = {"id": rec["id"], "action": rec["action"], "old path": str(src), "new path": "", "status": "", "note": ""}
            if not src.exists() and not src.is_symlink():
                entry["status"] = "missing"
                record(entry)
                continue
            if rec.get("kind") == "icloud placeholder" or src.name.endswith(".icloud"):
                entry["status"] = "skipped"
                entry["note"] = "iCloud placeholder, download it first"
                record(entry)
                continue
            if src.resolve() in protected or src.resolve() == root or src.resolve() in root.parents:
                entry["status"] = "error"
                entry["note"] = "refusing to move a protected folder"
                record(entry)
                continue
            if rec.get("kind") == "empty folder" and not folder_is_empty(src):
                entry["status"] = "skipped"
                entry["note"] = "folder is no longer empty, rescan before moving it"
                record(entry)
                continue
            try:
                st = os.lstat(src)
            except OSError as e:
                entry["status"] = "error"
                entry["note"] = str(e)
                record(entry)
                continue
            live_stamp = stamp_from_mtime(st.st_mtime)
            if rec.get("kind") in ("project folder", "bundle"):
                _, newest, _, _ = folder_stats(src)
                if newest:
                    live_stamp = stamp_from_mtime(newest)
            ext = rec.get("ext", "") if rec.get("kind") not in ("project folder", "empty folder") else ""
            name = res["name"]
            if live_stamp != rec.get("stamp"):
                name = with_stamp(name, live_stamp, ext)
                entry["note"] = f"modified after scan, stamp updated to {live_stamp}"
            dest_dir = root / res["folder"]
            dest = dest_dir / name
            if dest.exists() and same_file(src, dest):
                # Same file already at the destination. Either nothing changes, or only the
                # spelling of the name changes on a case insensitive disk, which is an in place rename.
                if dest.name == src.name and dest.parent.resolve() == src.parent.resolve():
                    entry["status"] = "unchanged"
                    entry["new path"] = str(dest)
                    record(entry)
                    continue
                entry["new path"] = str(dest)
                if args.execute:
                    try:
                        os.rename(src, dest)
                        entry["status"] = "renamed"
                        moved += 1
                    except OSError as e:
                        entry["status"] = "error"
                        entry["note"] = clean_spaces(entry["note"] + " " + str(e))
                else:
                    entry["status"] = "would rename"
                record(entry)
                continue
            if src.is_dir() and not src.is_symlink() and src.resolve() in dest.resolve().parents:
                entry["status"] = "error"
                entry["new path"] = str(dest)
                entry["note"] = "destination is inside the folder being moved"
                record(entry)
                continue
            if dest.exists():
                if src.is_file() and dest.is_file() and same_content(src, dest):
                    dest_dir = root / DUPLICATES_FOLDER
                    dup_parts = parse_folder(DUPLICATES_FOLDER)
                    desc = normalize_description(name, main_code(res["folder"]), company_for(parse_folder(res["folder"])), ext, live_stamp)
                    name, _ = compose_name(dup_parts, desc, live_stamp, ext)
                    dest = dest_dir / name
                    entry["note"] = clean_spaces(entry["note"] + " identical file already at destination, sent to duplicates")
                n = 2
                while dest.exists():
                    dest = dest_dir / with_suffix_before_stamp(name, n, ext)
                    n += 1
            entry["new path"] = str(dest)
            if args.execute:
                try:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dest))
                    entry["status"] = "moved"
                    moved += 1
                    source_dirs.append(src.parent)
                except OSError as e:
                    entry["status"] = "error"
                    entry["note"] = clean_spaces(entry["note"] + " " + str(e))
            else:
                entry["status"] = "would move"
            record(entry)

        if args.execute and args.prune_empty:
            pruned = []
            prune_empty_dirs(source_dirs, protected, pruned, root)
            for e in pruned:
                record(e)
    finally:
        log_file.close()

    status_counts = {}
    for e in entries:
        status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1
    say("Dry run. Nothing moved. Add --execute to move files." if not args.execute else f"Done. Files moved or renamed: {moved}")
    for k, v in sorted(status_counts.items()):
        say(f"  {k}: {v}")
    for e in entries[: args.show]:
        say(f"  {e['status']:10} {e['old path']}  ->  {e['new path']}")
    if len(entries) > args.show:
        say(f"  ... {len(entries) - args.show} more rows in the log")
    say(("Change log: " if args.execute else "Preview: ") + str(log_path))
    if args.execute:
        say(f"To reverse this run:  undo \"{log_path}\" --execute")


def with_stamp(name, stamp, ext):
    base = name[: -len(ext)] if ext and name.lower().endswith(ext.lower()) else name
    base = STAMP_RE.sub("", base).strip()
    return f"{base} {stamp}{ext}"


def cmd_undo(args):
    log_path = Path(os.path.expanduser(args.log))
    if not log_path.exists():
        die(f"log not found: {log_path}")
    with open(log_path, "r", encoding="utf-8-sig", newline="") as f:
        entries = list(csv.DictReader(f))
    out_dir = log_path.parent
    results = []
    restored = 0
    created_dirs = []
    for e in reversed(entries):
        if e.get("status") not in ("moved", "renamed"):
            continue
        new = Path(e["new path"])
        old = Path(e["old path"])
        r = {"id": e["id"], "action": "undo", "old path": str(new), "new path": str(old), "status": "", "note": ""}
        if not new.exists() and not new.is_symlink():
            r["status"] = "missing"
        elif old.exists() and not same_file(old, new):
            r["status"] = "blocked"
            r["note"] = "original path is occupied"
        elif args.execute:
            try:
                old.parent.mkdir(parents=True, exist_ok=True)
                if same_file(old, new):
                    os.rename(new, old)
                else:
                    shutil.move(str(new), str(old))
                r["status"] = "restored"
                restored += 1
                created_dirs.append(new.parent)
            except OSError as ex:
                r["status"] = "error"
                r["note"] = str(ex)
        else:
            r["status"] = "would restore"
        results.append(r)
    if args.execute:
        home = Path(os.path.expanduser("~")).resolve()
        protected = {home}
        try:
            protected.update(c.resolve() for c in home.iterdir() if c.is_dir())
        except OSError:
            pass
        prune_empty_dirs(created_dirs, protected, results)
    undo_log = unique_path(out_dir / f"Undo Log {now_tag()}.csv")
    write_log(undo_log, results)
    say(("Dry run. Nothing restored. Add --execute to restore." if not args.execute else f"Restored: {restored}"))
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    for k, v in sorted(counts.items()):
        say(f"  {k}: {v}")
    say(f"Undo log: {undo_log}")


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

def cmd_verify(args):
    root = Path(os.path.expanduser(args.root)).resolve()
    if not root.is_dir():
        die(f"root is not a folder: {root}")
    out_dir = Path(os.path.expanduser(args.out)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    excluded = {out_dir, Path(__file__).resolve().parent}
    for ex in args.exclude or []:
        excluded.add(Path(os.path.expanduser(ex)).resolve())
    items = []
    scan_tree(root, excluded, items, [root], use_spotlight=False)
    report = []
    per_folder = {}
    ok = 0
    for it in items:
        p = Path(it["path"])
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        top = rel.parts[0] if rel.parts else ""
        per_folder[top] = per_folder.get(top, 0) + 1
        if top not in MAIN_FOLDERS:
            report.append({"path": str(p), "problem": "outside the six main folders"})
            continue
        if len(rel.parts) < 2:
            report.append({"path": str(p), "problem": "file sits directly in the root"})
            continue
        folder = "/".join(rel.parts[:-1])
        ext = it.get("ext", "") if it["kind"] not in ("project folder", "empty folder") else ""
        if it["kind"] == "icloud placeholder":
            report.append({"path": str(p), "problem": "iCloud placeholder, not downloaded"})
            continue
        errors, _ = validate_name(folder, p.name, it["stamp"], ext, it["kind"], "move" if top not in (TRASH_FOLDER, PRINT_FOLDER) else ("trash" if top == TRASH_FOLDER else "print"))
        if errors:
            for e in errors:
                report.append({"path": str(p), "problem": e})
        else:
            ok += 1
    for missing in missing_skeleton(root):
        report.append({"path": str(missing), "problem": "skeleton folder is missing, run init"})
    report_path = unique_path(out_dir / f"Verify Report {now_tag()}.csv")
    with open(report_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "problem"])
        w.writeheader()
        for r in report:
            w.writerow(r)
    say(f"Items checked: {len(items)}   correct: {ok}   problems: {len(report)}")
    for k in MAIN_FOLDERS:
        say(f"  {k}: {per_folder.get(k, 0)}")
    strays = {k: v for k, v in per_folder.items() if k not in MAIN_FOLDERS}
    for k, v in sorted(strays.items()):
        say(f"  outside structure  {k or '(root)'}: {v}")
    for r in report[: args.show]:
        say(f"  {r['problem']}  <-  {r['path']}")
    if len(report) > args.show:
        say(f"  ... {len(report) - args.show} more in the report")
    say(f"Report: {report_path}")
    if report:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Skeleton
# ---------------------------------------------------------------------------

def skeleton_folders(root):
    """The six main folders and the company folders with their standard subfolders.
    Bukrah Foundation keeps its own inside structure, so only its company folder is listed."""
    out = [root / m for m in MAIN_FOLDERS]
    out.append(root / DUPLICATES_FOLDER)
    for company in WORK_FOLDERS:
        out.append(root / WORK_FOLDER / company)
        if company in (OTHER_WORK_FOLDER, "001 Bukrah Foundation"):
            continue
        for sub in COMPANY_SUBFOLDERS:
            out.append(root / WORK_FOLDER / company / sub)
    return out


def missing_skeleton(root):
    return [p for p in skeleton_folders(root) if not p.is_dir()]


def cmd_init(args):
    root = Path(os.path.expanduser(args.root)).resolve()
    if not root.is_dir():
        die(f"root is not a folder: {root}")
    created = 0
    for p in skeleton_folders(root):
        if not p.exists():
            p.mkdir(parents=True)
            created += 1
            say(f"  created {p.relative_to(root)}")
    say(f"Skeleton complete. Folders created: {created}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="Mac File Organizer " + VERSION)
    sub = p.add_subparsers(dest="command", required=True)
    default_out = "~/Organizer Working"

    s = sub.add_parser("scan", help="inventory folders and write the plan CSV")
    s.add_argument("folders", nargs="+", help="folders to scan, for example ~/Documents ~/Desktop ~/Downloads")
    s.add_argument("--out", default=default_out, help="working folder for outputs")
    s.add_argument("--exclude", action="append", help="folder to leave out, repeatable")
    s.add_argument("--no-spotlight", action="store_true", help="skip Spotlight metadata lookups, faster")
    s.set_defaults(func=cmd_scan)

    i = sub.add_parser("init", help="create the six main folders and the company skeleton")
    i.add_argument("--root", required=True, help="folder that holds the six main folders, for example ~/Documents")
    i.set_defaults(func=cmd_init)

    c = sub.add_parser("check", help="validate a filled plan")
    c.add_argument("plan", help="Plan CSV or .xlsx")
    c.set_defaults(func=cmd_check)

    sh = sub.add_parser("sheet", help="build the approval spreadsheet from a plan, or convert .xlsx back to CSV")
    sh.add_argument("plan", help="Plan CSV or .xlsx")
    sh.add_argument("--out", help="output path")
    sh.add_argument("--to-csv", action="store_true", help="convert an approved .xlsx back to CSV")
    sh.set_defaults(func=cmd_sheet)

    a = sub.add_parser("apply", help="execute an approved plan, dry run unless --execute")
    a.add_argument("plan", help="approved Plan CSV or .xlsx")
    a.add_argument("--root", required=True, help="folder that holds the six main folders, for example ~/Documents")
    a.add_argument("--out", default=default_out, help="working folder for logs")
    a.add_argument("--execute", action="store_true", help="move files for real")
    a.add_argument("--prune-empty", action="store_true", help="remove folders left empty after moving")
    a.add_argument("--source", action="append", help="a folder that was scanned, never removed by --prune-empty, repeatable")
    a.add_argument("--allow-undecided", action="store_true", help="proceed even if some rows have a blank action")
    a.add_argument("--show", type=int, default=25, help="rows to print")
    a.set_defaults(func=cmd_apply)

    v = sub.add_parser("verify", help="audit the organized root")
    v.add_argument("--root", required=True, help="folder that holds the six main folders")
    v.add_argument("--out", default=default_out, help="working folder for the report")
    v.add_argument("--show", type=int, default=40, help="problems to print")
    v.add_argument("--exclude", action="append", help="folder that keeps its own naming system and is not audited, repeatable")
    v.set_defaults(func=cmd_verify)

    u = sub.add_parser("undo", help="reverse a change log")
    u.add_argument("log", help="Change Log CSV written by apply --execute")
    u.add_argument("--execute", action="store_true", help="restore files for real")
    u.set_defaults(func=cmd_undo)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
