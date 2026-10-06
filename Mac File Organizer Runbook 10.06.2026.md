# Mac File Organizer Runbook

Date: 10.06.2026
Owner: Mohammad Alamour
For: the Claude Code session running on the Mac

This runbook turns the approved plan into action. Read all of it before running anything.
The organizer script is "Mac File Organizer 10.06.2026.py" in this folder.


## 1. What is on the Mac today

Desktop and Documents iCloud sync is on. ~/Desktop and ~/Documents already live in iCloud Drive, so the root for the new structure is ~/Documents and nothing more is needed for sync.

~/Documents today, as recorded by the September 2026 organizer runs:

    00 Inbox                       holding piles, dated duplicate folders, an unsorted archive
    01 Personal                    about 15 numbered subfolders, among them 01 Career, 04 Receipts and Bills, 08 Sensitive, 10 Photography, 11 Images
    02 Work                        01 Bukrah Foundation, 03 VampireTools, 04 Safi, 05 Dr Seema Stories, 08 Huston Apartments (misspelled, with a trailing space), 09 Resistance X, and others
    03 Reference
    04 Quick Share
    05 Backup
    99 Archive
    To Be Organized                low confidence items from the nightly organizer
    To Be Printed
    To Trash
    Duplicates                     verified byte identical duplicates plus Kept Originals Manifest.txt
    Nightly Organize Logs          summaries, manifests, and Undo.sh scripts from the nightly organizer
    Cowork Organize Logs           logs from an earlier organizer
    Bukrah Scripts                 scripts that the Bukrah routines depend on
    Claude                         a no go zone, never touched
    OneDrive                       a symlink into ~/Library/CloudStorage, never touched
    ScanSnap Home folder           managed by the scanner app, never touched
    Personal From Bukrah Drive 08 2026, tapmenu, thobeelez, and other loose folders

Two systems already act on these folders and must be paused before anything moves:

    Scheduled tasks in ~/.claude/scheduled-tasks that move files: nightly-organize, organize-now, organize-preview, organize-dashboard, nightly-mac-organize, nightly-remote-organize. They file loose files into the 01 and 02 folders by hard coded paths and write to Nightly Organize Logs. They also hold lock folders inside Nightly Organize Logs.
    The Bukrah routines: bukrah-weekly-organize (Saturday 7:30 AM), bukrah-monthly-donor-ledger, bukrah-chase-statement-reminder, bukrah-compliance-check, bukrah-archive-monthly-run. They read and write inside 02 Work/01 Bukrah Foundation by hard coded paths.

The Bukrah Foundation folder is a mirror of the Bukrah Foundation Master Folder on Google Drive. It carries its own record system: OCR and OOR record classes, BF project codes, bilingual names. That system stays as it is. The folder moves as one unit and nothing inside it is renamed.


## 2. The approved rules

Six main folders, numbered 001 to 006, in ~/Documents.

    001 Inbox             new and unsorted files, kept empty after each pass
    002 Personal          identity, family, home, health, personal finance
    003 Work              every company, one folder each
    004 Reference         manuals, templates, guides, saved articles, archives
    005 To Be Printed     anything flagged for printing
    006 Trash             unwanted files, duplicates, installers, junk

Subfolders inside each main folder restart at 001 and use the same three digit style. Names come from the actual content. Examples:

    002 Personal
        001 Finance
        002 Health
        003 Home
        004 Identity
        005 Family
        006 Career
        007 Photography
    004 Reference
        001 Manuals
        002 Templates
        003 Articles
        008 Backups
        009 Archive
    006 Trash
        001 Duplicates
        002 Screenshots
        003 Installers

Work is the master folder for all companies. The company list is fixed:

    003 Work
        001 Bukrah Foundation
        002 Stories from Long Ago
        003 VampireTools
        004 Houston Apartments
        005 Safi Uncle
        006 Lubna
        007 Other Work

Every company folder except Bukrah Foundation uses the same five inside folders:

    001 Admin and Legal          formation docs, licenses, agreements, insurance
    002 Finance                  bank statements, invoices, receipts, taxes
    003 Clients and Partners     contracts, proposals, correspondence
    004 Build                    product, design, code, plans, anything being made
    005 Marketing                brand, content, website, social

Files that span companies or belong to none go in 007 Other Work. Resistance X, tapmenu, thobeelez, Jamal Thobe El Ez, Rahma Center, Bullionite, and 5PIE are not on the company list, so their files go to 007 Other Work in a subfolder named after them, unless the user adds them as companies 008 and up.


