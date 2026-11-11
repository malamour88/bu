#!/usr/bin/env python3
# Universal File Organizer, Mac script
# Version 11.11.2026
#
# Keeps the Mac filed under the same 001 to 006 system as Google Drive.
# Reads "Organizer Rules 11.11.2026.json" for folders, companies, keywords, and naming.
# Standard library only. Runs on the python3 that ships with the Command Line Tools.
#
# Commands
#   install     Copy the script and rules to ~/Library/Application Support, schedule a
#               daily run with launchd, and run once now.
#   run         Organize now. Add --preview to list the changes without making them.
#   undo LOG    Reverse every change recorded in one run log.
#   status      Show the schedule, the last run, and where the logs are.
#   uninstall   Remove the daily schedule. Files stay where they are.
#
# What one run does
#   1. Builds the 001 to 006 folders and their standard subfolders in ~/Documents.
#   2. Merges the old 00 to 99 folders in ~/Documents into the new folders.
#   3. Files loose items on the Desktop, in Downloads, at the top of Documents, at the
#      top of iCloud Drive, and in 001 Inbox. A match by keyword goes to its company or
#      personal folder with a name that follows the rule. No match goes to 001 Inbox.
#   4. Sends exact duplicates, checked by content fingerprint, to the Mac Trash.
#   5. Writes a log of every change to 004 Reference/010 Organizer Logs.
#
# Safety
#   Nothing is deleted. Duplicates go to the Mac Trash, where Put Back is not offered but
#   the undo command restores them. Folders with Bukrah, Claude, or OneDrive in the name,
#   code repos, and the keep list never move. Files changed in the last 15 minutes wait
#   for the next run. Files that are only in iCloud and not on this Mac are never read.

import csv
import datetime as dt
import hashlib
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

VERSION = "11.11.2026"
APP_NAME = "Universal File Organizer"
LAUNCH_LABEL = "com.alamour.universalfileorganizer"
RULES_NAME = "Organizer Rules 11.11.2026.json"
SCRIPT_NAME = "Mac Organizer 11.11.2026.py"
SF_DATALESS = 0x40000000
PARTIAL_SUFFIXES = (".crdownload", ".part", ".download", ".partial", ".tmp", ".icloud")
SKIP_FILE_NAMES = {".DS_Store", ".localized", "Icon\r", "desktop.ini", "Thumbs.db"}


