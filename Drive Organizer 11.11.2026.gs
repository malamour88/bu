// Universal File Organizer, Google Drive script
// Version 11.11.2026
//
// Runs inside your own Google account on a daily schedule. No Claude session and no prompts.
// Keeps My Drive filed under the 001 to 006 system, with the same rules as the Mac script.
//
// One time setup, about five minutes. The Install Guide walks through it.
//   1. script.google.com > New project. Paste this whole file over the sample code.
//   2. Services (the + next to Services) > Drive API > version v3 > Add.
//   3. Pick installDailyRun in the function menu and click Run. Approve the access screen once.
//
// Functions you can run by hand
//   installDailyRun   Turns on the daily run and organizes once now.
//   organizeNow       Organizes now.
//   previewNow        Writes what it would do to the log sheet. Changes nothing.
//   undoLastRun       Reverses every change from the most recent run.
//   removeDailyRun    Turns the daily run off. Files stay where they are.
//
// What one run does
//   1. Makes sure 001 Inbox to 006 Trash and their standard subfolders exist.
//   2. Files every loose item at the top of My Drive and every file in 001 Inbox.
//      A keyword match goes to its company or personal folder with a rule compliant name.
//      No match goes to 001 Inbox and keeps its name.
//   3. Renames files inside 002 to 005 that break the naming rule. Bukrah Foundation is never renamed.
//   4. Sends exact duplicates (same content fingerprint) to the Drive trash, 30 days to restore.
//   5. Writes every change to the log sheet in 004 Reference/010 Organizer Logs.

