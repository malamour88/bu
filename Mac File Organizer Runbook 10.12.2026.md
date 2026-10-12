# Mac File Organizer Runbook

Date: 10.12.2026
Owner: Mohammad Alamour
For: the Claude Code session running on the Mac

This runbook turns the approved plan into action. Read all of it before running anything.
The organizer script is "Mac File Organizer 10.12.2026.py" in this folder.


## 0. Where the run stands on 10.12.2026

Done on the Mac in the 10.07.2026 session:

    The kit is cloned at ~/Organizer Kit. That clone is two commits behind this version. Update it first, section 5 item 2.
    The working folder ~/Organizer Working exists and is empty.
    nightly-organize and bukrah-weekly-organize are disabled. They were the only enabled tasks that move files.
    Desktop and Documents iCloud sync is confirmed on. Zero .icloud placeholders were found under Documents, Desktop, Downloads, and iCloud Drive.
    python3 is 3.9 from the Command Line Tools. pypdf is installed.
    The first scan ran for seven minutes and died on a corrupt .docx inside To Be Organized. This version catches that error and every other text extraction error. An unreadable file gets the needs read flag and the scan goes on.

Decisions Mohammad made on 10.07.2026 and 10.12.2026. They are folded into every section below.

    The first pass covers Desktop, Downloads, and Documents. The iCloud Drive root is a second pass after this one is verified.
    Code repos and log folders move as one unit each: thobeelez, tapmenu, design-log, Nightly Organize Logs, Cowork Organize Logs, and Bukrah Scripts. Claude stays exactly where it is.
    The old trash folders move whole into 006 Trash, never row by row: Documents/To Trash with 3,638 files, Desktop/To Trash, Documents/Duplicates, and 02 Work/Review and Trash.
    The Bukrah working folders on the Desktop move whole into the Bukrah Foundation folder with their names and contents untouched: Bukrah Intake 09 08 2026, Bukrah Intake 10.05.2026, Bukrah Evidence Staging 10.05.2026, and Bukrah Letterhead. The Saturday Bukrah session files them.
    Bukrah Foundation moves whole in step 0 as planned. The scheduled tasks that hard code its path are repointed in step 6, right after apply, in the same sitting.
    No more questions to Mohammad before the approval spreadsheet. Start organizing and name every file from its content.


## 1. What is on the Mac today

Desktop and Documents iCloud sync is on. ~/Desktop and ~/Documents already live in iCloud Drive, so the root for the new structure is ~/Documents and nothing more is needed for sync.

~/Documents on 10.07.2026, with file counts:

    00 Inbox                           62      holding piles, dated duplicate folders, an unsorted archive
    01 Personal                        314     about 15 numbered subfolders, among them 01 Career, 04 Receipts and Bills, 08 Sensitive, 10 Photography, 11 Images
    02 Work                            1,141   01 Bukrah Foundation, 03 VampireTools, 04 Safi, 05 Dr Seema Stories, 08 Huston Apartments (misspelled, with a trailing space), 09 Resistance X, Review and Trash, and others
    03 Reference                       10
    04 Quick Share                     0
    05 Backup                          0
    99 Archive                         34
    To Be Organized                    1,406   low confidence items from the nightly organizer
    To Be Printed                      13
    To Trash                           3,638   dated folders from earlier cleanups
    Duplicates                         19      verified byte identical duplicates plus Kept Originals Manifest.txt
    Nightly Organize Logs              131     summaries, manifests, and Undo.sh scripts from the nightly organizer
    Cowork Organize Logs               1       logs from an earlier organizer
    Bukrah Scripts                     10      scripts that the Bukrah routines depend on, not a git repo
    thobeelez                          22,783  a Next.js git repo with node_modules, clean working tree
    tapmenu                            51      a web app folder with README, index.html, admin.html, assets
    design-log                         1
    Personal From Bukrah Drive 08 2026 4
    Claude                             6,618   a no go zone, never touched
    OneDrive                           a symlink into ~/Library/CloudStorage, never touched
    ScanSnap Home folder               managed by the scanner app, never touched