## 3. Mapping from the old layout to the new one

    00 Inbox                            001 Inbox, then every file inside gets filed like any other
    00 Inbox dated Verified Duplicates  006 Trash/001 Duplicates
    01 Personal                         002 Personal, subfolders renumbered from content
    02 Work/01 Bukrah Foundation        003 Work/001 Bukrah Foundation, moved whole, inside untouched
    02 Work/03 VampireTools             003 Work/003 VampireTools
    02 Work/04 Safi                     003 Work/005 Safi Uncle
    02 Work/05 Dr Seema Stories         003 Work/002 Stories from Long Ago
    02 Work/08 Huston Apartments        003 Work/004 Houston Apartments
    02 Work/09 Resistance X             003 Work/007 Other Work/001 Resistance X
    03 Reference                        004 Reference
    04 Quick Share                      001 Inbox, for review, it was a staging area
    05 Backup                           004 Reference/008 Backups
    99 Archive                          004 Reference/009 Archive
    To Be Organized                     001 Inbox, then filed from content
    To Be Printed                       005 To Be Printed
    To Trash                            006 Trash
    Duplicates                          006 Trash/001 Duplicates, keep Kept Originals Manifest.txt with them
    Nightly Organize Logs               004 Reference/009 Archive/001 Nightly Organizer Logs, moved whole after the tasks are paused
    Cowork Organize Logs                004 Reference/009 Archive/002 Cowork Organizer Logs, moved whole
    Bukrah Scripts                      003 Work/001 Bukrah Foundation/Bukrah Scripts, moved whole, after the routines are repointed
    Claude, OneDrive, ScanSnap Home folder   stay exactly where they are

Desktop and Downloads: every loose file is filed from content. Shortcut files (.webloc) and launcher html symlinks on the Desktop stay where they are, they are shortcuts and not documents. Folders on the Desktop that are projects, such as Stories from Long Ago and the SFLA folders, move whole into the matching company.

iCloud Drive root (~/Library/Mobile Documents/com~apple~CloudDocs) holds about 105 loose files, among them bank statements, tax returns, visas, and letters. Scan it as a fourth source so those get filed into ~/Documents too. App containers next to it are never touched. Only scan the CloudDocs folder itself.


## 4. File naming rule

Pattern:

    [code] [company, Work only] [document type] [person or party] [last 4 of account, policy, VIN, or invoice number] [period] [MM.DD.YYYY].ext

The code is the three digit code of the main folder. The date stamp is the file's last modified date. The script adds the code, the company, the stamp, and the extension. The session supplies the description in the middle. Examples of finished names:

    002 Chase Checking Statement Mohammad Alamour 4821 March 2026 03.31.2026.pdf
    002 Amex Statement Mohammad Alamour 1005 April 2026 04.30.2026.pdf
    002 T Mobile Detailed Bill Mohammad Alamour August 2026 08.14.2026.pdf
    002 CONFIDENTIAL India eVisa Approval Mohammad Alamour 09.03.2026.pdf
    002 CONFIDENTIAL Blue Life Health Ambulatory Summary Mohammad Alamour 08.20.2026.xml
    003 VampireTools CONFIDENTIAL Received Check McMaster Carr 07.21.2026.pdf
    003 Houston Apartments 886 Final Financials August 2026 08.17.2026.zip
    003 Safi Uncle Tidewater Property Aerial View 07.06.2026.png
    003 Stories from Long Ago Book 2 Sample 2 Generated Images 07.29.2026
    004 Toyota Camry Owner Manual 2022 08.01.2023.pdf
    005 Boarding Pass Mohammad Alamour Houston to New York 10.02.2026.pdf
    006 Screenshot of Safari window 09.01.2026.png

Hard rules:

    No dashes and no underscores anywhere, in folder or file names.
    Spaces and dots only, plus letters and digits. Arabic text in a name is kept.
    Never the full account number, only the last 4 digits.
    Never the home address, never a street number.
    The description names the person, the account or policy or invoice number, and the period, so nobody has to open the file to know what it is.
    A family member's statement carries that person's name.
    The word CONFIDENTIAL goes right after the code (after the company for Work) on identity documents, passport and visa scans, medical records, credentials, and check images. This carries forward the standing rule from the earlier organizer.
    Project folders, app bundles, and Pages, Numbers, and Keynote packages move as one unit and get one name.
    Camera originals that come in JPG and CR2 pairs keep matching names, pair by pair, or the whole photo folder moves as one unit.
    Nothing is deleted. Trash means moved to 006 Trash, renamed with the same rule.
    Google native stubs (.gdoc, .gsheet, .gslides) are pointers, not files. Leave them where they are and list them in notes.


