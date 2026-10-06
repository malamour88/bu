# Mac File Organizer Runbook

Date: 10.06.2026
Owner: Mohammad Alamour
For: the Claude Code session running on the Mac

This runbook turns the approved plan into action. Read all of it before running anything.
The organizer script is "Mac File Organizer 10.06.2026.py" in this folder.


## 1. The approved rules

Six main folders, numbered 001 to 006, live in one root. The root is the Documents folder, which syncs with iCloud when Desktop and Documents sync is on.

    001 Inbox             new and unsorted files, kept empty after each pass
    002 Personal          identity, family, home, health, personal finance
    003 Work              every company, one folder each
    004 Reference         manuals, templates, guides, saved articles
    005 To Be Printed     anything flagged for printing
    006 Trash             unwanted files, duplicates, installers, junk

Subfolders inside each main folder restart at 001 and use the same three digit style. Names come from the actual content. Examples:

    002 Personal
        001 Finance
        002 Health
        003 Home
        004 Identity
        005 Family
    004 Reference
        001 Manuals
        002 Templates
        003 Articles
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

Every company folder uses the same five inside folders:

    001 Admin and Legal          formation docs, licenses, agreements, insurance
    002 Finance                  bank statements, invoices, receipts, taxes
    003 Clients and Partners     contracts, proposals, correspondence
    004 Build                    product, design, code, plans, anything being made
    005 Marketing                brand, content, website, social

Files that span companies or belong to none go in 007 Other Work.


## 2. File naming rule

Pattern:

    [code] [company, Work only] [document type] [person or party] [last 4 of account, policy, VIN, or invoice number] [period] [MM.DD.YYYY].ext

The code is the three digit code of the main folder. The date stamp is the file's last modified date. The script adds the code, the company, the stamp, and the extension. The session supplies the description in the middle. Examples of finished names:

    002 Chase Checking Statement Mohammad Alamour 4821 March 2026 03.31.2026.pdf
    002 Amex Statement Mohammad Alamour 1005 April 2026 04.30.2026.pdf
    002 ConEd Electric Bill Account 5590 March 2026 03.20.2026.pdf
    002 Geico Auto Policy Mohammad Alamour Camry 7731 01.01.2026.pdf
    002 Quest Lab Results Mohammad Alamour 02.12.2026.pdf
    002 Federal Tax Return 2025 Mohammad Alamour 04.10.2026.pdf
    003 VampireTools Chase Business Checking Statement 2290 March 2026 03.31.2026.pdf
    003 Houston Apartments Lease Agreement Unit 4B Tenant Name 05.14.2025.pdf
    003 Bukrah Foundation IRS Determination Letter 09.02.2024.pdf
    004 Toyota Camry Owner Manual 2022 08.01.2023.pdf
    005 Boarding Pass Mohammad Alamour Houston to New York 10.02.2026.pdf
    006 Screenshot of Safari window 09.01.2026.png

Hard rules:

    No dashes and no underscores anywhere, in folder or file names.
    Spaces and dots only, plus letters and digits.
    Never the full account number, only the last 4 digits.
    Never the home address.
    The description names the person, the account or policy or invoice number, and the period, so nobody has to open the file to know what it is.
    A family member's statement carries that person's name.
    Project folders, app bundles, and Pages, Numbers, and Keynote packages move as one unit and get one name.
    Nothing is deleted. Trash means moved to 006 Trash, renamed with the same rule.


## 3. Preconditions on the Mac

1. Run this from a Claude Code session on the Mac itself: the Claude Desktop app, or `claude remote-control` in a terminal. A cloud session cannot reach the files.
2. Clone the kit outside the folders being organized:

       git clone https://github.com/malamour88/bu.git ~/"Organizer Kit"