~/Desktop holds about 3,000 items. Among them: five carrier tracking PDFs from 10.05.2026 with dashes in their names, Bukrah Foundation Invoice Period 1 08.14.2026.pdf, the four Bukrah working folders named in section 0 (Bukrah Intake 09 08 2026 alone holds 1,094 files), a Claude outputs folder, a To Trash folder, .webloc shortcuts, and project folders such as Stories from Long Ago and the SFLA folders.

~/Downloads is the third source. Everything in it is filed from content like any other file.

The iCloud Drive root (~/Library/Mobile Documents/com~apple~CloudDocs) holds 164 top level entries and 8,420 files, among them Mohammad Personal, Vampire Tools, Bullionite, 5PIE, Cloud Library, Archive, and loose bank statements, tax returns, visas, and letters. It is the second pass. Only the CloudDocs folder itself is ever scanned, never the app containers next to it.

Two systems act on these folders. Both are paused:

    Scheduled tasks in ~/.claude/scheduled-tasks that move files: nightly-organize (disabled 10.07.2026), organize-now, organize-preview, organize-dashboard, nightly-mac-organize, nightly-remote-organize. They file loose files into the 01 and 02 folders by hard coded paths and write to Nightly Organize Logs. They also hold lock folders inside Nightly Organize Logs.
    The Bukrah routines: bukrah-weekly-organize (Saturday 7:30 AM, disabled 10.07.2026), bukrah-monthly-donor-ledger, bukrah-chase-statement-reminder, bukrah-compliance-check, bukrah-archive-monthly-run. They read and write inside 02 Work/01 Bukrah Foundation by hard coded paths.
    safi-daily-plan-sync (6:32 AM daily) and houston-monthly-report-check also name paths under 02 Work. Step 6 repoints them.

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

Files that span companies or belong to none go in 007 Other Work. Projects that are not on the company list get their own subfolder there:

    003 Work/007 Other Work
        001 Resistance X
        002 Tapmenu
        003 Thobeelez
        004 and up               Jamal Thobe El Ez, Rahma Center, Bullionite, 5PIE, and others as the passes reach them, unless Mohammad adds them as companies 008 and up

A folder that moves whole is one plan row of kind project folder. It gets one name by the naming rule in section 4, with no extension, and nothing inside it is listed or renamed. Verify never looks inside it.


## 3. Mapping from the old layout to the new one

~/Documents:

    00 Inbox                            001 Inbox, then every file inside gets filed like any other
    00 Inbox dated Verified Duplicates  006 Trash/001 Duplicates
    01 Personal                         002 Personal, subfolders renumbered from content
    02 Work/01 Bukrah Foundation        003 Work/001 Bukrah Foundation, moved whole in step 0, inside untouched
    02 Work/03 VampireTools             003 Work/003 VampireTools
    02 Work/04 Safi                     003 Work/005 Safi Uncle
    02 Work/05 Dr Seema Stories         003 Work/002 Stories from Long Ago
    02 Work/08 Huston Apartments        003 Work/004 Houston Apartments
    02 Work/09 Resistance X             003 Work/007 Other Work/001 Resistance X
    02 Work/Review and Trash            006 Trash, one whole row, action trash, description Review and Trash from Work
    03 Reference                        004 Reference
    04 Quick Share                      001 Inbox, for review, it was a staging area
    05 Backup                           004 Reference/008 Backups
    99 Archive                          004 Reference/009 Archive
    To Be Organized                     001 Inbox, then filed from content
    To Be Printed                       005 To Be Printed
    To Trash                            006 Trash, one whole row, action trash, description To Trash from Documents
    Duplicates                          006 Trash/001 Duplicates, one whole row, action trash, description Duplicates from Documents, Kept Originals Manifest.txt stays inside
    Nightly Organize Logs               004 Reference/009 Archive, one whole row, description Nightly Organizer Logs
    Cowork Organize Logs                004 Reference/009 Archive, one whole row, description Cowork Organizer Logs
    design-log                          004 Reference/009 Archive, one whole row, description from its content
    tapmenu                             003 Work/007 Other Work/002 Tapmenu, one whole row, description from its README
    thobeelez                           003 Work/007 Other Work/003 Thobeelez, one whole row, description from its README
    Bukrah Scripts                      003 Work/001 Bukrah Foundation/Bukrah Scripts, moved whole by hand in step 7, after the routines are repointed
    Personal From Bukrah Drive 08 2026  002 Personal, four files filed from content
    Claude, OneDrive, ScanSnap Home folder   stay exactly where they are