## 5. Preconditions on the Mac

1. Run this from a Claude Code session on the Mac itself: the Claude Desktop app, or `claude remote-control` in a terminal. A cloud session cannot reach the files.
2. The kit is cloned outside the folders being organized:

       git clone -b claude/magical-curie-xbp4pp https://github.com/malamour88/bu.git ~/"Organizer Kit"

3. Confirm python3 runs. If it is missing, run `xcode-select --install` and retry.
4. Optional for the .xlsx spreadsheet: `python3 -m pip install --user openpyxl`. Without it the plan stays a CSV, which Numbers and Excel also open.
5. Pause the file moving scheduled tasks in the Claude desktop app before the scan: nightly-organize, organize-now, organize-preview, organize-dashboard, nightly-mac-organize, nightly-remote-organize, bukrah-weekly-organize, bukrah-archive-monthly-run. Confirm no lock folder is live:

       ls -la ~/Documents/"Nightly Organize Logs"/ | grep lock

   Do not run on a Saturday morning before the Bukrah session has finished.
6. Confirm the source folders with the user. Default: ~/Documents, ~/Desktop, ~/Downloads, and ~/Library/Mobile Documents/com~apple~CloudDocs. Ask once and use the answer.
7. Download iCloud placeholders so every file is local:

       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -print
       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -exec brctl download {} \;

   Wait until the find returns nothing. The scan flags any placeholder as needs download, and apply skips it.
8. Ask the user to close open documents. A file edited after the scan gets its stamp refreshed at apply time, and the log notes it.


## 6. Step by step

Set this once in the shell:

    ORG=~/"Organizer Kit/Mac File Organizer 10.06.2026.py"
    WORK=~/"Organizer Working"
    DOCS=~/Documents
    ICLOUD=~/"Library/Mobile Documents/com~apple~CloudDocs"

Step 0. Move the managed folders whole, before the scan, so their insides are never listed:

    mkdir -p "$DOCS/003 Work"
    mv "$DOCS/02 Work/01 Bukrah Foundation" "$DOCS/003 Work/001 Bukrah Foundation"

Nothing inside Bukrah Foundation is renamed. If the user later wants its loose root files named by the rule, that is a separate pass with the Bukrah routines paused.

Step 1. Scan.

    python3 "$ORG" scan "$DOCS" ~/Desktop ~/Downloads "$ICLOUD" --out "$WORK" \
      --exclude "$DOCS/003 Work/001 Bukrah Foundation" \
      --exclude "$DOCS/Claude" --exclude "$DOCS/Bukrah Scripts" \
      --exclude "$DOCS/Nightly Organize Logs" --exclude "$DOCS/Cowork Organize Logs"

Outputs: Inventory MM.DD.YYYY.json and Plan MM.DD.YYYY.csv. The inventory holds a content snippet, Spotlight metadata, hash, size, dates, and flags for each item. The plan is the editable work list. Flags to act on: duplicate, installer, archive extracted, zero bytes, temp file, screenshot, empty folder, old structure, already organized, needs read, needs download, project folder, bundle, symlink.

Step 2. Fill the plan. This is the session's main work. For each row set three columns:

    action       move, trash, print, or skip
    new folder   the destination relative to the root, for example 002 Personal/001 Finance
    new name     the description only. The script adds code, company, stamp, and extension.

How to decide:

    Read the snippet in the inventory first. When a row is flagged needs read, open the file with the Read tool. PDFs and images are readable that way. For docx and rtf use textutil -convert txt -stdout "file".
    Pull the identifiers into the description: who, which account or policy or invoice, which period.
    Use the mapping in section 3 to choose the destination. The old subfolder a file sat in is a strong hint, the content decides.
    Rows flagged duplicate, installer, zero bytes, temp file, archive extracted, or empty folder are prefilled as trash. Keep that unless the content says otherwise.
    Screenshots: trash unless the image holds something worth keeping, then move it where it belongs with a description of what it shows.
    Rows flagged already organized are prefilled as skip. Leave them.
    Symlinks and .webloc shortcuts: skip.
    Anything that must be printed gets action print. The script places it in 005 To Be Printed.
    Project folders and bundles move as a whole. Name them by what they are, for example "Website Source Code" or "Pitch Deck".
    If the content does not say which company a Work file belongs to, use 003 Work/007 Other Work and write the reason in notes.
    If a file is unreadable or its purpose is unclear, send it to 001 Inbox with a short note. Never guess a name.
    Never leave a row blank. Blank means undecided and apply refuses to run.

