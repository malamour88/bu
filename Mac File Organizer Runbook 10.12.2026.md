# Mac File Organizer Runbook

Date: 10.12.2026
Owner: Mohammad Alamour
For: the Claude Code session running on the Mac

This runbook turns the approved plan into action. Read all of it before running anything.
The kit in this folder: "Mac File Organizer 10.12.2026.py" (the script) and "Plan Filler Workflow 10.12.2026.js" (the fan out that fills the plan).


## 0. Where the run stands on 10.12.2026

Done on the Mac in the 10.07.2026 session:

    The kit is cloned at ~/Organizer Kit. That clone is behind this version. Update it first, section 5 item 2.
    The working folder ~/Organizer Working exists and is empty.
    nightly-organize and bukrah-weekly-organize are disabled. They were the only enabled tasks that move files.
    Desktop and Documents iCloud sync is confirmed on. Zero .icloud placeholders were found under Documents, Desktop, Downloads, and iCloud Drive.
    python3 is 3.9.6 from the Command Line Tools. openpyxl 3.1.5 and pypdf are installed.
    The first scan ran for seven minutes and died on a corrupt .docx inside To Be Organized. This version catches that error and every other text extraction error. An unreadable file gets the needs read flag and the scan goes on.

Decisions Mohammad made on 10.07.2026 and 10.12.2026. They are folded into every section below.

    The first pass covers Desktop, Downloads, and Documents. The iCloud Drive root is a second pass after this one is verified.
    Code repos and log folders move as one unit each: thobeelez, tapmenu, design-log, Nightly Organize Logs, Cowork Organize Logs, and Bukrah Scripts. Claude stays exactly where it is.
    The old trash folders move whole into 006 Trash, never row by row: Documents/To Trash with 3,638 files, Desktop/To Trash with 977 files, Documents/Duplicates, and 02 Work/Review and Trash.
    The Bukrah working folders on the Desktop move whole into the Bukrah Foundation folder with their names and contents untouched: Bukrah Intake 09 08 2026, Bukrah Intake 10.05.2026, Bukrah Evidence Staging 10.05.2026, and Bukrah Letterhead. The Saturday Bukrah session files them.
    Bukrah Foundation moves whole in step 0 as planned. The scheduled tasks that hard code its path are repointed in step 6, right after apply, in the same sitting.
    No more questions to Mohammad before the approval spreadsheet. Start organizing and name every file from its content.


## 1. What is on the Mac today

Desktop and Documents iCloud sync is on. ~/Desktop and ~/Documents already live in iCloud Drive, so the root for the new structure is ~/Documents and nothing more is needed for sync.

~/Documents on 10.07.2026, with file counts:

    00 Inbox                           62      holding piles, dated duplicate folders, an unsorted archive
    01 Personal                        314     about 15 numbered subfolders, among them 00 Command Center, 01 Career, 02 Plan and Goals, 04 Receipts and Bills, 08 Sensitive, 10 Photography, 11 Images
    02 Work                            1,141   see the subfolder list below
    03 Reference                       10
    04 Quick Share                     0
    05 Backup                          0
    99 Archive                         34
    To Be Organized                    1,406   low confidence items from the nightly organizer, many already carry a description and a spaced date such as "DMV Vehicle Registration Renewal Confirmation 07 17 2026.png"
    To Be Printed                      13
    To Trash                           3,638   dated folders from earlier cleanups
    Duplicates                         19      verified byte identical duplicates plus Kept Originals Manifest.txt
    Nightly Organize Logs              131     summaries, manifests, and Undo.sh scripts from the nightly organizer
    Cowork Organize Logs               1       logs from an earlier organizer
    Bukrah Scripts                     10      bukrah-archive-monthly-run.py, bukrah-retire-project.py, their state and logs, not a git repo
    thobeelez                          22,783  a Next.js git repo with node_modules, clean working tree
    tapmenu                            51      a web app folder with README, index.html, admin.html, assets
    design-log                         1
    Personal From Bukrah Drive 08 2026 4
    Claude                             6,618   a no go zone, never touched
    OneDrive                           a symlink into ~/Library/CloudStorage, never touched
    ScanSnap Home folder               managed by the scanner app, never touched

