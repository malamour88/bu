<div align="right">11.11.2026</div>

# Universal File Organizer Install Guide

Owner: Mohammad Alamour
Time needed: about 10 minutes, once. After that, both organizers run every day with no prompts.

The kit:

| File | What it does |
|------|--------------|
| Organizer Rules 11.11.2026.json | The one rule book: folders 001 to 006, the seven companies, keywords, and the naming rule |
| Drive Organizer 11.11.2026.gs | Organizes Google Drive every day at 6 AM inside your Google account |
| Mac Organizer 11.11.2026.py | Organizes the Mac every day at 6:37 AM |
| Build And Test 11.11.2026.py | Copies rule changes into the Drive script and tests both scripts |
| Archive 10.12.2026 | The old Mac File Organizer kit, kept for reference |


## 1. What runs every day

Both organizers follow the same rules, so Drive and the Mac stay identical.

1. Every loose file goes to its home. A keyword in the name decides the folder. Hartford, Kimball, STAFDA, and BOP go to VampireTools. Skyline, Synology, and Qureshey go to Safi Uncle. GMAT and Stanford go to 002 Personal/004 School. The full list is in the rules file.
2. A file that matches no keyword goes to 001 Inbox with its name unchanged.
3. Filed files get a name that follows the rule: code, company, description, date. Example: Hartford_Quote_Comparison_08_06_2026.pdf becomes 003 VampireTools Hartford Quote Comparison 08.06.2026.pdf. No dashes, no underscores, and no street addresses. Identity and medical files get CONFIDENTIAL in the name.
4. Exact duplicates go to the trash. A duplicate means the same content, checked by fingerprint, not just the same name. Drive trash keeps them 30 days. The Mac Trash keeps them until you empty it.
5. Every change is logged, and one command undoes a whole run.

What never moves or gets renamed:

1. Anything inside a folder with Bukrah, Claude, or OneDrive in its name. The Bukrah routines keep working.
2. Code projects such as thobeelez and tapmenu, and the keep list in the rules file.
3. Files changed in the last 15 minutes, and downloads still in progress.
4. Files that live only in iCloud and are not on the Mac. They are never downloaded or read.
5. The My Mac backup in Google Drive.


## 2. Google Drive setup, about 5 minutes

1. Open github.com/malamour88/bu, switch to the branch claude/busy-darwin-7bdkts, and open Drive Organizer 11.11.2026.gs. Click Raw, then select all and copy.
2. Open script.google.com and click New project. Click Untitled project at the top and name it Universal File Organizer.
3. Delete the sample code in Code.gs and paste the script.
4. In the left bar, click the + next to Services. Pick Google Drive API, keep version v3 and the identifier Drive, and click Add.
5. Click the gear icon, Project Settings, and set the time zone to (GMT-08:00) Pacific Time, Los Angeles.
6. Back in the editor, pick installDailyRun in the function menu at the top and click Run.
7. Google asks for access once. Click Review permissions, pick your account, click Advanced, click Go to Universal File Organizer, then Allow. Google shows this warning for every personal script. The script runs only in your account.

Done. The first run starts right away. The results land in a log sheet at 004 Reference/010 Organizer Logs/004 Organizer Log. A large Drive can need more than one six minute window. The script picks up again 10 minutes later on its own.

Other functions in the same menu:

| Function | Use |
|----------|-----|
| previewNow | Logs what a run would do and changes nothing |
| organizeNow | Runs now |
| undoLastRun | Reverses every change from the last run, including trashed duplicates |
| removeDailyRun | Turns the daily run off |


## 3. Mac setup, about 5 minutes

1. Open github.com/malamour88/bu, switch to the branch claude/busy-darwin-7bdkts, click Code, then Download ZIP. Open the ZIP in Downloads.
2. Open Terminal and paste these two lines:

       cd ~/Downloads/bu-claude-busy-darwin-7bdkts
       python3 "Mac Organizer 11.11.2026.py" install

3. macOS asks once whether Terminal may open Desktop, Documents, and Downloads. Click Allow each time.
4. The installer prints one path. Open System Settings, Privacy and Security, Full Disk Access, and click +. Press Command Shift G, paste that path, press Return, and click Open. This lets the 6:37 AM run reach your folders while you are away.

Done. The first run starts right away and a notification shows the result. The first run is the largest. It merges the old 00 to 99 folders in Documents into 001 to 006 and can take several minutes.

How the old Documents folders merge:

| Old folder | New home |
|------------|----------|
| 00 Inbox, 04 Quick Share, To Be Organized | 001 Inbox |
| 01 Personal | 002 Personal, with matching subfolders merged, for example 01 Career into 003 Career |
| 02 Work | 003 Work, with companies merged, for example Vampire Tools into 003 VampireTools |
| 03 Reference | 004 Reference |
| 05 Backup | 004 Reference/008 Backups |
| 99 Archive | 004 Reference/009 Archive |
| To Be Printed | 005 To Be Printed |
| To Trash, Duplicates | 006 Trash |

Bukrah Foundation stays exactly where it is inside 02 Work, so its scheduled tasks keep their paths. Bukrah Scripts, Claude, OneDrive, and the code projects stay at the top of Documents.

Mac commands, run in Terminal:

    ORG="$HOME/Library/Application Support/Universal File Organizer/Mac Organizer 11.11.2026.py"
    python3 "$ORG" run --preview      # list the changes in a CSV on the Desktop, change nothing
    python3 "$ORG" run                # organize now
    python3 "$ORG" status             # schedule and last run
    python3 "$ORG" undo "<log file>"  # reverse one run, logs are in 004 Reference/010 Organizer Logs
    python3 "$ORG" uninstall          # stop the daily run


## 4. Changing the rules

1. Edit Organizer Rules 11.11.2026.json. Add a keyword to a company, add a folder to the keep list, or add a street name to blocked_words.
2. Run python3 "Build And Test 11.11.2026.py". It copies the rules into the Drive script and runs every test.
3. Paste the new Drive script into Apps Script again, and run the Mac install command again.


## 5. Tested on 11.11.2026

The build and test script passes every check:

1. The Mac and Drive scripts give the same name on 15 real file names from your Drive. Running a name through twice does not change it.
2. On a fake Mac home folder: files are filed and renamed, the old folders merge, duplicates go to the Trash, Bukrah, Claude, and code repos stay put, a second run changes nothing, and undo restores everything.
3. On a fake Google Drive: the root ends with only the six folders and the protected Bukrah folders, duplicates are trashed in favor of the Bukrah copy, a second run changes nothing, and undo restores everything.