Work in batches of 25 to 40 rows. For more than about 150 rows, fan the batches out with the Workflow tool, one agent per batch, each returning the id, action, new folder, new name, and notes for its rows, then merge back into the CSV. Keep the inventory JSON as the source for snippets.

Step 3. Check until clean.

    python3 "$ORG" check "$WORK/Plan MM.DD.YYYY.csv"

Fix every ERROR line. Warnings are allowed but read them. The check also rejects two rows that would land on the same destination name.

Step 4. Build the approval spreadsheet and hand it to the user.

    python3 "$ORG" sheet "$WORK/Plan MM.DD.YYYY.csv"

This writes Plan MM.DD.YYYY.xlsx with the final composed names in the new name column, a dropdown on action, and a Rules tab. Send the file to the user. Say in one line how many rows go to each main folder and how many go to trash. Wait for approval. The user may edit action, new folder, and new name in the spreadsheet. Any edit is normalized again on apply, so a typed name without the stamp still comes out right.

Step 5. Apply, dry run first.

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK"

Read the preview. Then execute:

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK" --execute --prune-empty \
      --source "$DOCS" --source ~/Desktop --source ~/Downloads --source "$ICLOUD"

The change log lands in the working folder. Moving keeps the modified date, so the stamp stays true. A destination name that already exists gets a run number before the stamp. A file identical to one already at its destination goes to 006 Trash/001 Duplicates instead. Empty source folders are removed, never the sources named with --source, never home folders, never iCloud Drive.

Step 6. Move the remaining managed folders whole:

    mkdir -p "$DOCS/004 Reference/009 Archive"
    mv "$DOCS/Nightly Organize Logs" "$DOCS/004 Reference/009 Archive/001 Nightly Organizer Logs"
    mv "$DOCS/Cowork Organize Logs" "$DOCS/004 Reference/009 Archive/002 Cowork Organizer Logs"

Leave Bukrah Scripts in place until step 8 has repointed the routines.

Step 7. Verify.

    python3 "$ORG" verify --root "$DOCS" --out "$WORK" \
      --exclude "$DOCS/003 Work/001 Bukrah Foundation" --exclude "$DOCS/Claude" \
      --exclude "$DOCS/Bukrah Scripts" --exclude "$DOCS/004 Reference/009 Archive"

Zero problems is the target. Fix any violation by editing the plan row and applying again, or by a direct rename that follows the rule.

Step 8. Repoint the scheduled tasks. Every task under ~/.claude/scheduled-tasks that names an old path needs the new path. Grep them:

    grep -rl "02 Work\|01 Personal\|00 Inbox\|To Be Organized\|Nightly Organize Logs" ~/.claude/scheduled-tasks

Replace by the mapping in section 3, above all "02 Work/08 Huston Apartments " with the trailing space, which becomes "003 Work/004 Houston Apartments", and "02 Work/01 Bukrah Foundation", which becomes "003 Work/001 Bukrah Foundation". Then propose to the user whether the nightly organizer keeps running, repointed to file new files into 001 Inbox with this naming rule, or is retired. Do not turn it back on before the user answers.

Step 9. Report to the user in a few lines: counts per main folder, how many went to trash, the change log path, and the undo command. The undo command is:

    python3 "$ORG" undo "$WORK/Change Log MM.DD.YYYY HHMM.csv" --execute

Step 10. Leftover old folders. After a clean verify, the old numbered folders such as "00 Inbox", "01 Personal", "02 Work" should be empty and removed by prune. If any survive, list what is still inside and ask.


## 7. Privacy

The working folder holds private names, last 4 digits, and content snippets. It stays on the Mac. The .gitignore in this kit blocks those files from being committed. Never push the working folder, never paste full account numbers into a name, and never put the home address in a name. The contents of the old 08 Sensitive folder are never described in the chat, only filed.


## 8. Command reference

    scan   FOLDER... --out DIR [--exclude DIR] [--no-spotlight]
    check  PLAN
    sheet  PLAN [--out FILE] [--to-csv]
    apply  PLAN --root DIR --out DIR [--execute] [--prune-empty] [--source DIR] [--allow-undecided] [--show N]
    verify --root DIR --out DIR [--exclude DIR] [--show N]
    undo   LOG [--execute]

PLAN is the CSV or the xlsx. Every command is safe to rerun. apply and undo move nothing without --execute.