~/Desktop:

    Bukrah Intake 09 08 2026, Bukrah Intake 10.05.2026, Bukrah Evidence Staging 10.05.2026, Bukrah Letterhead
                                        003 Work/001 Bukrah Foundation, moved whole by hand in step 0, names kept
    To Trash                            006 Trash, one whole row, action trash, description To Trash from Desktop
    Claude outputs                      the files inside are filed from content
    .webloc shortcuts and launcher html symlinks   skip, they are shortcuts and not documents
    Project folders such as Stories from Long Ago and the SFLA folders   move whole into the matching company
    Every other loose file              filed from content

~/Downloads: every loose file is filed from content. Installers and archives that were already extracted are trash.

iCloud Drive root: second pass, after this run is verified. Its app containers are never touched.


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

Whole folders follow the same pattern with no extension. The stamp is the newest file inside the folder:

    006 To Trash from Documents 10.05.2026
    004 Nightly Organizer Logs 10.06.2026
    003 Thobeelez Website Source Code 07.29.2026

Hard rules:

    No dashes and no underscores anywhere, in folder or file names.
    The only separators are spaces and dots. Letters, digits, and Arabic text are kept. Parentheses, commas, and apostrophes that are part of a title are allowed.
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
2. Bring the kit to this version. The clone from 10.06.2026 is behind:

       cd ~/"Organizer Kit" && git fetch origin claude/busy-darwin-7bdkts && git checkout claude/busy-darwin-7bdkts && git pull origin claude/busy-darwin-7bdkts
       ls ~/"Organizer Kit"

   The listing must show "Mac File Organizer 10.12.2026.py" and this runbook. If the kit folder is missing:

       git clone -b claude/busy-darwin-7bdkts https://github.com/malamour88/bu.git ~/"Organizer Kit"

3. python3 runs. Confirmed 3.9 on 10.07.2026.
4. Optional for the .xlsx spreadsheet: `python3 -c "import openpyxl"`. If that fails, `python3 -m pip install --user openpyxl`. Without it the plan stays a CSV, which Numbers and Excel also open.
5. The file moving tasks are already paused. Confirm no lock folder is live:

       ls -la ~/Documents/"Nightly Organize Logs"/ | grep lock

   Do not run on a Saturday morning before the Bukrah session has finished.
6. Sources are decided: ~/Documents, ~/Desktop, ~/Downloads. Do not ask again.
7. Confirm every file is local. Zero placeholders were found on 10.07.2026, so this is a quick recheck:

       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -print
       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -exec brctl download {} +

   Wait until the find returns nothing. The scan flags any placeholder as needs download, and apply skips it.
8. Tell Mohammad in one line that the scan is starting and that open documents should be closed. Do not wait for an answer. A file edited after the scan gets its stamp refreshed at apply time, and the log notes it.


## 6. Step by step

Set this once in the shell:

    ORG=~/"Organizer Kit/Mac File Organizer 10.12.2026.py"
    WORK=~/"Organizer Working"
    DOCS=~/Documents

Step 0. Move the managed folders whole, before the scan, so their insides are never listed:

    mkdir -p "$DOCS/003 Work"
    mv "$DOCS/02 Work/01 Bukrah Foundation" "$DOCS/003 Work/001 Bukrah Foundation"
    for f in "Bukrah Intake 09 08 2026" "Bukrah Intake 10.05.2026" "Bukrah Evidence Staging 10.05.2026" "Bukrah Letterhead"; do
      if [ -e ~/Desktop/"$f" ] && [ ! -e "$DOCS/003 Work/001 Bukrah Foundation/$f" ]; then
        mv ~/Desktop/"$f" "$DOCS/003 Work/001 Bukrah Foundation/$f"
      fi
    done
    ls "$DOCS/003 Work/001 Bukrah Foundation"

If a Desktop folder did not move because a folder of the same name already sits inside Bukrah Foundation, leave it on the Desktop and list it in the notes for the Saturday session. Nothing inside Bukrah Foundation is renamed. If Mohammad later wants its loose root files named by the rule, that is a separate pass with the Bukrah routines paused.