02 Work subfolders with file counts:

    01 Bukrah Foundation               231     moves whole in step 0
    02 Rahma Center                    55
    03 VampireTools                    83
    04 Safi                            113     holds 03 Other/01 Scheduling/safi-uncle-daily-plan.html, read every morning by safi-daily-plan-sync
    05 Dr Seema Stories                330
    06 5PIE                            6
    08 Huston Apartments               57      misspelled, with a trailing space
    09 5PIE                            1
    09 Resistance X                    264
    Archived Work                      0
    Review and Trash                   1

~/Desktop holds 2,979 files. Folders: Stories from Long Ago (625), SFLA Book 2 Sample 2 Generated (55), SFLA Book 2 Gemini Reference Images (19), Water Project Forms (12), Orientations 08 2026 (4), Claude outputs (59, Claude Code context packs and three .py helpers), To Trash (977), and the four Bukrah working folders named in section 0 (Bukrah Intake 09 08 2026 alone holds 1,094 files). Loose files: five carrier tracking PDFs from 10.05.2026 with dashes in their names, two Pirate Ship shipping PDFs, Bukrah Foundation Invoice Period 1 08.14.2026.pdf, a timesheet earning statement, 16 screenshots, two .webloc shortcuts, and two html symlinks (Houston Dashboard, VT SharePoint Proposal).

~/Downloads holds 131 files, most of them Bukrah Foundation documents (BF packet and template PDFs, financial reports, Masar audit material, a board deck), plus a Jamal Thobe El Ez folder, Stories From Long Ago booth print files, a T Mobile bill, a VPTI sales report, a UPS refund check, and a video download with its zip.

The iCloud Drive root (~/Library/Mobile Documents/com~apple~CloudDocs) holds 164 top level entries and 8,420 files, among them Mohammad Personal, Vampire Tools, Bullionite, 5PIE, Rahma Center, Safi, Dr Seema Stories, Cloud Library, Archive, and about 40 loose bank statements from four accounts. It is the second pass. Only the CloudDocs folder itself is ever scanned, never the app containers next to it.

Scheduled tasks under ~/.claude/scheduled-tasks on 10.07.2026, ten registered:

    safi-daily-plan-sync               enabled, 6:32 AM daily, reads 02 Work/04 Safi/03 Other/01 Scheduling/safi-uncle-daily-plan.html
    houston-monthly-report-check       enabled, day 12 monthly
    bukrah-monthly-donor-ledger        enabled, day 3 monthly, reads and writes inside 02 Work/01 Bukrah Foundation
    bukrah-chase-statement-reminder    enabled, day 1 monthly, reads inside 02 Work/01 Bukrah Foundation
    bukrah-compliance-check            enabled, quarterly, reads inside 02 Work/01 Bukrah Foundation
    nightly-organize                   disabled 10.07.2026, the file mover, hard codes 00 Inbox, 01 Personal, 02 Work, Nightly Organize Logs
    bukrah-weekly-organize             disabled 10.07.2026, Saturday 7:33 AM, reads and writes inside 02 Work/01 Bukrah Foundation
    daily-safi-ops-brief               disabled, retired
    personal-morning-briefing          disabled, reads 01 Personal/00 Command Center/PERSONAL-PLAYBOOK.md
    personal-weekly-review             disabled, reads 01 Personal/00 Command Center/PERSONAL-PLAYBOOK.md

Task folders that are not registered but still name old paths: job-matches-daily (runs two .py generators and reads Active Jobs Search Tracker.xlsx inside 01 Personal/02 Plan and Goals), bukrah-archive-monthly-run and archive-upload-check (name Bukrah Scripts), weekly-progress-upkeep. Step 6 repoints all of them.

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

Bukrah Foundation keeps its own inside structure. Loose Bukrah files found anywhere else (Downloads, To Be Organized, Inbox, Desktop) go to one staging folder inside it, named by the rule, for the Saturday Bukrah session to file by its own system:

    003 Work/001 Bukrah Foundation/001 Organizer Intake

Files that span companies or belong to none go in 007 Other Work. Projects that are not on the company list get their own subfolder there:

    003 Work/007 Other Work
        001 Resistance X
        002 Tapmenu
        003 Thobeelez
        004 Rahma Center
        005 5PIE
        006 Jamal Thobe El Ez
        007 and up               Bullionite and others as the passes reach them, unless Mohammad adds them as companies 008 and up

A folder that moves whole is one plan row of kind project folder. It gets one name by the naming rule in section 4, with no extension, and nothing inside it is listed or renamed. Verify never looks inside it.


## 3. Mapping from the old layout to the new one