# ----------------------------------------------------------------------------
# Naming. The Drive script carries the same logic in JavaScript. The tests run
# both on the same cases so the two never drift apart.
# ----------------------------------------------------------------------------

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DATE_PATTERNS = [
    ("ymd", re.compile(r"(?<!\d)((?:19|20)\d{2})[-_. ](\d{1,2})[-_. ](\d{1,2})(?!\d)")),
    ("mdy", re.compile(r"(?<!\d)(\d{1,2})[-_. ](\d{1,2})[-_. ]((?:19|20)\d{2})(?!\d)")),
    ("ymd", re.compile(r"(?<!\d)((?:19|20)\d{2})(\d{2})(\d{2})(?!\d)")),
    ("mdy8", re.compile(r"(?<!\d)(\d{2})(\d{2})((?:19|20)\d{2})(?!\d)")),
    ("mdy6", re.compile(r"(?<!\d)(\d{2})(\d{2})(\d{2})(?!\d)")),
    ("name", re.compile(
        r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+((?:19|20)\d{2})(?!\d)")),
]

ADDRESS_PATTERNS = [
    re.compile(r"(?i)\b\d{1,6}\s+(?:[a-z]+\s+){0,3}(?:street|st|avenue|ave|road|rd|drive|lane|ln|way|court|ct|circle|cir|"
               r"boulevard|blvd|place|pl|terrace|ter|trail|trl|parkway|pkwy|highway|hwy)\b"),
    re.compile(r"(?i)\b(?:apt|apartment|unit|suite)\s+\w+\b"),
]

SEPARATORS = re.compile(r"[_—–‒\-:;,|/\\()\[\]{}\"!?#*~<>]")
MAIN_CODE = re.compile(r"^00[1-6]\s+")
STAMP_AT_END = re.compile(r" \d{2}\.\d{2}\.\d{4}$")


def split_ext(name):
    m = re.match(r"^(.+)\.([A-Za-z0-9]{1,5})$", name)
    if m and not m.group(2).isdigit():
        return m.group(1), m.group(2)
    return name, ""


def extract_date(text):
    """Return (MM.DD.YYYY or None, text with that date removed)."""
    for kind, pattern in DATE_PATTERNS:
        for m in pattern.finditer(text):
            if kind == "ymd":
                y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            elif kind == "name":
                mo, d, y = MONTHS[m.group(1).lower()[:3]], int(m.group(2)), int(m.group(3))
            elif kind == "mdy6":
                mo, d, y = int(m.group(1)), int(m.group(2)), 2000 + int(m.group(3))
            else:
                mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1 <= mo <= 12 and 1 <= d <= 31:
                rest = text[:m.start()] + " " + text[m.end():]
                return "%02d.%02d.%04d" % (mo, d, y), rest
    return None, text


def normalize_words(text):
    """Lower case, drop accent and Arabic vowel marks, keep letters and digits of any script."""
    text = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if unicodedata.category(c) != "Mn")
    return " " + re.sub(r"[\W_]+", " ", text).strip() + " "


def match_rule(text, rules):
    norm = normalize_words(text)
    for rule in rules["rules"]:
        for kw in rule["keywords"]:
            if normalize_words(kw) in norm:
                return rule
    return None


def label_words(label):
    return re.sub(r"^\d{3}\s*", "", label).strip()


def fix_case(text, acronyms):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return text
    lower_all = all(c.islower() for c in letters)
    upper_all = all(c.isupper() for c in letters) and len(letters) > 3
    if not (lower_all or upper_all):
        return text
    keep = {a.upper() for a in acronyms}
    out = []
    for word in text.split(" "):
        if word.upper() in keep:
            out.append(word.upper())
        elif word:
            out.append(word[0].upper() + word[1:].lower())
    return " ".join(out)


def strip_prefixes(text, words):
    changed = True
    while changed:
        changed = False
        if MAIN_CODE.match(text):
            text = MAIN_CODE.sub("", text, count=1)
            changed = True
        for w in words:
            if not w:
                continue
            if text.lower() == w.lower():
                text = ""
                changed = True
            elif text.lower().startswith(w.lower() + " "):
                text = text[len(w) + 1:]
                changed = True
    return text.strip()


def clean_description(base, rule, rules):
    text = base.strip()
    copy = False
    m = re.match(r"(?i)^copy of\s+", text)
    if m:
        text = text[m.end():]
        copy = True
    date, text = extract_date(text)
    text = text.replace("&", " and ").replace("+", " and ")
    text = SEPARATORS.sub(" ", text)
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text).strip()
    words = []
    if rule:
        words.append(label_words(rule["label"]))
        words.extend(rule.get("strip", []))
    text = strip_prefixes(text, sorted(set(words), key=len, reverse=True))
    for pattern in ADDRESS_PATTERNS:
        text = pattern.sub(" ", text)
    for w in rules.get("blocked_words", []):
        if w:
            text = re.sub(r"(?i)\b" + re.escape(w) + r"\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = fix_case(text, rules.get("acronyms", []))
    if copy:
        text = (text + " Copy").strip()
    if re.match(r"(?i)^copy\s+", text):
        text = text[5:] + " Copy"
    return (text or "Untitled"), date


def conforms(name, label):
    base, _ = split_ext(name)
    if re.search(r"[_—–‒\-]", name):
        return False
    if not base.startswith(label + " "):
        return False
    return bool(STAMP_AT_END.search(base))


def build_name(name, rule, rules, fallback_date, label=None):
    """The rule compliant name for a file, or the same name when it already complies."""
    label = label or rule["label"]
    if conforms(name, label):
        return name
    base, ext = split_ext(name)
    desc, date = clean_description(base, rule, rules)
    parts = [label]
    if rule and rule.get("confidential") and "CONFIDENTIAL" not in desc.upper():
        parts.append("CONFIDENTIAL")
    parts.append(desc)
    parts.append(date or fallback_date)
    new = " ".join(parts)
    return new + ("." + ext.lower() if ext else "")


def with_counter(name, n):
    base, ext = split_ext(name)
    m = STAMP_AT_END.search(base)
    if m:
        base = base[:m.start()] + " " + str(n) + base[m.start():]
    else:
        base = base + " " + str(n)
    return base + ("." + ext if ext else "")


# ----------------------------------------------------------------------------
# Mac side
# ----------------------------------------------------------------------------

def home_path(p):
    return Path(os.path.expanduser(p))


def stamp(ts=None):
    d = dt.datetime.fromtimestamp(ts) if ts else dt.datetime.now()
    return d.strftime("%m.%d.%Y")


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def default_rules_path():
    here = Path(__file__).resolve().parent
    return here / RULES_NAME


class Run:
    def __init__(self, rules, preview):
        self.rules = rules
        self.preview = preview
        self.mac = rules["mac"]
        self.root = home_path(self.mac["root"])
        self.inbox = self.root / rules["inbox"]
        self.trash = home_path("~/.Trash")
        self.protected = [w.lower() for w in rules.get("protected_folder_names_contain", [])]
        self.keep = set(self.mac.get("keep_in_place", []))
        self.cutoff = dt.datetime.now().timestamp() - 60 * self.mac.get("skip_newer_than_minutes", 15)
        self.rows = []
        self.moves = 0
        self.counts = {"filed": 0, "renamed": 0, "to inbox": 0, "duplicates trashed": 0,
                       "folders merged": 0, "empty folders removed": 0, "left in place": 0}
        log_dir = self.root / rules["log_folder"]
        now = dt.datetime.now()
        kind = "Preview" if preview else "Organizer Log"
        self.log_path = log_dir / ("%s %s %s.csv" % (kind, now.strftime("%m.%d.%Y"), now.strftime("%H.%M")))

    # --- helpers --------------------------------------------------------

    def record(self, action, src, dst="", note=""):
        self.rows.append({
            "time": dt.datetime.now().strftime("%m.%d.%Y %H:%M:%S"),
            "action": action, "from": str(src), "to": str(dst), "note": note,
        })

    def is_protected_dir(self, path):
        name = path.name.lower()
        return any(w in name for w in self.protected)

    def is_code_repo(self, path):
        return (path / ".git").exists() or (path / "node_modules").exists() or path.suffix == ".app"

    def mkdir(self, path):
        if not path.exists():
            if not self.preview:
                path.mkdir(parents=True, exist_ok=True)
            self.record("create folder", "", path)

    def move(self, src, dst, action):
        if not self.preview:
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.rename(src, dst) if same_volume(src, dst.parent) else shutil.move(str(src), str(dst))
        self.moves += 1
        self.record(action, src, dst)

    def send_to_trash(self, path, note):
        dst = self.trash / path.name
        n = 2
        while dst.exists():
            dst = self.trash / with_counter(path.name, n)
            n += 1
        self.move(path, dst, "trash duplicate")
        self.rows[-1]["note"] = note
        self.counts["duplicates trashed"] += 1

    def free_name(self, folder, name):
        target = folder / name
        n = 2
        while target.exists():
            target = folder / with_counter(name, n)
            n += 1
        return target

    # --- step 1 ---------------------------------------------------------

    def standing_folders(self):
        """The six main folders, the seven companies, and the log folder. Every other folder
        is made only when a file goes into it, so no empty folder is ever created."""
        paths = list(self.rules["main_folders"])
        for r in self.rules["rules"]:
            parts = r["path"].split("/")
            if parts[0] == "003 Work" and len(parts) > 1:
                paths.append("/".join(parts[:2]))
        paths.append(self.rules["log_folder"])
        out = []
        for p in paths:
            if p not in out:
                out.append(p)
        return out

    def build_structure(self):
        for p in self.standing_folders():
            self.mkdir(self.root / p)

    def remove_empty_folders(self):
        """Removes every empty folder under the six main folders, deepest first. Protected,
        kept, code, and recently changed folders stay, and so do the standing folders."""
        keep = {self.root / p for p in self.standing_folders()}
        found = []
        for main in self.rules["main_folders"]:
            top = self.root / main
            if not top.is_dir():
                continue
            for dirpath, dirnames, _ in os.walk(top):
                here = Path(dirpath)
                dirnames[:] = [d for d in dirnames
                               if not self.is_protected_dir(here / d) and d not in self.keep
                               and not self.is_code_repo(here / d) and not (here / d).is_symlink()]
                try:
                    found.append((here, here.stat().st_mtime))
                except OSError:
                    pass
        # Ages are read before anything is removed, since removing a child folder
        # makes its parent look freshly changed.
        for folder, mtime in reversed(found):
            if folder in keep or mtime > self.cutoff:
                continue
            before = len(self.rows)
            self.remove_if_empty(folder)
            if len(self.rows) > before:
                self.counts["empty folders removed"] += 1

    # --- step 2 ---------------------------------------------------------

    def merge_old_folders(self):
        pairs = [(self.root / old, new) for old, new in self.mac.get("merge_old_folders", {}).items()]
        cloud = home_path("~/Library/Mobile Documents/com~apple~CloudDocs")
        pairs += [(cloud / old, new) for old, new in self.mac.get("icloud_merge", {}).items()]
        for src, new in pairs:
            if src.is_dir() and not src.is_symlink():
                before = self.moves
                self.merge_dir(src, self.root / new)
                if self.moves > before:
                    self.counts["folders merged"] += 1

    def find_merge_target(self, child, dst):
        """A folder inside dst that the old child folder should merge into, or None."""
        exact = dst / child.name
        if exact.is_dir():
            return exact
        words = re.sub(r"^\d+\s+", "", child.name).strip().lower()
        if dst.is_dir():
            for sib in dst.iterdir():
                if sib.is_dir() and re.sub(r"^\d+\s+", "", sib.name).strip().lower() == words:
                    return sib
        rule = match_rule(child.name, self.rules)
        if rule:
            rel = str(dst.relative_to(self.root)) if dst != self.root else ""
            if rule["path"].startswith(rel + "/"):
                return self.root / rule["path"]
        return None

    def merge_dir(self, src, dst):
        self.mkdir(dst)
        for child in sorted(src.iterdir()):
            if child.name in SKIP_FILE_NAMES:
                continue
            if child.is_dir() and not child.is_symlink():
                if self.is_protected_dir(child) or self.is_code_repo(child):
                    self.record("left in place", child, "", "protected folder or code repo")
                    continue
                target = self.find_merge_target(child, dst)
                if target is not None and target != child:
                    self.merge_dir(child, target)
                    continue
            dest = dst / child.name
            if not dest.exists():
                self.move(child, dest, "merge")
            elif child.is_file() and dest.is_file() and same_content(child, dest):
                self.send_to_trash(child, "same content as " + str(dest))
            else:
                self.record("left in place", child, dest, "a different item with this name is already there")
                self.counts["left in place"] += 1
        self.remove_if_empty(src)

    def remove_if_empty(self, folder):
        try:
            names = [n for n in os.listdir(folder) if n not in SKIP_FILE_NAMES]
        except OSError:
            return
        if names or folder == self.root:
            return
        if not self.preview:
            for n in os.listdir(folder):
                try:
                    os.remove(folder / n)
                except OSError:
                    return
            os.rmdir(folder)
        self.record("remove empty folder", folder)

    # --- step 3 ---------------------------------------------------------

    def sources(self):
        out = []
        for s in self.mac["sources"]:
            p = home_path(s["path"])
            if p.is_dir():
                out.append((p, s.get("move_unmatched_folders", False), False))
        out.append((self.inbox, False, True))
        return out

    def skip_entry(self, entry, source):
        name = entry.name
        if name.startswith(".") or name in SKIP_FILE_NAMES or name in self.keep:
            return True
        if name.lower().endswith(PARTIAL_SUFFIXES):
            return True
        if entry.is_symlink():
            return True
        if source == self.root and (name in self.rules["main_folders"] or name in self.mac.get("merge_old_folders", {})):
            return True
        try:
            st = entry.lstat()
        except OSError:
            return True
        if entry.is_dir():
            if newest_mtime(entry) > self.cutoff:
                return True
        elif st.st_mtime > self.cutoff:
            return True
        return False

    def file_loose_items(self):
        for source, move_folders, is_inbox in self.sources():
            if not source.is_dir():
                continue
            try:
                entries = sorted(source.iterdir())
            except PermissionError:
                self.record("blocked", source, "", "macOS did not allow access. Give python3 Full Disk Access.")
                continue
            for entry in entries:
                if self.stale_partial(entry):
                    self.send_to_trash(entry, "unfinished download older than 2 days")
                    continue
                if self.skip_entry(entry, source):
                    continue
                if entry.is_dir():
                    self.file_folder(entry, move_folders, source, is_inbox)
                elif entry.is_file():
                    self.file_one(entry, is_inbox)

    def stale_partial(self, entry):
        name = entry.name.lower()
        if not name.endswith((".crdownload", ".part", ".download", ".partial")) or not entry.is_file():
            return False
        try:
            return entry.stat().st_mtime < dt.datetime.now().timestamp() - 2 * 86400
        except OSError:
            return False

    def special_target(self, path):
        """Files named by what is inside them, or named by hand in the rules. Returns (folder, name) or None."""
        manual = manual_lookup(self.rules, path.name)
        if manual:
            if manual == "TRASH":
                return "TRASH", ""
            folder, _, name = manual.rpartition("/")
            return self.root / folder, name
        try:
            size = path.stat().st_size
        except OSError:
            return None
        if size == 0:
            return "TRASH", ""
        when = stamp(path.stat().st_mtime)
        if re.match(r"(?i)^_?chat( \d+)?\.txt$", path.name) or path.name.lower().startswith("whatsapp chat"):
            people = chat_people(path)
            title = "WhatsApp Chat with " + " and ".join(people) if people else "WhatsApp Chat"
            return self.root / "004 Reference/011 Chat Exports", "004 %s %s.txt" % (title, when)
        shot = re.match(r"^Screen ?shot (\d{4})-(\d{2})-(\d{2}) at (\d{1,2})\.(\d{2})\.\d{2}\s*(AM|PM)?.*\.(png|jpg|jpeg|heic)$",
                        plain_name(path.name), re.I)
        if shot:
            y, mo, d, hh, mm, ampm, ext = shot.groups()
            h = int(hh) % 12 + (12 if (ampm or "").upper() == "PM" else 0) if ampm else int(hh)
            return (self.root / "002 Personal/014 Screenshots",
                    "002 Personal Screenshot %02d%s %s.%s.%s.%s" % (h, mm, mo, d, y, ext.lower()))
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})_(\d{2})_(\d{2})_\d{2}\.(mp3|m4a|aac|wav)$", path.name, re.I)
        if m:
            y, mo, d, hh, mm, ext = m.groups()
            return (self.root / "002 Personal/013 Voice Recordings",
                    "002 Personal Voice Recording %s%s %s.%s.%s.%s" % (hh, mm, mo, d, y, ext.lower()))
        return None

    def file_one(self, path, is_inbox):
        special = self.special_target(path)
        if special:
            folder, new_name = special
            if folder == "TRASH":
                self.send_to_trash(path, "empty file or marked useless in the rules")
                return
            target = folder / new_name
            if target.exists():
                if same_content(path, target):
                    self.send_to_trash(path, "same content as " + str(target))
                    return
                target = self.free_name(folder, new_name)
            self.move(path, target, "file and rename")
            self.counts["filed"] += 1
            self.counts["renamed"] += 1
            return
        base, _ = split_ext(path.name)
        rule = match_rule(base, self.rules)
        if rule:
            dest_dir = self.root / rule["path"]
            new_name = build_name(path.name, rule, self.rules, stamp(path.stat().st_mtime))
            action = "file and rename" if new_name != path.name else "file"
        elif is_inbox:
            return
        else:
            dest_dir, new_name, action = self.inbox, path.name, "to inbox"
        target = dest_dir / new_name
        if target.exists():
            if target.is_file() and same_content(path, target):
                self.send_to_trash(path, "same content as " + str(target))
                return
            target = self.free_name(dest_dir, new_name)
        self.move(path, target, action)
        if action == "to inbox":
            self.counts["to inbox"] += 1
        else:
            self.counts["filed"] += 1
            if new_name != path.name:
                self.counts["renamed"] += 1

    def file_folder(self, path, move_unmatched, source=None, is_inbox=False):
        manual = manual_lookup(self.rules, path.name)
        if manual:
            if manual == "TRASH":
                self.send_to_trash(path, "marked useless in the rules")
                return
            dest = self.root / manual
            if dest.exists():
                self.record("left in place", path, dest, "a folder with this name is already there")
                return
            self.move(path, dest, "file folder")
            self.counts["filed"] += 1
            return
        bukrah_to = self.mac.get("bukrah_working_folders_to")
        working = source in (home_path("~/Desktop"), home_path("~/Downloads"),
                             home_path("~/Library/Mobile Documents/com~apple~CloudDocs"))
        keep_bukrah = self.mac.get("bukrah_keep_in_place", [])
        if (bukrah_to and working and "bukrah" in path.name.lower() and path.name not in keep_bukrah
                and not self.is_code_repo(path)):
            dest = self.root / bukrah_to / path.name
            if dest.exists():
                self.record("left in place", path, dest, "a folder with this name is already there")
                return
            self.move(path, dest, "file folder")
            self.counts["filed"] += 1
            return
        if self.is_protected_dir(path) or self.is_code_repo(path):
            return
        rule = match_rule(path.name, self.rules)
        if is_inbox and not rule:
            return
        if rule:
            dest = self.root / rule["path"] / path.name
        elif move_unmatched:
            dest = self.inbox / path.name
        else:
            return
        if dest.exists():
            self.record("left in place", path, dest, "a folder with this name is already there")
            self.counts["left in place"] += 1
            return
        self.move(path, dest, "file folder" if rule else "folder to inbox")
        self.counts["filed" if rule else "to inbox"] += 1

    # --- step 4 ---------------------------------------------------------

    def walk_for_dedupe(self):
        skip_top = set(self.keep) | {self.rules["trash_folder"]}
        for dirpath, dirnames, filenames in os.walk(self.root):
            d = Path(dirpath)
            keep_dirs = []
            for name in dirnames:
                sub = d / name
                if name.startswith(".") or sub.is_symlink():
                    continue
                if d == self.root and name in skip_top:
                    continue
                if self.is_protected_dir(sub) or self.is_code_repo(sub) or name in self.keep:
                    continue
                keep_dirs.append(name)
            dirnames[:] = keep_dirs
            for name in filenames:
                if name.startswith(".") or name in SKIP_FILE_NAMES:
                    continue
                p = d / name
                try:
                    st = p.lstat()
                except OSError:
                    continue
                if not os.path.isfile(p) or os.path.islink(p) or st.st_size == 0:
                    continue
                if getattr(st, "st_flags", 0) & SF_DATALESS:
                    continue
                yield p, st

    def remove_duplicates(self):
        by_size = {}
        for p, st in self.walk_for_dedupe():
            by_size.setdefault(st.st_size, []).append((p, st))
        for size, group in by_size.items():
            if len(group) < 2:
                continue
            by_head = {}
            for p, st in group:
                h = file_hash(p, head_only=True)
                if h:
                    by_head.setdefault(h, []).append((p, st))
            for heads in by_head.values():
                if len(heads) < 2:
                    continue
                by_full = {}
                for p, st in heads:
                    h = file_hash(p) if size > 65536 else file_hash(p, head_only=True)
                    if h:
                        by_full.setdefault(h, []).append((p, st))
                for same in by_full.values():
                    if len(same) < 2:
                        continue
                    keeper = choose_keeper(same, self.root)
                    for p, st in same:
                        if p != keeper and p.exists():
                            self.send_to_trash(p, "same content as " + str(keeper))

    # --- the run --------------------------------------------------------

    def execute(self):
        self.build_structure()
        self.merge_old_folders()
        self.file_loose_items()
        self.remove_duplicates()
        self.remove_empty_folders()
        self.write_log()
        return self.summary()

    def write_log(self):
        if self.preview:
            self.log_path = Path(os.path.expanduser("~/Desktop")) / self.log_path.name
            if not Path(os.path.expanduser("~/Desktop")).is_dir():
                self.log_path = Path.cwd() / self.log_path.name
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        n = 2
        base = self.log_path
        while self.log_path.exists():
            self.log_path = base.with_name("%s %d.csv" % (base.stem, n))
            n += 1
        with open(self.log_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["time", "action", "from", "to", "note"])
            w.writeheader()
            w.writerows(self.rows)

    def summary(self):
        parts = ["%d %s" % (v, k) for k, v in self.counts.items() if v]
        head = "Preview, nothing changed. " if self.preview else ""
        body = ", ".join(parts) if parts else "Nothing to organize"
        return head + body + ". Log: " + str(self.log_path)


