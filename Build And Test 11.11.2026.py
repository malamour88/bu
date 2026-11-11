#!/usr/bin/env python3
# Universal File Organizer, build and test
# Version 11.11.2026
#
# 1. Copies "Organizer Rules 11.11.2026.json" into "Drive Organizer 11.11.2026.gs".
# 2. Checks that the Mac script and the Drive script name files the same way.
# 3. Runs the Mac script against a fake Mac home folder, then undoes the run.
# 4. Runs the Drive script against a fake Google Drive in Node.
#
# Usage: python3 "Build And Test 11.11.2026.py"
# Needs python3 and node. Touches nothing outside a temporary folder.

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES = HERE / "Organizer Rules 11.11.2026.json"
MAC = HERE / "Mac Organizer 11.11.2026.py"
GS = HERE / "Drive Organizer 11.11.2026.gs"

FAILURES = []


def check(cond, message):
    if not cond:
        FAILURES.append(message)
        print("  FAIL " + message)


def load_mac():
    spec = importlib.util.spec_from_file_location("mac_organizer", MAC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build():
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    text = GS.read_text(encoding="utf-8")
    block = json.dumps(rules, indent=2, ensure_ascii=False)
    new = re.sub(r"/\*RULES_JSON\*/.*?/\*END_RULES_JSON\*/",
                 lambda m: "/*RULES_JSON*/" + block + "/*END_RULES_JSON*/", text, flags=re.S)
    GS.write_text(new, encoding="utf-8")
    print("Built: rules copied into " + GS.name)


NAME_CASES = [
    ("Hartford_Quote_Comparison_08_06_2026.pdf", "003 VampireTools Hartford Quote Comparison 08.06.2026.pdf"),
    ("VT_Catalog_KimballMidwest_EMAIL_V2-071626.pdf", "003 VampireTools Catalog KimballMidwest EMAIL V2 07.16.2026.pdf"),
    ("Vampire Tools Financial Health Report, October 26, 2026", "003 VampireTools Financial Health Report 10.26.2026"),
    ("Daily_Report_for_Mr__Safi_08_06_2026.pdf", "003 Safi Uncle Daily Report for Mr Safi 08.06.2026.pdf"),
    ("Synology BC510 License Fix 07232026.pdf", "003 Safi Uncle Synology BC510 License Fix 07.23.2026.pdf"),
    ("OBESITY TALK 10 8 2026 - SEEMA MUNIR ICOI.pptx", "003 Stories from Long Ago Obesity Talk Seema Munir ICOI 10.08.2026.pptx"),
    ("Deaa High School Acceleration Plan Portola - 08 09 2026", "002 Personal Deaa High School Acceleration Plan Portola 08.09.2026"),
    ("STFDA attendees and exhibitors research November 5 2026", "003 VampireTools STFDA attendees and exhibitors research 11.05.2026"),
    ("003 VampireTools Hartford BOP Quote Comparison 08.06.2026.pdf", "003 VampireTools Hartford BOP Quote Comparison 08.06.2026.pdf"),
    ("Claude_Best_Practices_Guide_08_07_2026.pdf", "004 Claude Best Practices Guide 08.07.2026.pdf"),
    ("Passport scan 2024-03-02.jpg", "002 Personal CONFIDENTIAL Passport scan 03.02.2024.jpg"),
    ("Bukrah Foundation — Routine Audit & Proposed Weekly/Monthly Structure (2026-07-19)",
     "003 Bukrah Foundation Routine Audit and Proposed Weekly Monthly Structure 07.19.2026"),
    ("Copy of Safi Household Budget", "003 Safi Uncle Household Budget Copy 11.11.2026"),
    ("safi move notes 4521 Ocean View Drive Apt 12.docx", "003 Safi Uncle Move Notes 11.11.2026.docx"),
    ("UHaul 5x8 Trailer Las Vegas Plan 06 13 2026.pdf", "002 Personal UHaul 5x8 Trailer Las Vegas Plan 06.13.2026.pdf"),
]


def test_names():
    print("Naming parity, Mac script and Drive script:")
    mac = load_mac()
    rules = mac.load_rules(RULES)
    py = []
    for name, expected in NAME_CASES:
        base, _ = mac.split_ext(name)
        rule = mac.match_rule(base, rules)
        got = mac.build_name(name, rule, rules, "11.11.2026") if rule else None
        py.append(got)
        check(got == expected, "Mac name for %r: got %r, want %r" % (name, got, expected))
        if got:
            again = mac.build_name(got, mac.match_rule(mac.split_ext(got)[0], rules), rules, "01.01.2000")
            check(again == got, "Mac name is not stable on a second run: %r became %r" % (got, again))
            check(not re.search(r"[_\-—–]", got), "Mac name has a dash or underscore: %r" % got)
    js = r"""
const m = require(process.argv[1]);
const rules = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const names = JSON.parse(process.argv[3]);
const out = names.map(n => { const r = m.matchRule(m.splitExt(n)[0], rules); return r ? m.buildName(n, r, rules, '11.11.2026') : null; });
console.log(JSON.stringify(out));
"""
    res = subprocess.run(["node", "-e", js, str(GS), str(RULES), json.dumps([n for n, _ in NAME_CASES])],
                         capture_output=True, text=True)
    check(res.returncode == 0, "Drive script failed to load in Node: " + res.stderr[-400:])
    if res.returncode == 0:
        out = json.loads(res.stdout)
        for (name, _), a, b in zip(NAME_CASES, py, out):
            check(a == b, "Mac and Drive disagree on %r: %r vs %r" % (name, a, b))
    print("  %d cases checked" % len(NAME_CASES))


def make(path, content="x", age_days=10):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode() if isinstance(content, str) else content)
    t = time.time() - age_days * 86400
    os.utime(path, (t, t))