// The rules below are copied from "Organizer Rules 11.11.2026.json" by "Build And Test 11.11.2026.py".
// Edit the JSON, run the build, then paste this file into Apps Script again.
const RULES = /*RULES_JSON*/{
  "version": "11.11.2026",
  "about": "Universal File Organizer rules. One file drives both the Mac script and the Google Drive script. Rules are checked top to bottom and the first match wins. Keywords match whole words in the file or folder name, case is ignored.",
  "main_folders": [
    "001 Inbox",
    "002 Personal",
    "003 Work",
    "004 Reference",
    "005 To Be Printed",
    "006 Trash"
  ],
  "inbox": "001 Inbox",
  "trash_folder": "006 Trash",
  "log_folder": "004 Reference/010 Organizer Logs",
  "rules": [
    {
      "path": "003 Work/001 Bukrah Foundation/001 Organizer Intake",
      "label": "003 Bukrah Foundation",
      "strip": [
        "Bukrah Foundation",
        "Bukrah"
      ],
      "keywords": [
        "bukrah",
        "katz compliance",
        "بكرا",
        "بكرة",
        "بكره"
      ]
    },
    {
      "path": "003 Work/002 Stories from Long Ago",
      "label": "003 Stories from Long Ago",
      "strip": [
        "Stories from Long Ago",
        "Stories From Long Ago"
      ],
      "keywords": [
        "stories from long ago",
        "seema",
        "prophet yusuf",
        "icoi"
      ]
    },
    {
      "path": "003 Work/003 VampireTools",
      "label": "003 VampireTools",
      "strip": [
        "VampireTools",
        "Vampire Tools",
        "VT"
      ],
      "keywords": [
        "vampire",
        "vampiretools",
        "vampire tools",
        "vt",
        "kimball",
        "hartford",
        "stafda",
        "stfda",
        "bop",
        "broker call",
        "vpti"
      ]
    },
    {
      "path": "003 Work/004 Houston Apartments",
      "label": "003 Houston Apartments",
      "strip": [
        "Houston Apartments"
      ],
      "keywords": [
        "houston",
        "propcare",
        "bonnie garcia",
        "texas comptroller"
      ]
    },
    {
      "path": "003 Work/005 Safi Uncle",
      "label": "003 Safi Uncle",
      "strip": [
        "Safi Uncle",
        "Safi"
      ],
      "keywords": [
        "safi",
        "qureshey",
        "skyline",
        "synology",
        "yf sq"
      ]
    },
    {
      "path": "003 Work/006 Lubna",
      "label": "003 Lubna",
      "strip": [
        "Lubna"
      ],
      "keywords": [
        "lubna"
      ]
    },
    {
      "path": "003 Work/007 Other Work/012 Mount Fuji Water",
      "label": "003 Mount Fuji Water",
      "strip": [
        "Mount Fuji Water"
      ],
      "keywords": [
        "mount fuji",
        "fuji water"
      ]
    },
    {
      "path": "003 Work/007 Other Work/010 Onsite Trucking Compliance Instagram Launch 10.17.2026",
      "label": "003 Onsite Trucking",
      "strip": [
        "Onsite Trucking"
      ],
      "keywords": [
        "onsite trucking",
        "trucking compliance"
      ]
    },
    {
      "path": "003 Work/007 Other Work/011 Syrian Olive Oil Import Project",
      "label": "003 Syrian Olive Oil",
      "strip": [
        "Syrian Olive Oil"
      ],
      "keywords": [
        "olive oil"
      ]
    },
    {
      "path": "003 Work/007 Other Work/001 Resistance X",
      "label": "003 Resistance X",
      "strip": [
        "Resistance X"
      ],
      "keywords": [
        "resistance x"
      ]
    },
    {
      "path": "003 Work/007 Other Work/004 Rahma Center",
      "label": "003 Rahma Center",
      "strip": [
        "Rahma Center"
      ],
      "keywords": [
        "rahma"
      ]
    },
    {
      "path": "003 Work/007 Other Work/005 5PIE",
      "label": "003 5PIE",
      "strip": [
        "5PIE"
      ],
      "keywords": [
        "5pie"
      ]
    },
    {
      "path": "003 Work/007 Other Work/007 Bullionite",
      "label": "003 Bullionite",
      "strip": [
        "Bullionite"
      ],
      "keywords": [
        "bullionite"
      ]
    },
    {
      "path": "003 Work/007 Other Work/009 Timesheets",
      "label": "003 Other Work",
      "strip": [],
      "keywords": [
        "timesheet",
        "timesheets"
      ]
    },
    {
      "path": "003 Work/007 Other Work/008 Startup Ideas",
      "label": "003 Other Work",
      "strip": [],
      "keywords": [
        "startup idea",
        "startup ideas"
      ]
    },
    {
      "path": "006 Trash",
      "label": "006",
      "strip": [],
      "keywords": [
        "safe to delete",
        "verified duplicates"
      ]
    },
    {
      "path": "002 Personal/010 Sensitive",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "confidential": true,
      "keywords": [
        "passport",
        "ssn",
        "social security",
        "drivers license",
        "driver license",
        "green card",
        "birth certificate",
        "password",
        "passwords",
        "recovery codes",
        "check scan",
        "voided check",
        "passports",
        "جوازات",
        "passport photo"
      ]
    },
    {
      "path": "002 Personal/011 Vehicles",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "model 3",
        "tesla",
        "honda",
        "grom",
        "dmv",
        "vehicle",
        "car insurance",
        "insurance card"
      ]
    },
    {
      "path": "002 Personal/012 Legal",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "confidential": true,
      "keywords": [
        "settlement agreement",
        "petitioner",
        "petitioners",
        "court",
        "attorney",
        "lawsuit"
      ]
    },
    {
      "path": "002 Personal/006 Family",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "deaa",
        "family",
        "ahmad",
        "qais",
        "karam"
      ]
    },
    {
      "path": "002 Personal/005 Health",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "confidential": true,
      "keywords": [
        "medical",
        "doctor",
        "lab results",
        "prescription",
        "dental",
        "vision exam"
      ]
    },
    {
      "path": "002 Personal/005 Health",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "workout",
        "supplement",
        "supplements",
        "fitness",
        "nutrition",
        "meal plan"
      ]
    },
    {
      "path": "002 Personal/004 School",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "gmat",
        "stanford",
        "gsb",
        "mba",
        "transcript",
        "uci",
        "school"
      ]
    },
    {
      "path": "002 Personal/003 Career",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "resume",
        "cv",
        "cover letter",
        "career",
        "linkedin",
        "community leadership",
        "job offer"
      ]
    },
    {
      "path": "002 Personal/002 Finances",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "bank statement",
        "account statement",
        "tax return",
        "1099",
        "w2",
        "w 2",
        "receipt",
        "receipts",
        "credit card",
        "budget",
        "statements",
        "bank",
        "paystub",
        "pay stub",
        "robinhood",
        "brokerage",
        "citi",
        "chase",
        "dispute",
        "unemployment"
      ]
    },
    {
      "path": "002 Personal/007 Travel",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "itinerary",
        "flight",
        "boarding pass",
        "hotel",
        "uhaul",
        "u haul",
        "trip",
        "travel",
        "getaway",
        "ticket",
        "emirates"
      ]
    },
    {
      "path": "002 Personal/009 Mentorship",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "mentorship",
        "mentor",
        "mentee"
      ]
    },
    {
      "path": "002 Personal/001 Plan and Goals",
      "label": "002 Personal",
      "strip": [
        "Personal"
      ],
      "keywords": [
        "goals",
        "life plan",
        "vision board"
      ]
    },
    {
      "path": "004 Reference/001 Guides",
      "label": "004",
      "strip": [
        "Reference"
      ],
      "keywords": [
        "guide",
        "best practices",
        "manual",
        "tutorial",
        "handbook",
        "how to"
      ]
    },
    {
      "path": "005 To Be Printed",
      "label": "005",
      "strip": [],
      "keywords": [
        "to print",
        "print this",
        "printable"
      ]
    }
  ],
  "extra_folders": [
    "002 Personal/008 Photography",
    "003 Work/007 Other Work",
    "004 Reference/008 Backups",
    "004 Reference/009 Archive"
  ],
  "main_folder_labels": {
    "001 Inbox": "001",
    "002 Personal": "002 Personal",
    "003 Work": "003 Other Work",
    "004 Reference": "004",
    "005 To Be Printed": "005",
    "006 Trash": "006"
  },
  "acronyms": [
    "AI",
    "BOP",
    "CV",
    "DMV",
    "GMAT",
    "GSB",
    "ICOI",
    "IRS",
    "LLC",
    "MBA",
    "PDF",
    "SQ",
    "STAFDA",
    "UCI",
    "USA",
    "VT",
    "YF",
    "FINAL"
  ],
  "blocked_words": [],
  "protected_folder_names_contain": [
    "Bukrah",
    "Claude",
    "OneDrive",
    "Mohammad X Safi"
  ],
  "mac": {
    "root": "~/Documents",
    "sources": [
      {
        "path": "~/Desktop",
        "move_unmatched_folders": true
      },
      {
        "path": "~/Downloads",
        "move_unmatched_folders": true
      },
      {
        "path": "~/Documents",
        "move_unmatched_folders": false
      },
      {
        "path": "~/Library/Mobile Documents/com~apple~CloudDocs",
        "move_unmatched_folders": false
      }
    ],
    "keep_in_place": [
      "Desktop",
      "Documents",
      "Downloads",
      "Shortcuts",
      "VT Sales Agent",
      "thobeelez",
      "tapmenu",
      "design-log",
      "Bukrah Scripts",
      "Nightly Organize Logs",
      "Cowork Organize Logs",
      "Organizer Kit",
      "Organizer Working"
    ],
    "merge_old_folders": {
      "00 Inbox": "001 Inbox",
      "01 Personal": "002 Personal",
      "02 Work": "003 Work",
      "03 Reference": "004 Reference",
      "04 Quick Share": "001 Inbox",
      "05 Backup": "004 Reference/008 Backups",
      "99 Archive": "004 Reference/009 Archive",
      "To Be Organized": "001 Inbox",
      "To Be Printed": "005 To Be Printed",
      "To Trash": "006 Trash",
      "Duplicates": "006 Trash",
      "Personal From Bukrah Drive 08 2026": "002 Personal"
    },
    "skip_newer_than_minutes": 15,
    "run_time": {
      "hour": 6,
      "minute": 37
    },
    "icloud_merge": {
      "Mohammad Personal": "002 Personal",
      "Archive": "004 Reference/009 Archive"
    },
    "bukrah_working_folders_to": "003 Work/001 Bukrah Foundation"
  },
  "drive": {
    "never_rename_inside": [
      "003 Work/001 Bukrah Foundation",
      "004 Reference/008 Backups",
      "004 Reference/009 Archive"
    ],
    "run_hour": 6
  }
}/*END_RULES_JSON*/;