def newest_mtime(folder, limit=5000):
    """The newest change time among the files in a folder, checking at most limit files."""
    newest, seen = 0.0, 0
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            try:
                newest = max(newest, os.lstat(os.path.join(dirpath, name)).st_mtime)
            except OSError:
                pass
            seen += 1
            if seen >= limit:
                return newest
    return newest


def plain_name(name):
    """macOS stores names decomposed and puts a narrow space before AM and PM. Compose and plain space them."""
    name = unicodedata.normalize("NFC", name)
    for ch in ("\u202f", "\u00a0", "\u2009"):
        name = name.replace(ch, " ")
    return re.sub(r"[\u200e\u200f\u2066-\u2069]", "", name)


def manual_lookup(rules, name):
    table = rules.get("manual", {})
    if name in table:
        return table[name]
    key = plain_name(name)
    for k, v in table.items():
        if plain_name(k) == key:
            return v
    return None


CHAT_LINE = re.compile(r"^\u200e?\[?\d{1,4}[/.\-]\d{1,2}[/.\-]\d{1,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap]\.?[Mm]\.?)?\]?\s*(?:-\s*)?([^:]{1,40}):")


def chat_people(path, me=("mohammad alamour", "mohammad", "you")):
    """The people who wrote the most lines in a chat export, without the owner."""
    counts = {}
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i > 5000:
                    break
                m = CHAT_LINE.match(line.strip())
                if m:
                    name = re.sub(r"[^\w\s]", "", m.group(1), flags=re.UNICODE).strip()
                    if name and name.lower() not in me:
                        counts[name] = counts.get(name, 0) + 1
    except OSError:
        return []
    return [n for n, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:2]]