def test_mac_run():
    print("Mac run on a fake home folder:")
    tmp = Path(tempfile.mkdtemp(prefix="organizer test "))
    home = tmp / "home"
    env = dict(os.environ, HOME=str(home))
    docs, desk, down = home / "Documents", home / "Desktop", home / "Downloads"
    cloud = home / "Library/Mobile Documents/com~apple~CloudDocs"
    make(desk / "Hartford_Quote_Comparison_08_06_2026.pdf", "hartford")
    make(desk / "Screenshot 2026-11-10 at 3.45.12 PM.png", "shot")
    make(desk / "fresh download.pdf", "new", age_days=0)
    make(desk / "Old Project Folder/notes.txt", "notes")
    make(desk / "Bukrah Intake 10.05.2026/letter.pdf", "bukrah letter")
    make(down / "GMAT Focus Study Guide 10.29.2026.pdf", "gmat")
    make(down / "GMAT copy.pdf", "gmat")
    make(down / "setup.dmg.crdownload", "partial")
    make(docs / "01 Personal/01 Career/resume.pdf", "resume")
    make(docs / "01 Personal/04 Receipts and Bills/bill.pdf", "bill")
    make(docs / "02 Work/Vampire Tools/price list.xlsx", "prices")
    make(docs / "02 Work/Bukrah Foundation/board minutes.docx", "minutes")
    make(docs / "To Trash/old.txt", "old")
    make(docs / "thobeelez/.git/HEAD", "ref")
    make(docs / "Claude/memory.md", "memory")
    make(docs / "Safi_Uncle_notes.txt", "safi")
    make(cloud / "Desktop/placeholder.txt", "desk mirror")
    make(cloud / "loose bank statement 2025-01-31.pdf", "bank")
    make(cloud / "Keynote/deck.key", "keynote")

    def run(*args):
        return subprocess.run([sys.executable, str(MAC)] + list(args) + ["--rules", str(RULES)],
                              capture_output=True, text=True, env=env)

    res = run("run", "--preview")
    check(res.returncode == 0, "preview failed: " + res.stderr[-600:])
    check((desk / "Hartford_Quote_Comparison_08_06_2026.pdf").exists(), "preview moved a file")

    res = run("run")
    check(res.returncode == 0, "run failed: " + res.stderr[-600:])
    print("  " + res.stdout.strip().splitlines()[-1] if res.stdout.strip() else "  (no output)")
    vt = docs / "003 Work/003 VampireTools"
    check((vt / "003 VampireTools Hartford Quote Comparison 08.06.2026.pdf").exists(), "VampireTools file not filed and renamed")
    check((docs / "001 Inbox/Screenshot 2026-11-10 at 3.45.12 PM.png").exists(), "unmatched Desktop file not in 001 Inbox")
    check((desk / "fresh download.pdf").exists(), "a file changed minutes ago was moved")
    check((docs / "001 Inbox/Old Project Folder/notes.txt").exists(), "unmatched Desktop folder not in 001 Inbox")
    check((desk / "Bukrah Intake 10.05.2026/letter.pdf").exists(), "a Bukrah folder moved")
    check((docs / "002 Personal/004 School/002 Personal GMAT Focus Study Guide 10.29.2026.pdf").exists(), "GMAT file not filed")
    check((down / "setup.dmg.crdownload").exists(), "a partial download moved")
    check((docs / "002 Personal/003 Career/resume.pdf").exists(), "old 01 Career not merged into 003 Career")
    check((docs / "002 Personal/002 Finances/bill.pdf").exists(), "old Receipts and Bills not merged into 002 Finances")
    check((vt / "price list.xlsx").exists(), "old 02 Work/Vampire Tools not merged into 003 VampireTools")
    check((docs / "02 Work/Bukrah Foundation/board minutes.docx").exists(), "Bukrah Foundation moved during the merge")
    check((docs / "006 Trash/old.txt").exists(), "To Trash not merged into 006 Trash")
    check(not (docs / "To Trash").exists(), "empty To Trash folder not removed")
    check((docs / "thobeelez/.git/HEAD").exists(), "a code repo moved")
    check((docs / "Claude/memory.md").exists(), "the Claude folder moved")
    check((docs / ("003 Work/005 Safi Uncle/003 Safi Uncle Notes " +
           time.strftime("%m.%d.%Y", time.localtime(time.time() - 10 * 86400)) + ".txt")).exists(),
          "Safi file at the top of Documents not filed")
    check((cloud / "Desktop/placeholder.txt").exists(), "iCloud Desktop mirror touched")
    check((cloud / "Keynote/deck.key").exists(), "an iCloud app folder moved")
    check((docs / "002 Personal/002 Finances/002 Personal Loose Bank Statement 01.31.2025.pdf").exists(),
          "iCloud bank statement not filed")
    trash = home / ".Trash"
    gmat_copies = list((docs / "002 Personal/004 School").glob("*GMAT*")) + list(docs.glob("001 Inbox/GMAT*"))
    check(len(gmat_copies) == 1, "duplicate GMAT copy not removed: %s" % gmat_copies)
    check(trash.is_dir() and any(trash.iterdir()), "nothing went to the Mac Trash")
    for p in docs.rglob("*"):
        if p.is_dir() and re.match(r"^00[1-6] ", p.name):
            check(not re.search(r"[_\-]", p.name) or "Onsite" in p.name, "folder name breaks the rule: " + p.name)

    res2 = run("run")
    check(res2.returncode == 0, "second run failed: " + res2.stderr[-400:])
    check("Nothing to organize" in res2.stdout, "second run was not quiet: " + res2.stdout.strip())

    logs = sorted((docs / "004 Reference/010 Organizer Logs").glob("Organizer Log *.csv"), key=lambda p: p.stat().st_mtime)
    check(len(logs) >= 1, "no run log written")
    if logs:
        first = logs[0]
        res = subprocess.run([sys.executable, str(MAC), "undo", str(first)], capture_output=True, text=True, env=env)
        check(res.returncode == 0, "undo failed: " + res.stderr[-400:])
        check((desk / "Hartford_Quote_Comparison_08_06_2026.pdf").exists(), "undo did not bring the Desktop file back")
        check((docs / "01 Personal/01 Career/resume.pdf").exists(), "undo did not restore the old folders")
        check((down / "GMAT copy.pdf").exists() or (down / "GMAT Focus Study Guide 10.29.2026.pdf").exists(),
              "undo did not restore the trashed duplicate")
        check((docs / "To Trash/old.txt").exists(), "undo did not restore To Trash")
    shutil.rmtree(tmp, ignore_errors=True)