// ---------------------------------------------------------------------------
// Naming. Mirrors the Mac script line for line. The tests compare both.
// ---------------------------------------------------------------------------

const MONTHS = {jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12};

const DATE_PATTERNS = [
  ['ymd', /(?<!\d)((?:19|20)\d{2})[-_. ](\d{1,2})[-_. ](\d{1,2})(?!\d)/g],
  ['mdy', /(?<!\d)(\d{1,2})[-_. ](\d{1,2})[-_. ]((?:19|20)\d{2})(?!\d)/g],
  ['ymd', /(?<!\d)((?:19|20)\d{2})(\d{2})(\d{2})(?!\d)/g],
  ['mdy8', /(?<!\d)(\d{2})(\d{2})((?:19|20)\d{2})(?!\d)/g],
  ['mdy6', /(?<!\d)(\d{2})(\d{2})(\d{2})(?!\d)/g],
  ['name', /\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+((?:19|20)\d{2})(?!\d)/gi],
];

const ADDRESS_PATTERNS = [
  /\b\d{1,6}\s+(?:[a-z]+\s+){0,3}(?:street|st|avenue|ave|road|rd|drive|lane|ln|way|court|ct|circle|cir|boulevard|blvd|place|pl|terrace|ter|trail|trl|parkway|pkwy|highway|hwy)\b/gi,
  /\b(?:apt|apartment|unit|suite)\s+\w+\b/gi,
];