def same_volume(a, b):
    try:
        return os.stat(a).st_dev == os.stat(b).st_dev
    except OSError:
        return False


def file_hash(path, head_only=False):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if head_only:
                h.update(f.read(65536))
            else:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def same_content(a, b):
    try:
        if os.path.getsize(a) != os.path.getsize(b):
            return False
    except OSError:
        return False
    return file_hash(a) is not None and file_hash(a) == file_hash(b)


def choose_keeper(items, root):
    """Keep the copy whose name follows the rule, then the oldest, then the shortest path."""
    def score(item):
        p, st = item
        rule_named = 0 if re.match(r"^00[1-6] ", p.name) and STAMP_AT_END.search(split_ext(p.name)[0]) else 1
        return (rule_named, st.st_mtime, len(str(p)), str(p))
    return sorted(items, key=score)[0][0]


# ----------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------

def lock_path(rules):
    return home_path("~/Library/Application Support") / APP_NAME / "running.lock"


def cmd_run(args):
    rules = load_rules(args.rules)
    lp = lock_path(rules)
    lp.parent.mkdir(parents=True, exist_ok=True)
    if lp.exists() and dt.datetime.now().timestamp() - lp.stat().st_mtime < 3 * 3600:
        print("Another run is in progress. Try again later.")
        return 1
    lp.write_text(str(os.getpid()))
    try:
        run = Run(rules, args.preview)
        message = run.execute()
    finally:
        try:
            lp.unlink()
        except OSError:
            pass
    print(message)
    notify(message.split(". Log:")[0])
    return 0