FAKE_DRIVE = r"""
const path = process.argv[1];
const files = {};
let seq = 0;
function add(name, parent, extra) { const id = 'f' + (++seq); files[id] = Object.assign({id, name, parents: [parent], trashed: false, ownedByMe: true,
  mimeType: 'application/pdf', createdTime: '2026-0' + (1 + seq % 9) + '-01T00:00:00Z', modifiedTime: '2026-08-06T12:00:00Z'}, extra || {}); return id; }
const FOLDER = 'application/vnd.google-apps.folder';
files.root = {id: 'root', name: 'My Drive', parents: [], mimeType: FOLDER};
const p = add('002 Personal', 'root', {mimeType: FOLDER});
const w = add('003 Work', 'root', {mimeType: FOLDER});
const b = add('001 Bukrah Foundation', w, {mimeType: FOLDER});
add('Hartford_Quote_Comparison_08_06_2026.pdf', 'root', {md5Checksum: 'aaa', size: '10'});
add('Hartford copy.pdf', 'root', {md5Checksum: 'aaa', size: '10'});
add('IMG_7455.HEIC', 'root', {md5Checksum: 'bbb', size: '20'});
add('Random Folder', 'root', {mimeType: FOLDER});
add('Bukrah Shared', 'root', {mimeType: FOLDER});
add('board_minutes-2026.docx', b, {md5Checksum: 'ccc', size: '30'});
add('board copy.docx', p, {md5Checksum: 'ccc', size: '30'});
add('my_resume.pdf', p, {md5Checksum: 'ddd', size: '40'});
function parseQ(q) {
  const parent = /'([^']+)' in parents/.exec(q)[1];
  const name = /name = '((?:[^'\\]|\\.)*)'/.exec(q);
  const folderOnly = q.indexOf("mimeType = '" + FOLDER + "'") !== -1;
  return Object.values(files).filter(f => f.id !== 'root' && !f.trashed && f.parents.indexOf(parent) !== -1 &&
    (!folderOnly || f.mimeType === FOLDER) && (!name || f.name === name[1].replace(/\\'/g, "'")));
}
global.Drive = {Files: {
  get: id => files[id],
  list: o => ({files: parseQ(o.q).map(f => Object.assign({}, f))}),
  create: o => { const id = add(o.name, o.parents[0], {mimeType: o.mimeType}); return files[id]; },
  update: (body, id, blob, opts) => { const f = files[id]; Object.assign(f, body);
    if (opts && opts.addParents) { f.parents = f.parents.filter(x => x !== opts.removeParents).concat([opts.addParents]); } return f; },
}};
global.Utilities = {formatDate: (d, tz, fmt) => { const x = new Date(d); const pad = n => String(n).padStart(2, '0');
  return fmt.replace('MM', pad(x.getUTCMonth() + 1)).replace('dd', pad(x.getUTCDate())).replace('yyyy', x.getUTCFullYear()).replace('HH', '06').replace('mm', '30').replace('ss', pad(++tick % 60)); }};
let tick = 0;
global.Session = {getScriptTimeZone: () => 'UTC'};
const props = {}; global.PropertiesService = {getScriptProperties: () => ({getProperty: k => props[k] || null, setProperty: (k, v) => { props[k] = v; }, deleteProperty: k => { delete props[k]; }})};
const sheetRows = [];
global.SpreadsheetApp = {create: () => { const id = add('log', 'root', {mimeType: 'sheet'}); return sheetObj(id); }, openById: id => sheetObj(id)};
function sheetObj(id) { return {getId: () => id, getSheets: () => [{appendRow: r => sheetRows.push(r), getLastRow: () => sheetRows.length,
  getRange: () => ({setValues: v => v.forEach(r => sheetRows.push(r))}), getDataRange: () => ({getValues: () => sheetRows})}]}; }
global.Logger = {log: () => {}};
global.ScriptApp = {getProjectTriggers: () => [], deleteTrigger: () => {}, newTrigger: () => ({timeBased: () => ({everyDays: () => ({atHour: () => ({create: () => {}})})})})};
const src = require('fs').readFileSync(path, 'utf8');
// The test loads our own Drive script into this fake environment. No outside input is evaluated.
eval(src.replace(/if \(typeof module[\s\S]*$/, '') + '\nglobal.__api = {organizeNow, previewNow, undoLastRun};');
function pathOf(id) { const out = []; let f = files[id]; while (f && f.id !== 'root') { out.unshift(f.name); f = files[f.parents[0]]; } return out.join('/'); }
function snapshot() { return Object.values(files).filter(f => f.id !== 'root' && !f.trashed && f.mimeType !== FOLDER && f.mimeType !== 'sheet').map(f => pathOf(f.id)).sort(); }
const before = snapshot();
__api.previewNow();
const afterPreview = snapshot();
const summary = __api.organizeNow();
const after = snapshot();
const trashed = Object.values(files).filter(f => f.trashed).map(f => f.name);
const second = __api.organizeNow();
const rootFolders = Object.values(files).filter(f => f.parents[0] === 'root' && f.mimeType === FOLDER && !f.trashed).map(f => f.name).sort();
__api.undoLastRun();
__api.undoLastRun();
const restored = snapshot();
console.log(JSON.stringify({before, afterPreview, summary, after, trashed, second, restored, rootFolders}));
"""