const SEPARATORS = /[_—–‒\-:;,|\/\\()\[\]{}"!?#*~<>]/g;
const MAIN_CODE = /^00[1-6]\s+/;
const STAMP_AT_END = / \d{2}\.\d{2}\.\d{4}$/;

function pad2_(n) { return String(n).padStart(2, '0'); }

function splitExt(name) {
  const m = /^(.+)\.([A-Za-z0-9]{1,5})$/.exec(name);
  if (m && !/^\d+$/.test(m[2])) return [m[1], m[2]];
  return [name, ''];
}

function extractDate(text) {
  for (const [kind, source] of DATE_PATTERNS) {
    const pattern = new RegExp(source.source, source.flags);
    let m;
    while ((m = pattern.exec(text)) !== null) {
      let y, mo, d;
      if (kind === 'ymd') { y = +m[1]; mo = +m[2]; d = +m[3]; }
      else if (kind === 'name') { mo = MONTHS[m[1].toLowerCase().slice(0, 3)]; d = +m[2]; y = +m[3]; }
      else if (kind === 'mdy6') { mo = +m[1]; d = +m[2]; y = 2000 + +m[3]; }
      else { mo = +m[1]; d = +m[2]; y = +m[3]; }
      if (mo >= 1 && mo <= 12 && d >= 1 && d <= 31) {
        const rest = text.slice(0, m.index) + ' ' + text.slice(m.index + m[0].length);
        return [pad2_(mo) + '.' + pad2_(d) + '.' + String(y).padStart(4, '0'), rest];
      }
    }
  }
  return [null, text];
}

function normalizeWords(text) {
  // Lower case, drop accent and Arabic vowel marks, keep letters and digits of any script.
  const t = text.toLowerCase().normalize('NFKD').replace(/\p{Mn}/gu, '');
  return ' ' + t.replace(/[^\p{L}\p{N}]+/gu, ' ').trim() + ' ';
}

function matchRule(text, rules) {
  const norm = normalizeWords(text);
  for (const rule of rules.rules) {
    for (const kw of rule.keywords) {
      if (norm.indexOf(normalizeWords(kw)) !== -1) return rule;
    }
  }
  return null;
}

function labelWords(label) { return label.replace(/^\d{3}\s*/, '').trim(); }

function isAlpha_(c) { return c.toLowerCase() !== c.toUpperCase(); }

function fixCase(text, acronyms) {
  const letters = Array.from(text).filter(isAlpha_);
  if (!letters.length) return text;
  const lowerAll = letters.every(c => c === c.toLowerCase());
  const upperAll = letters.every(c => c === c.toUpperCase()) && letters.length > 3;
  if (!(lowerAll || upperAll)) return text;
  const keep = new Set(acronyms.map(a => a.toUpperCase()));
  const out = [];
  for (const word of text.split(' ')) {
    if (keep.has(word.toUpperCase())) out.push(word.toUpperCase());
    else if (word) out.push(word[0].toUpperCase() + word.slice(1).toLowerCase());
  }
  return out.join(' ');
}

function stripPrefixes(text, words) {
  let changed = true;
  while (changed) {
    changed = false;
    if (MAIN_CODE.test(text)) { text = text.replace(MAIN_CODE, ''); changed = true; }
    for (const w of words) {
      if (!w) continue;
      if (text.toLowerCase() === w.toLowerCase()) { text = ''; changed = true; }
      else if (text.toLowerCase().startsWith(w.toLowerCase() + ' ')) { text = text.slice(w.length + 1); changed = true; }
    }
  }
  return text.trim();
}

function escapeRegex_(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function cleanDescription(base, rule, rules) {
  let text = base.trim();
  let copy = false;
  const m = /^copy of\s+/i.exec(text);
  if (m) { text = text.slice(m[0].length); copy = true; }
  let date;
  [date, text] = extractDate(text);
  text = text.replace(/&/g, ' and ').replace(/\+/g, ' and ');
  text = text.replace(SEPARATORS, ' ');
  text = text.replace(/\./g, ' ');
  text = text.replace(/\s+/g, ' ').trim();
  const words = [];
  if (rule) { words.push(labelWords(rule.label)); for (const s of (rule.strip || [])) words.push(s); }
  const uniq = Array.from(new Set(words)).sort((a, b) => b.length - a.length);
  text = stripPrefixes(text, uniq);
  for (const p of ADDRESS_PATTERNS) text = text.replace(new RegExp(p.source, p.flags), ' ');
  for (const w of (rules.blocked_words || [])) {
    if (w) text = text.replace(new RegExp('\\b' + escapeRegex_(w) + '\\b', 'gi'), ' ');
  }
  text = text.replace(/\s+/g, ' ').trim();
  text = fixCase(text, rules.acronyms || []);
  if (copy) text = (text + ' Copy').trim();
  if (/^copy\s+/i.test(text)) text = text.slice(5) + ' Copy';
  return [text || 'Untitled', date];
}

function conforms(name, label) {
  const base = splitExt(name)[0];
  if (/[_—–‒\-]/.test(name)) return false;
  if (!base.startsWith(label + ' ')) return false;
  return STAMP_AT_END.test(base);
}

function buildName(name, rule, rules, fallbackDate, label) {
  label = label || rule.label;
  if (conforms(name, label)) return name;
  const [base, ext] = splitExt(name);
  const [desc, date] = cleanDescription(base, rule, rules);
  const parts = [label];
  if (rule && rule.confidential && desc.toUpperCase().indexOf('CONFIDENTIAL') === -1) parts.push('CONFIDENTIAL');
  parts.push(desc);
  parts.push(date || fallbackDate);
  return parts.join(' ') + (ext ? '.' + ext.toLowerCase() : '');
}

// ---------------------------------------------------------------------------
// Drive side
// ---------------------------------------------------------------------------

const FOLDER_MIME = 'application/vnd.google-apps.folder';
const FILE_FIELDS = 'nextPageToken, files(id, name, mimeType, md5Checksum, size, createdTime, modifiedTime, ownedByMe, parents)';
const TIME_BUDGET_MS = 5 * 60 * 1000;

function installDailyRun() {
  removeDailyRun();
  ScriptApp.newTrigger('organizeNow').timeBased().everyDays(1).atHour(RULES.drive.run_hour || 6).create();
  organizeNow();
}

function removeDailyRun() {
  for (const t of ScriptApp.getProjectTriggers()) {
    if (t.getHandlerFunction() === 'organizeNow') ScriptApp.deleteTrigger(t);
  }
}

function organizeNow() {
  clearContinuation_();
  const run = new DriveRun_(false);
  const summary = run.execute();
  if (run.stopped) scheduleContinuation_();
  return summary;
}

// A big Drive can need more than one six minute window. The run picks up again ten minutes later.
function scheduleContinuation_() {
  const t = ScriptApp.newTrigger('organizeNow').timeBased().after(10 * 60 * 1000).create();
  PropertiesService.getScriptProperties().setProperty('continuationId', t.getUniqueId());
}

function clearContinuation_() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('continuationId');
  if (!id) return;
  for (const t of ScriptApp.getProjectTriggers()) {
    if (t.getUniqueId() === id) ScriptApp.deleteTrigger(t);
  }
  props.deleteProperty('continuationId');
}

function previewNow() { return new DriveRun_(true).execute(); }

class DriveRun_ {
  constructor(preview) {
    this.preview = preview;
    this.started = Date.now();
    this.runId = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'MM.dd.yyyy HH.mm.ss') + (preview ? ' Preview' : '');
    this.rows = [];
    this.stopped = false;
    this.folderCache = {};
    this.counts = {filed: 0, renamed: 0, 'to inbox': 0, 'duplicates trashed': 0};
    this.rootId = Drive.Files.get('root', {fields: 'id'}).id;
    this.tz = Session.getScriptTimeZone();
  }

  timeLeft() {
    if (Date.now() - this.started > TIME_BUDGET_MS) {
      if (!this.stopped) this.log('stopped', '', '', '', '', '', 'Time limit reached. The next run continues.');
      this.stopped = true;
    }
    return !this.stopped;
  }

  log(action, name, newName, fromId, toId, fileId, note) {
    this.rows.push([this.runId, new Date(), action, name || '', newName || '', fromId || '', toId || '', fileId || '', note || '']);
  }

  stampOf(file) {
    return Utilities.formatDate(new Date(file.modifiedTime || file.createdTime), this.tz, 'MM.dd.yyyy');
  }

  listChildren(parentId) {
    const out = [];
    let token = null;
    do {
      const res = Drive.Files.list({
        q: "'" + parentId + "' in parents and trashed = false",
        fields: FILE_FIELDS, pageSize: 1000, pageToken: token,
      });
      for (const f of (res.files || [])) out.push(f);
      token = res.nextPageToken;
    } while (token);
    return out;
  }

  childFolder(parentId, name, create) {
    if (String(parentId).startsWith('new:')) return create ? parentId + '/' + name : null;
    const key = parentId + '/' + name;
    if (this.folderCache[key]) return this.folderCache[key];
    const q = "'" + parentId + "' in parents and trashed = false and mimeType = '" + FOLDER_MIME + "' and name = '" +
      name.replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";
    const res = Drive.Files.list({q: q, fields: 'files(id, name)', pageSize: 10});
    let id = res.files && res.files.length ? res.files[0].id : null;
    if (!id && create) {
      if (this.preview) { id = 'new:' + key; }
      else { id = Drive.Files.create({name: name, mimeType: FOLDER_MIME, parents: [parentId]}).id; }
      this.log('create folder', name, '', parentId, id, id, '');
    }
    if (id) this.folderCache[key] = id;
    return id;
  }

  folderFor(path) {
    let id = this.rootId;
    for (const part of path.split('/')) {
      if (String(id).startsWith('new:')) return id + '/' + part;
      id = this.childFolder(id, part, true);
    }
    return id;
  }

  move(file, fromId, toId, newName, action) {
    if (!this.timeLeft()) return false;
    if (!this.preview) {
      const body = {};
      if (newName && newName !== file.name) body.name = newName;
      const opts = {};
      if (toId && toId !== fromId) { opts.addParents = toId; opts.removeParents = fromId; }
      Drive.Files.update(body, file.id, null, opts);
    }
    this.log(action, file.name, newName || file.name, fromId, toId, file.id, '');
    return true;
  }

  trash(file, parentId, note) {
    if (!this.timeLeft()) return;
    if (!this.preview) Drive.Files.update({trashed: true}, file.id);
    this.log('trash duplicate', file.name, '', parentId, '', file.id, note);
    this.counts['duplicates trashed'] += 1;
  }

  isProtectedFolder(name) {
    const n = name.toLowerCase();
    return (RULES.protected_folder_names_contain || []).some(w => n.indexOf(w.toLowerCase()) !== -1);
  }

  buildStructure() {
    for (const main of RULES.main_folders) this.folderFor(main);
    const paths = RULES.rules.map(r => r.path).concat(RULES.extra_folders || []).concat([RULES.log_folder]);
    for (const p of paths) this.folderFor(p);
  }

  fileLooseItems() {
    const inboxId = this.folderFor(RULES.inbox);
    for (const item of this.listChildren(this.rootId)) {
      if (!this.timeLeft()) return;
      if (item.mimeType === FOLDER_MIME) {
        if (RULES.main_folders.indexOf(item.name) !== -1 || this.isProtectedFolder(item.name)) continue;
        const rule = matchRule(item.name, RULES);
        const toId = rule ? this.folderFor(rule.path) : inboxId;
        if (this.childFolder(toId, item.name, false)) {
          this.log('left in place', item.name, '', this.rootId, toId, item.id, 'A folder with this name is already there');
          continue;
        }
        if (this.move(item, this.rootId, toId, item.name, rule ? 'file folder' : 'folder to inbox')) {
          this.counts[rule ? 'filed' : 'to inbox'] += 1;
        }
      } else {
        this.fileOne(item, this.rootId, false);
      }
    }
    if (String(inboxId).startsWith('new:')) return;
    for (const item of this.listChildren(inboxId)) {
      if (!this.timeLeft()) return;
      if (item.mimeType !== FOLDER_MIME) this.fileOne(item, inboxId, true);
    }
  }

  fileOne(file, fromId, inInbox) {
    if (file.ownedByMe === false) return;
    const rule = matchRule(splitExt(file.name)[0], RULES);
    if (!rule) {
      if (inInbox) return;
      if (this.move(file, fromId, this.folderFor(RULES.inbox), file.name, 'to inbox')) this.counts['to inbox'] += 1;
      return;
    }
    const newName = buildName(file.name, rule, RULES, this.stampOf(file));
    if (this.move(file, fromId, this.folderFor(rule.path), newName, newName !== file.name ? 'file and rename' : 'file')) {
      this.counts.filed += 1;
      if (newName !== file.name) this.counts.renamed += 1;
    }
  }

  // Walks 001 to 005 and returns every file with its folder path.
  walkTree() {
    const out = [];
    const stack = [];
    for (const main of RULES.main_folders) {
      if (main === RULES.trash_folder) continue;
      const id = this.childFolder(this.rootId, main, false);
      if (id) stack.push([id, main]);
    }
    while (stack.length) {
      if (Date.now() - this.started > TIME_BUDGET_MS) break;
      const [id, path] = stack.pop();
      for (const item of this.listChildren(id)) {
        if (item.mimeType === FOLDER_MIME) stack.push([item.id, path + '/' + item.name]);
        else out.push({file: item, path: path, parentId: id});
      }
    }
    return out;
  }

  labelForPath(path) {
    let best = null;
    for (const rule of RULES.rules) {
      if ((path === rule.path || path.startsWith(rule.path + '/')) && (!best || rule.path.length > best.path.length)) best = rule;
    }
    if (best) return [best, best.label];
    const main = path.split('/')[0];
    return [null, (RULES.main_folder_labels || {})[main] || main.slice(0, 3)];
  }

  isNeverRename(path) {
    return (RULES.drive.never_rename_inside || []).some(p => path === p || path.startsWith(p + '/'));
  }

  renameInsideTree(entries) {
    for (const e of entries) {
      if (!this.timeLeft()) return;
      if (e.path === RULES.inbox || e.path.startsWith(RULES.inbox + '/') || this.isNeverRename(e.path)) continue;
      if (!e.file.ownedByMe) continue;
      const [rule, label] = this.labelForPath(e.path);
      if (conforms(e.file.name, label)) continue;
      const newName = buildName(e.file.name, rule, RULES, this.stampOf(e.file), label);
      if (newName !== e.file.name && this.move(e.file, e.parentId, e.parentId, newName, 'rename')) {
        this.counts.renamed += 1;
        e.file.name = newName;
      }
    }
  }

  removeDuplicates(entries) {
    const groups = {};
    for (const e of entries) {
      if (!e.file.md5Checksum || !e.file.size || +e.file.size === 0) continue;
      const key = e.file.md5Checksum + ':' + e.file.size;
      (groups[key] = groups[key] || []).push(e);
    }
    for (const key of Object.keys(groups)) {
      const same = groups[key];
      if (same.length < 2) continue;
      same.sort((a, b) => {
        const pa = this.isNeverRename(a.path) ? 0 : 1, pb = this.isNeverRename(b.path) ? 0 : 1;
        if (pa !== pb) return pa - pb;
        const ca = conformsAny_(a.file.name) ? 0 : 1, cb = conformsAny_(b.file.name) ? 0 : 1;
        if (ca !== cb) return ca - cb;
        return new Date(a.file.createdTime) - new Date(b.file.createdTime);
      });
      const keeper = same[0];
      for (const e of same.slice(1)) {
        if (this.isNeverRename(e.path) || !e.file.ownedByMe) continue;
        this.trash(e.file, e.parentId, 'Same content as ' + keeper.path + '/' + keeper.file.name);
        e.trashed = true;
      }
    }
  }

  writeLog() {
    const folderId = this.folderFor(RULES.log_folder);
    const props = PropertiesService.getScriptProperties();
    let sheetId = props.getProperty('logSheetId');
    let ss = null;
    if (sheetId) { try { ss = SpreadsheetApp.openById(sheetId); } catch (err) { ss = null; } }
    if (!ss) {
      ss = SpreadsheetApp.create('004 Organizer Log ' + Utilities.formatDate(new Date(), this.tz, 'MM.dd.yyyy'));
      sheetId = ss.getId();
      props.setProperty('logSheetId', sheetId);
      if (!String(folderId).startsWith('new:')) Drive.Files.update({}, sheetId, null, {addParents: folderId, removeParents: this.rootId});
      ss.getSheets()[0].appendRow(['Run', 'Time', 'Action', 'Name', 'New Name', 'From Folder ID', 'To Folder ID', 'File ID', 'Note']);
    }
    const sheet = ss.getSheets()[0];
    const summary = this.summary();
    this.rows.push([this.runId, new Date(), 'summary', '', '', '', '', '', summary]);
    sheet.getRange(sheet.getLastRow() + 1, 1, this.rows.length, 9).setValues(this.rows);
    return summary;
  }

  summary() {
    const parts = Object.keys(this.counts).filter(k => this.counts[k]).map(k => this.counts[k] + ' ' + k);
    return (this.preview ? 'Preview, nothing changed. ' : '') + (parts.length ? parts.join(', ') : 'Nothing to organize');
  }

  execute() {
    this.buildStructure();
    this.fileLooseItems();
    if (this.timeLeft()) {
      const entries = this.walkTree();
      this.removeDuplicates(entries);
      this.renameInsideTree(entries.filter(e => !e.trashed));
    }
    const summary = this.writeLog();
    Logger.log(summary);
    return summary;
  }
}