def cmd_undo(args):
    with open(args.log, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    undone = 0
    for row in reversed(rows):
        src, dst, action = row["from"], row["to"], row["action"]
        if action == "remove empty folder":
            Path(src).mkdir(parents=True, exist_ok=True)
        elif action in ("merge", "file", "file and rename", "to inbox", "file folder", "folder to inbox", "trash duplicate"):
            if dst and os.path.exists(dst) and not os.path.exists(src):
                Path(src).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(dst, src)
                undone += 1
    print("Restored %d items." % undone)
    return 0


def install_dir():
    return home_path("~/Library/Application Support") / APP_NAME


def plist_path():
    return home_path("~/Library/LaunchAgents") / (LAUNCH_LABEL + ".plist")


def cmd_install(args):
    if sys.platform != "darwin":
        print("Install runs on the Mac only.")
        return 1
    rules = load_rules(args.rules)
    target = install_dir()
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), target / SCRIPT_NAME)
    shutil.copy2(Path(args.rules).resolve(), target / RULES_NAME)
    python = os.path.realpath(sys.executable)
    when = rules["mac"].get("run_time", {"hour": 6, "minute": 37})
    log_file = home_path("~/Library/Logs") / (APP_NAME + ".log")
    plist = {
        "Label": LAUNCH_LABEL,
        "ProgramArguments": [python, str(target / SCRIPT_NAME), "run", "--rules", str(target / RULES_NAME)],
        "StartCalendarInterval": {"Hour": int(when["hour"]), "Minute": int(when["minute"])},
        "StandardOutPath": str(log_file),
        "StandardErrorPath": str(log_file),
        "RunAtLoad": False,
    }
    pp = plist_path()
    pp.parent.mkdir(parents=True, exist_ok=True)
    with open(pp, "wb") as f:
        plistlib.dump(plist, f)
    uid = str(os.getuid())
    subprocess.run(["launchctl", "bootout", "gui/" + uid, str(pp)], capture_output=True)
    subprocess.run(["launchctl", "bootstrap", "gui/" + uid, str(pp)], capture_output=True)
    print("Installed. The organizer runs every day at %02d:%02d." % (int(when["hour"]), int(when["minute"])))
    print("")
    print("One more step so the daily run can reach Desktop, Documents, and Downloads:")
    print("  System Settings > Privacy and Security > Full Disk Access > the + button")
    print("  Press Command Shift G, paste the path below, press Return, then Open:")
    print("  " + python)
    print("")
    if not args.no_run:
        print("Running once now.")
        args.preview = False
        args.rules = str(target / RULES_NAME)
        return cmd_run(args)
    return 0