def test_drive_run():
    print("Drive run on a fake Google Drive:")
    res = subprocess.run(["node", "-e", FAKE_DRIVE, str(GS)], capture_output=True, text=True)
    check(res.returncode == 0, "Drive script failed: " + res.stderr[-800:])
    if res.returncode != 0:
        return
    r = json.loads(res.stdout)
    print("  " + r["summary"])
    check(r["before"] == r["afterPreview"], "preview changed files")
    after = r["after"]
    check("003 Work/003 VampireTools/003 VampireTools Hartford Quote Comparison 08.06.2026.pdf" in after,
          "VampireTools file not filed and renamed")
    check(not any("Hartford copy" in a for a in after), "duplicate Hartford copy not trashed")
    check("001 Inbox/IMG_7455.HEIC" in after, "unmatched file not in 001 Inbox")
    check("003 Work/001 Bukrah Foundation/board_minutes-2026.docx" in after, "a file inside Bukrah was renamed or moved")
    check("board copy.docx" in r["trashed"], "duplicate outside Bukrah not trashed in favor of the Bukrah copy")
    check(any(a.startswith("002 Personal/") and "Resume" in a and a.endswith(".pdf") and "_" not in a for a in after),
          "file inside 002 Personal not renamed to the rule: %s" % after)
    check(r["rootFolders"] == ["001 Inbox", "002 Personal", "003 Work", "004 Reference", "005 To Be Printed", "006 Trash", "Bukrah Shared"],
          "My Drive root holds more than the six folders: %s" % r["rootFolders"])
    check("Nothing to organize" in r["second"], "second run was not quiet: " + r["second"])
    check(r["restored"] == r["before"], "undo did not restore the Drive: %s" % r["restored"])


def main():
    build()
    test_names()
    test_mac_run()
    test_drive_run()
    print("")
    if FAILURES:
        print("%d checks failed." % len(FAILURES))
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