~/Documents:

    00 Inbox                            001 Inbox, then every file inside gets filed like any other
    00 Inbox dated Verified Duplicates  006 Trash/001 Duplicates
    01 Personal                         002 Personal, subfolders renumbered from content
    01 Personal/02 Plan and Goals       002 Personal/006 Career, one whole row, description Plan and Goals with Jobs Tracker. It holds the job tracker and the two generator scripts that job-matches-daily runs, so it stays one unit
    02 Work/01 Bukrah Foundation        003 Work/001 Bukrah Foundation, moved whole in step 0, inside untouched
    02 Work/02 Rahma Center             003 Work/007 Other Work/004 Rahma Center
    02 Work/03 VampireTools             003 Work/003 VampireTools
    02 Work/04 Safi                     003 Work/005 Safi Uncle
    02 Work/05 Dr Seema Stories         003 Work/002 Stories from Long Ago
    02 Work/06 5PIE and 02 Work/09 5PIE 003 Work/007 Other Work/005 5PIE
    02 Work/08 Huston Apartments        003 Work/004 Houston Apartments
    02 Work/09 Resistance X             003 Work/007 Other Work/001 Resistance X
    02 Work/Archived Work               empty, trash
    02 Work/Review and Trash            006 Trash, one whole row, action trash, description Review and Trash from Work
    03 Reference                        004 Reference
    04 Quick Share                      001 Inbox, for review, it was a staging area
    05 Backup                           004 Reference/008 Backups
    99 Archive                          004 Reference/009 Archive
    To Be Organized                     filed from content. "Bukrah - For Saturday Session" inside it goes whole to 003 Work/001 Bukrah Foundation/001 Organizer Intake
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
    Stories from Long Ago, SFLA Book 2 Sample 2 Generated, SFLA Book 2 Gemini Reference Images
                                        003 Work/002 Stories from Long Ago/004 Build, each one whole row, description from content
    Water Project Forms                 Bukrah water program forms if the content confirms it, then 003 Work/001 Bukrah Foundation/001 Organizer Intake as one whole row
    Orientations 08 2026                content decides
    Claude outputs                      the files inside are filed from content, context packs and registry backups are 004 Reference/008 Backups material
    Carrier tracking PDFs and Pirate Ship PDFs   shipping records, content names the company, VampireTools when they are customer shipments
    Timesheet earning statement         002 Personal/001 Finance, last 4 of the statement number only
    .webloc shortcuts and html symlinks  skip, they are shortcuts and not documents
    Every other loose file              filed from content

~/Downloads: every loose file is filed from content. Bukrah Foundation documents go to 003 Work/001 Bukrah Foundation/001 Organizer Intake. The Jamal Thobe El Ez folder goes whole to 003 Work/007 Other Work/006 Jamal Thobe El Ez. Installers and archives that were already extracted are trash.

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
    003 Bukrah Foundation Financial Report August 2026 08.31.2026.pdf
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

   The listing must show "Mac File Organizer 10.12.2026.py", "Plan Filler Workflow 10.12.2026.js", and this runbook. If the kit folder is missing:

       git clone -b claude/busy-darwin-7bdkts https://github.com/malamour88/bu.git ~/"Organizer Kit"

3. python3 runs. Confirmed 3.9.6 on 10.07.2026, with openpyxl 3.1.5 and pypdf installed. Nothing to install.
4. The file moving tasks are already paused. Confirm no lock folder is live:

       ls -la ~/Documents/"Nightly Organize Logs"/ | grep lock

   Do not run on a Saturday morning before the Bukrah session has finished.
5. Sources are decided: ~/Documents, ~/Desktop, ~/Downloads. Do not ask again.
6. Confirm every file is local. Zero placeholders were found on 10.07.2026, so this is a quick recheck:

       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -print
       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -exec brctl download {} +

   Wait until the find returns nothing. The scan flags any placeholder as needs download, and apply skips it.
7. Tell Mohammad in one line that the scan is starting and that open documents should be closed. Do not wait for an answer. A file edited after the scan gets its stamp refreshed at apply time, and the log notes it.


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
      --whole "$DOCS/design-log" --whole "$DOCS/tapmenu" --whole "$DOCS/thobeelez" \
      --whole "$DOCS/01 Personal/02 Plan and Goals"

The scan prints a line every 500 items. It stops with a clear error if a --whole folder does not exist. Drop that one flag and rerun. If it stops on a traceback, fix the cause in the script, note the fix in the report, and rerun with the same sources.