function conformsAny_(name) {
  return /^00[1-6] /.test(name) && STAMP_AT_END.test(splitExt(name)[0]);
}

function undoLastRun() {
  const sheetId = PropertiesService.getScriptProperties().getProperty('logSheetId');
  if (!sheetId) { Logger.log('No run to undo.'); return; }
  const sheet = SpreadsheetApp.openById(sheetId).getSheets()[0];
  const values = sheet.getDataRange().getValues();
  const undone = new Set(values.map(r => String(r[0])).filter(r => / Undo$/.test(r)).map(r => r.replace(/ Undo$/, '')));
  let lastRun = null;
  for (let i = values.length - 1; i > 0; i--) {
    const run = String(values[i][0]);
    if (run.indexOf('Preview') === -1 && !/ Undo$/.test(run) && !undone.has(run)) { lastRun = run; break; }
  }
  if (!lastRun) { Logger.log('No run to undo.'); return; }
  let restored = 0;
  for (let i = values.length - 1; i > 0; i--) {
    const [run, , action, name, newName, fromId, toId, fileId] = values[i];
    if (String(run) !== lastRun || !fileId) continue;
    if (action === 'trash duplicate') {
      Drive.Files.update({trashed: false}, fileId); restored++;
    } else if (['file', 'file and rename', 'to inbox', 'file folder', 'folder to inbox', 'rename'].indexOf(action) !== -1) {
      const opts = {};
      if (toId && fromId && toId !== fromId) { opts.addParents = fromId; opts.removeParents = toId; }
      Drive.Files.update(name && name !== newName ? {name: name} : {}, fileId, null, opts); restored++;
    }
  }
  sheet.appendRow([lastRun + ' Undo', new Date(), 'undo', '', '', '', '', '', 'Restored ' + restored + ' items']);
  Logger.log('Restored ' + restored + ' items from run ' + lastRun);
}

// Lets the tests load the naming functions in Node. Apps Script ignores this.
if (typeof module !== 'undefined') {
  module.exports = {splitExt, extractDate, matchRule, cleanDescription, conforms, buildName, fixCase};
}