Then create the skeleton, the six main folders and every company with its five standard subfolders:

    python3 "$ORG" init --root "$DOCS"

Step 1. Scan. One command, all three sources, the whole folders named, the no go zones excluded:

    python3 "$ORG" scan "$DOCS" ~/Desktop ~/Downloads --out "$WORK" \
      --exclude "$DOCS/003 Work/001 Bukrah Foundation" \
      --exclude "$DOCS/Claude" --exclude "$DOCS/Bukrah Scripts" \
      --whole "$DOCS/To Trash" --whole ~/Desktop/"To Trash" \
      --whole "$DOCS/Duplicates" --whole "$DOCS/02 Work/Review and Trash" \
      --whole "$DOCS/Nightly Organize Logs" --whole "$DOCS/Cowork Organize Logs" \
      --whole "$DOCS/design-log" --whole "$DOCS/tapmenu" --whole "$DOCS/thobeelez"

The scan prints a line every 500 items. It stops with a clear error if a --whole folder does not exist. Drop that one flag and rerun. If it stops on a traceback, fix the cause in the script, note the fix in the report, and rerun with the same sources.

Outputs: Inventory MM.DD.YYYY.json and Plan MM.DD.YYYY.csv. The inventory holds a content snippet, Spotlight metadata, hash, size, dates, and flags for each item. The plan is the editable work list. Flags to act on: duplicate, installer, archive extracted, zero bytes, temp file, screenshot, empty folder, old structure, already organized, needs read, needs download, project folder, moved whole, bundle, symlink.

Step 2. Fill the plan. This is the session's main work. For each row set three columns:

    action       move, trash, print, or skip
    new folder   the destination relative to the root, for example 002 Personal/001 Finance
    new name     the description only. The script adds code, company, stamp, and extension. A trash or print row with a blank description keeps the old file name as its description.

How to decide:

    Read the snippet in the inventory first. When a row is flagged needs read, open the file with the Read tool. PDFs and images are readable that way. For docx and rtf use textutil -convert txt -stdout "file".
    Pull the identifiers into the description: who, which account or policy or invoice, which period. Write a period as "March 2026" or "Q1 2026". A date inside the description in MM.DD.YYYY form is kept, the stamp is added after it.
    Use the mapping in section 3 to choose the destination. The old subfolder a file sat in is a strong hint, the content decides.
    Rows flagged moved whole take their destination and description from section 3. For tapmenu, thobeelez, and design-log the description comes from the README or the content.
    Rows flagged duplicate, installer, zero bytes, temp file, archive extracted, or empty folder are prefilled as trash. Keep that unless the content says otherwise.
    Screenshots: trash unless the image holds something worth keeping, then move it where it belongs with a description of what it shows.
    Rows flagged already organized are prefilled as skip. Leave them.
    Symlinks and .webloc shortcuts: skip.
    Anything that must be printed gets action print. The script places it in 005 To Be Printed.
    Project folders and bundles move as a whole. Name them by what they are, for example "Website Source Code" or "Pitch Deck".
    If the content does not say which company a Work file belongs to, use 003 Work/007 Other Work and write the reason in notes.
    If a file is unreadable or its purpose is unclear, send it to 001 Inbox with a short note. Never guess a name.
    Never leave a row blank. Blank means undecided and apply refuses to run.

Expect several thousand rows. Rows prefilled trash or skip by their flags need only a glance. Work the rest in batches of 25 to 40 rows. Fan the batches out with the Workflow tool, one agent per batch, each returning the id, action, new folder, new name, and notes for its rows, then merge back into the CSV. Keep the inventory JSON as the source for snippets.

Step 3. Check until clean.

    python3 "$ORG" check "$WORK/Plan MM.DD.YYYY.csv"

Fix every ERROR line. Warnings are allowed but read them. The check also rejects two rows that would land on the same destination name.

Step 4. Build the approval spreadsheet and hand it to Mohammad.

    python3 "$ORG" sheet "$WORK/Plan MM.DD.YYYY.csv"

This writes Plan MM.DD.YYYY.xlsx with the final composed names in the new name column, a dropdown on action, and a Rules tab. Send the file. Say in one line how many rows go to each main folder and how many go to trash. Wait for approval. Mohammad may edit action, new folder, and new name in the spreadsheet. Any edit is normalized again on apply, so a typed name without the stamp still comes out right. This is the only stop before apply.