Outputs: Inventory MM.DD.YYYY.json and Plan MM.DD.YYYY.csv. The inventory holds a content snippet, Spotlight metadata, hash, size, dates, and flags for each item. The plan is the editable work list. Flags to act on: duplicate, installer, archive extracted, zero bytes, temp file, screenshot, empty folder, old structure, already organized, needs read, needs download, project folder, moved whole, bundle, symlink.

Step 2. Fill the plan. This is the session's main work. Expect several thousand rows. Three columns per row:

    action       move, trash, print, or skip
    new folder   the destination relative to the root, for example 002 Personal/001 Finance
    new name     the description only. The script adds code, company, stamp, and extension. A trash or print row with a blank description keeps the old file name as its description.

The work is fanned out in batches. Each batch is one file with 40 rows, their snippets, and their Spotlight metadata, so an agent reads one small file instead of the whole plan.

Step 2a. Cut the batches. Only rows without a destination are included, so this is safe to rerun after a partial merge:

    python3 "$ORG" batches "$WORK/Plan MM.DD.YYYY.csv" --out "$WORK"

This writes a folder Batches MM.DD.YYYY with Batch 001 MM.DD.YYYY.json and so on, a Batch Index CSV, and Batch List MM.DD.YYYY.json, which is the list of batch file paths.

Step 2b. Run the plan filler workflow. Read Batch List MM.DD.YYYY.json and pass its contents as args.batches:

    Workflow tool, scriptPath ~/Organizer Kit/Plan Filler Workflow 10.12.2026.js,
    args { "batches": [ ...the list... ], "runbook": "~/Organizer Kit/Mac File Organizer Runbook 10.12.2026.md", "verify": true }

One agent fills each batch and writes Batch NNN Answers MM.DD.YYYY.json next to it. A second agent per batch re reads every answer as a skeptic and fixes weak or unsafe ones in place. The workflow returns counts, the rows sent to Inbox, the files nobody could read, and the questions only a human can answer. Keep those for the report. If the Workflow tool is not available, run one Agent per batch file with the fill prompt from the script, then one skeptic Agent per batch with the verify prompt.

Step 2c. Merge the answers into the plan:

    python3 "$ORG" merge "$WORK/Plan MM.DD.YYYY.csv" --answers "$WORK/Batches MM.DD.YYYY"

Merge reports answers applied, unknown ids, bad actions, and the rows still to decide. If rows remain, run batches again. It writes a new dated batch folder with only the remaining rows. Run the workflow on that list and merge again. Repeat until merge reports zero rows still to decide.

How the agents decide, and how the session decides any row it handles itself:

    Read the snippet first. When a row is flagged needs read or the snippet is empty, open the file with the Read tool. PDFs and images are readable that way. For docx, rtf, and pages use textutil -convert txt -stdout "file".
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
    Loose Bukrah Foundation files go to 003 Work/001 Bukrah Foundation/001 Organizer Intake.
    If a file is unreadable or its purpose is unclear, send it to 001 Inbox with a short note. Never guess a name.
    Never leave a row blank. Blank means undecided and apply refuses to run.

Step 3. Check until clean.

    python3 "$ORG" check "$WORK/Plan MM.DD.YYYY.csv"

Fix every ERROR line. Warnings are allowed but read them. The check also rejects two rows that would land on the same destination name.

Step 4. Build the approval spreadsheet and hand it to Mohammad.

    python3 "$ORG" sheet "$WORK/Plan MM.DD.YYYY.csv"

This writes Plan MM.DD.YYYY.xlsx with the final composed names in the new name column, a dropdown on action, and a Rules tab. Send the file. Say in one line how many rows go to each main folder and how many go to trash, and list the questions the workflow returned. Wait for approval. Mohammad may edit action, new folder, and new name in the spreadsheet. Any edit is normalized again on apply, so a typed name without the stamp still comes out right. This is the only stop before apply.

Step 5. Apply, dry run first.

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK"

Read the preview. Then execute:

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK" --execute --prune-empty \
      --source "$DOCS" --source ~/Desktop --source ~/Downloads