def cmd_uninstall(args):
    pp = plist_path()
    subprocess.run(["launchctl", "bootout", "gui/" + str(os.getuid()), str(pp)], capture_output=True)
    if pp.exists():
        pp.unlink()
    print("The daily run is off. Your files stay where they are.")
    return 0


def spotlight(path, keys):
    if sys.platform != "darwin":
        return {}
    cmd = ["mdls"] + sum([["-name", k] for k in keys], []) + [str(path)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    found = {}
    for line in out.splitlines():
        if " = " in line:
            k, v = line.split(" = ", 1)
            v = v.strip().strip('"')
            if v not in ("(null)", "("):
                found[k.strip()] = v
    return found


def cmd_review(args):
    """Prints one line per file left in 001 Inbox so Claude can name it from what it holds."""
    rules = load_rules(args.rules)
    inbox = home_path(rules["mac"]["root"]) / rules["inbox"]
    keys = ["kMDItemTitle", "kMDItemNumberOfPages", "kMDItemPixelWidth", "kMDItemPixelHeight",
            "kMDItemDurationSeconds", "kMDItemKind"]
    for p in sorted(inbox.iterdir()):
        if p.name.startswith("."):
            continue
        if p.is_dir():
            print("%s | folder | %d items" % (p.name, len(os.listdir(p))))
            continue
        st = p.stat()
        info = spotlight(p, keys)
        parts = [p.name, "%d KB" % (st.st_size // 1024), stamp(st.st_mtime)]
        for k in keys:
            if k in info:
                parts.append(k.replace("kMDItem", "") + " " + info[k][:60])
        if p.suffix.lower() in (".txt", ".md", ".csv"):
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    parts.append("first line: " + f.readline().strip()[:80])
            except OSError:
                pass
        print(" | ".join(parts))
    return 0


def cmd_status(args):
    rules = load_rules(args.rules)
    pp = plist_path()
    print("Schedule: " + ("on, " + str(pp) if pp.exists() else "off"))
    logs = home_path(rules["mac"]["root"]) / rules["log_folder"]
    if logs.is_dir():
        runs = sorted(logs.glob("Organizer Log *.csv"), key=lambda p: p.stat().st_mtime)
        print("Runs logged: %d" % len(runs))
        if runs:
            print("Last run: " + str(runs[-1]))
    print("Logs folder: " + str(logs))
    return 0


def notify(message):
    if sys.platform != "darwin":
        return
    text = message.replace('"', "'")
    subprocess.run(["osascript", "-e", 'display notification "%s" with title "%s"' % (text, APP_NAME)],
                   capture_output=True)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="Mac Organizer", description=APP_NAME + " " + VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--rules", default=None)
    p = sub.add_parser("undo")
    p.add_argument("log")
    p = sub.add_parser("install")
    p.add_argument("--no-run", dest="no_run", action="store_true")
    p.add_argument("--rules", default=None)
    p = sub.add_parser("uninstall")
    p = sub.add_parser("review")
    p.add_argument("--rules", default=None)
    p = sub.add_parser("status")
    p.add_argument("--rules", default=None)
    args = parser.parse_args(argv)
    if getattr(args, "rules", None) is None:
        args.rules = str(default_rules_path())
    commands = {"review": cmd_review, "run": cmd_run, "undo": cmd_undo, "install": cmd_install,
                "uninstall": cmd_uninstall, "status": cmd_status}
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