3. Confirm python3 runs. If it is missing, run `xcode-select --install` and retry.
4. Optional for the .xlsx spreadsheet: `python3 -m pip install --user openpyxl`. Without it the plan stays a CSV, which Numbers and Excel also open.
5. iCloud. Ask the user to confirm that System Settings > Apple ID > iCloud > iCloud Drive > Desktop and Documents Folders is turned on. If it is on, the root is ~/Documents. If the user does not want it on, the root is ~/Library/Mobile Documents/com~apple~CloudDocs, which is iCloud Drive itself. Do not proceed until the root is confirmed.
6. Confirm the source folders. Default: ~/Documents, ~/Desktop, ~/Downloads. Ask once and use the answer.
7. Download iCloud placeholders so every file is local:

       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -print
       find ~/Documents ~/Desktop ~/Downloads -name "*.icloud" -exec brctl download {} \;

   Wait until the find returns nothing. The scan flags any placeholder as needs download, and apply skips it.
8. Ask the user to close open documents. A file edited after the scan gets its stamp refreshed at apply time, and the log notes it.


## 4. Step by step

Set this once in the shell:

    ORG=~/"Organizer Kit/Mac File Organizer 10.06.2026.py"
    WORK=~/"Organizer Working"

Step 1. Scan.

    python3 "$ORG" scan ~/Documents ~/Desktop ~/Downloads --out "$WORK"

Outputs: Inventory MM.DD.YYYY.json and Plan MM.DD.YYYY.csv. The inventory holds a content snippet, Spotlight metadata, hash, size, dates, and flags for each item. The plan is the editable work list. Flags to act on: duplicate, installer, archive extracted, zero bytes, temp file, screenshot, empty folder, old structure, already organized, needs read, needs download, project folder, bundle.

Step 2. Fill the plan. This is the session's main work. For each row set three columns:

    action       move, trash, print, or skip
    new folder   the destination relative to the root, for example 002 Personal/001 Finance
    new name     the description only. The script adds code, company, stamp, and extension.

How to decide:

    Read the snippet in the inventory first. When a row is flagged needs read, open the file with the Read tool. PDFs and images are readable that way. For docx and rtf use textutil -convert txt -stdout "file".
    Pull the identifiers into the description: who, which account or policy or invoice, which period.
    Rows flagged duplicate, installer, zero bytes, temp file, archive extracted, or empty folder are prefilled as trash. Keep that unless the content says otherwise.
    Screenshots: trash unless the image holds something worth keeping, then move it where it belongs with a description of what it shows.
    Rows flagged already organized are prefilled as skip. Leave them.
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

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root ~/Documents --out "$WORK"

Read the preview. Then execute:

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root ~/Documents --out "$WORK" --execute --prune-empty --source ~/Documents --source ~/Desktop --source ~/Downloads

The change log lands in the working folder. Moving keeps the modified date, so the stamp stays true. A destination name that already exists gets a run number before the stamp. A file identical to one already at its destination goes to 006 Trash/001 Duplicates instead. Empty source folders are removed, never the sources named with --source, never home folders, never iCloud Drive.

Step 6. Verify.

    python3 "$ORG" verify --root ~/Documents --out "$WORK"

Zero problems is the target. Fix any violation by editing the plan row and applying again, or by a direct rename that follows the rule.

Step 7. Report to the user in a few lines: counts per main folder, how many went to trash, the change log path, and the undo command. The undo command is:

    python3 "$ORG" undo "$WORK/Change Log MM.DD.YYYY HHMM.csv" --execute

Step 8. Leftover old folders. After a clean verify, the old numbered folders such as "001 inbox" or "002 work" should be empty and removed by prune. If any survive, list what is still inside and ask.


## 5. Privacy

The working folder holds private names, last 4 digits, and content snippets. It stays on the Mac. The .gitignore in this kit blocks those files from being committed. Never push the working folder, never paste full account numbers into a name, and never put the home address in a name.


## 6. Command reference

    scan   FOLDER... --out DIR [--exclude DIR] [--no-spotlight]
    check  PLAN
    sheet  PLAN [--out FILE] [--to-csv]
    apply  PLAN --root DIR --out DIR [--execute] [--prune-empty] [--source DIR] [--allow-undecided] [--show N]
    verify --root DIR --out DIR [--show N]
    undo   LOG [--execute]

PLAN is the CSV or the xlsx. Every command is safe to rerun. apply and undo move nothing without --execute.