The change log is written row by row while apply runs, so an interrupted run still has a complete undo record for every move it made. Trash and print rows run before move rows, so a slot they vacate is free for the file that takes it. A file whose name changes only in letter case is renamed in place. Moving keeps the modified date, so the stamp stays true. A destination name that already exists gets a run number before the stamp. A file identical to one already at its destination goes to 006 Trash/001 Duplicates instead. Empty source folders are removed, never the sources named with --source, never home folders, never iCloud Drive.

Step 6. Repoint the scheduled tasks right after apply, in the same sitting. Every task under ~/.claude/scheduled-tasks that names an old path needs the new path. Grep them:

    grep -rl "02 Work\|01 Personal\|00 Inbox\|To Be Organized\|Nightly Organize Logs\|Bukrah Scripts" ~/.claude/scheduled-tasks

On 10.07.2026 the hits were nightly-organize, bukrah-weekly-organize, bukrah-chase-statement-reminder, bukrah-monthly-donor-ledger, bukrah-compliance-check, safi-daily-plan-sync, job-matches-daily, personal-morning-briefing, personal-weekly-review, and weekly-progress-upkeep. Folders follow the mapping in section 3, above all "02 Work/08 Huston Apartments " with the trailing space, which becomes "003 Work/004 Houston Apartments", "02 Work/01 Bukrah Foundation", which becomes "003 Work/001 Bukrah Foundation", and "02 Work/04 Safi", which becomes "003 Work/005 Safi Uncle". A single file that was renamed has its new path in the change log:

    grep -F "old path of the file" "$WORK/Change Log MM.DD.YYYY HHMM.csv"

Do this for safi-uncle-daily-plan.html, PERSONAL-PLAYBOOK.md, and every other file a prompt names. safi-daily-plan-sync runs every morning, so it must be repointed before the next 6:32 AM.

Step 7. Move Bukrah Scripts whole, now that the routines point at the new path:

    mv "$DOCS/Bukrah Scripts" "$DOCS/003 Work/001 Bukrah Foundation/Bukrah Scripts"

Repoint bukrah-archive-monthly-run, archive-upload-check, and any script that names ~/Documents/Bukrah Scripts. Then re enable bukrah-weekly-organize so the Saturday session runs again. Leave nightly-organize off.

Step 8. Verify.

    python3 "$ORG" verify --root "$DOCS" --out "$WORK" \
      --exclude "$DOCS/003 Work/001 Bukrah Foundation" --exclude "$DOCS/Claude" --exclude "$DOCS/OneDrive"

Zero problems is the target. Verify also lists any skeleton folder that is missing, which init creates. Fix any naming violation by editing the plan row and applying again, or by a direct rename that follows the rule.

Step 9. Report to Mohammad in a few lines: counts per main folder, how many went to trash, how many sit in 001 Inbox for his eyes, the change log path, and the undo command. The undo command is:

    python3 "$ORG" undo "$WORK/Change Log MM.DD.YYYY HHMM.csv" --execute

Step 10. Leftover old folders. After a clean verify, the old numbered folders such as "00 Inbox", "01 Personal", "02 Work" should be empty and removed by prune. If any survive, list what is still inside and ask.

Step 11. Propose to Mohammad whether the nightly organizer keeps running, repointed to file new files into 001 Inbox with this naming rule, or is retired. Do not turn it back on before he answers. Then propose the iCloud Drive root as the second pass.


## 7. Privacy

The working folder holds private names, last 4 digits, and content snippets. It stays on the Mac. The .gitignore in this kit blocks those files, the batch files, and the answer files from being committed. Never push the working folder, never paste full account numbers into a name, and never put the home address in a name. The contents of the old 08 Sensitive folder are never described in the chat, only filed. The workflow agents return counts and row ids, never file contents.


## 8. Command reference

    init     --root DIR
    scan     FOLDER... --out DIR [--exclude DIR] [--whole DIR] [--no-spotlight]
    batches  PLAN [--inventory FILE] [--out DIR] [--size N]
    merge    PLAN --answers DIR_OR_FILE [--out FILE]
    check    PLAN
    sheet    PLAN [--out FILE] [--to-csv]
    apply    PLAN --root DIR --out DIR [--execute] [--prune-empty] [--source DIR] [--allow-undecided] [--show N]
    verify   --root DIR --out DIR [--exclude DIR] [--show N]
    undo     LOG [--execute]

PLAN is the CSV or the xlsx, except merge, which writes the CSV. --exclude and --whole repeat. A --whole folder must sit inside a scanned folder and is listed as one unit. Every command is safe to rerun. apply and undo move nothing without --execute.