Step 5. Apply, dry run first.

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK"

Read the preview. Then execute:

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK" --execute --prune-empty \
      --source "$DOCS" --source ~/Desktop --source ~/Downloads

The change log is written row by row while apply runs, so an interrupted run still has a complete undo record for every move it made. Trash and print rows run before move rows, so a slot they vacate is free for the file that takes it. A file whose name changes only in letter case is renamed in place. Moving keeps the modified date, so the stamp stays true. A destination name that already exists gets a run number before the stamp. A file identical to one already at its destination goes to 006 Trash/001 Duplicates instead. Empty source folders are removed, never the sources named with --source, never home folders, never iCloud Drive.

Step 6. Repoint the scheduled tasks right after apply, in the same sitting. Every task under ~/.claude/scheduled-tasks that names an old path needs the new path. Grep them:

    grep -rl "02 Work\|01 Personal\|00 Inbox\|To Be Organized\|Nightly Organize Logs\|Bukrah Scripts" ~/.claude/scheduled-tasks

On 10.07.2026 the hits were nightly-organize, bukrah-weekly-organize, bukrah-chase-statement-reminder, bukrah-monthly-donor-ledger, bukrah-compliance-check, and safi-daily-plan-sync. Replace by the mapping in section 3, above all "02 Work/08 Huston Apartments " with the trailing space, which becomes "003 Work/004 Houston Apartments", "02 Work/01 Bukrah Foundation", which becomes "003 Work/001 Bukrah Foundation", and "02 Work/04 Safi", which becomes "003 Work/005 Safi Uncle". safi-daily-plan-sync runs every morning, so it must be repointed before the next 6:32 AM.

Step 7. Move Bukrah Scripts whole, now that the routines point at the new path:

    mv "$DOCS/Bukrah Scripts" "$DOCS/003 Work/001 Bukrah Foundation/Bukrah Scripts"

Repoint any task prompt or script that names ~/Documents/Bukrah Scripts. Then re enable bukrah-weekly-organize so the Saturday session runs again. Leave nightly-organize off.

Step 8. Verify.

    python3 "$ORG" verify --root "$DOCS" --out "$WORK" \
      --exclude "$DOCS/003 Work/001 Bukrah Foundation" --exclude "$DOCS/Claude" --exclude "$DOCS/OneDrive"

Zero problems is the target. Verify also lists any skeleton folder that is missing, which init creates. Fix any naming violation by editing the plan row and applying again, or by a direct rename that follows the rule.

Step 9. Report to Mohammad in a few lines: counts per main folder, how many went to trash, the change log path, and the undo command. The undo command is:

    python3 "$ORG" undo "$WORK/Change Log MM.DD.YYYY HHMM.csv" --execute

Step 10. Leftover old folders. After a clean verify, the old numbered folders such as "00 Inbox", "01 Personal", "02 Work" should be empty and removed by prune. If any survive, list what is still inside and ask.

Step 11. Propose to Mohammad whether the nightly organizer keeps running, repointed to file new files into 001 Inbox with this naming rule, or is retired. Do not turn it back on before he answers. Then propose the iCloud Drive root as the second pass.


## 7. Privacy

The working folder holds private names, last 4 digits, and content snippets. It stays on the Mac. The .gitignore in this kit blocks those files from being committed. Never push the working folder, never paste full account numbers into a name, and never put the home address in a name. The contents of the old 08 Sensitive folder are never described in the chat, only filed.


## 8. Command reference

    init   --root DIR
    scan   FOLDER... --out DIR [--exclude DIR] [--whole DIR] [--no-spotlight]
    check  PLAN
    sheet  PLAN [--out FILE] [--to-csv]
    apply  PLAN --root DIR --out DIR [--execute] [--prune-empty] [--source DIR] [--allow-undecided] [--show N]
    verify --root DIR --out DIR [--exclude DIR] [--show N]
    undo   LOG [--execute]

PLAN is the CSV or the xlsx. --exclude and --whole repeat. A --whole folder must sit inside a scanned folder and is listed as one unit. Every command is safe to rerun. apply and undo move nothing without --execute.
