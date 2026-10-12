<div align="right">10.12.2026</div>

# Mac Desktop Pass Runbook

Date: 10.12.2026
Owner: Mohammad Alamour
For: the Claude Code session running in the Claude Desktop app on the Mac

Goal: the Desktop shows only the folders in the keep list, plus one Shortcuts folder. Everything else is filed into ~/Documents by the rules in "Mac File Organizer Runbook 10.06.2026.md". Read that runbook first. This one only adds the Desktop specifics.


## 1. Find out what already ran

Nothing moves in this section.

    ls -la ~/"Organizer Working" 2>/dev/null
    ls ~/"Organizer Working"/"Change Log"* 2>/dev/null
    ls ~/"Organizer Working"/"Verify Report"* 2>/dev/null
    ls ~/Documents

Read the result:

    No Organizer Working folder, or no Change Log in it: the organizer never applied. Run the full 10.06 runbook, with the Desktop rules below folded into step 2.
    A Change Log exists and ~/Documents shows the 00x numbered folders: apply ran. Continue with this runbook for the Desktop only.
    A Plan CSV or XLSX but no Change Log: scan ran, apply did not. Reuse the plan if it is less than a week old, else rescan.

Then check whether the nightly tasks are refilling the Desktop:

    ls ~/.claude/scheduled-tasks
    ls -d ~/Documents/"Nightly Organize Logs"/*lock* ~/Documents/"004 Reference/009 Archive/001 Nightly Organizer Logs"/*lock* 2>/dev/null
    ls -lt ~/Desktop | head -20

If the newest Desktop items are younger than the last apply, something is still writing there. Pause every file moving task named in section 5 of the 10.06 runbook before going on.


## 2. Inventory the Desktop and settle the keep list

    ls -la ~/Desktop
    find ~/Desktop -maxdepth 1 -name "*.icloud" -exec brctl download {} +

Show the user the top level list, one line per item with its kind: folder, file, screenshot, shortcut. The user names the folders that stay. Record them:

    KEEP=("Folder One" "Folder Two")

Anything not in KEEP is in scope.


## 3. Shortcuts first

Shortcuts are not documents, so they never enter the plan. Move them into one folder:

    mkdir -p ~/Desktop/Shortcuts
    find ~/Desktop -maxdepth 1 \( -name "*.webloc" -o -name "*.inetloc" -o -type l \) -exec mv -n {} ~/Desktop/Shortcuts/ \;
    find ~/Desktop -maxdepth 1 -name "*.html" -exec sh -c 'grep -qil "refresh\|window.location" "$1" && mv -n "$1" ~/Desktop/Shortcuts/' _ {} \;

Finder aliases are files with the alias flag. List them and move the ones the user confirms:

    mdfind -onlyin ~/Desktop "kMDItemKind == 'Alias'"


## 4. Scan the Desktop only

    ORG=~/"Organizer Kit/Mac File Organizer 10.06.2026.py"
    WORK=~/"Organizer Working"
    DOCS=~/Documents
    EXCL=(); for k in "${KEEP[@]}"; do EXCL+=(--exclude ~/Desktop/"$k"); done
    python3 "$ORG" scan ~/Desktop --out "$WORK" --exclude ~/Desktop/Shortcuts "${EXCL[@]}"

If ~/Documents has no 00x skeleton yet, run init first as in the 10.06 runbook step 0.


## 5. Fill the plan, Desktop rules

Follow step 2 of the 10.06 runbook, with these Desktop specifics:

    Screenshots (names starting Screenshot or Screen Recording, or flagged screenshot): trash, unless the image shows something to keep. Then move it with a description of what it shows.
    Loose documents: file by content into the matching company or personal folder. The Desktop gives no folder hint, so read the snippet for every row.
    Project folders: move whole into the matching company, named by what they are. A folder with mixed content is a project folder when it has its own structure, else its files are filed one by one.
    Installers, zips already extracted, zero byte files: trash.
    Anything unclear: 001 Inbox with a note. Never guess.
    Rows for items inside KEEP folders or Shortcuts should not exist. If one appears, the exclude was wrong. Fix the scan, do not skip the row.

Then check, sheet, and wait for approval exactly as steps 3 and 4 of the 10.06 runbook. Say in one line how many rows go to each main folder and to trash.


## 6. Apply

Dry run, read the preview, then execute with the Desktop as the only source:

    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK"
    python3 "$ORG" apply "$WORK/Plan MM.DD.YYYY.xlsx" --root "$DOCS" --out "$WORK" --execute --prune-empty --source ~/Desktop

Undo, if needed:

    python3 "$ORG" undo "$WORK/Change Log MM.DD.YYYY HHMM.csv" --execute


## 7. Verify the Desktop

    ls -la ~/Desktop

Pass condition: only the KEEP folders, Shortcuts, and hidden system files (.DS_Store, .localized). Then run the full verify from step 7 of the 10.06 runbook so the filed items pass the naming rule.


## 8. Keep it clean

Report to the user: items filed per main folder, items trashed, shortcuts moved, change log path, undo command.

Then settle the refill question. Propose one of:

    Retire the nightly organizer tasks that write to the Desktop.
    Repoint them to file new Desktop files into 001 Inbox with the naming rule, and run them only after approval.

Do not turn a task back on before the user answers. macOS can also hide clutter without filing it: Finder, View, Use Stacks. That is a cosmetic option, not a replacement for this pass.
