<div align="right">10.12.2026</div>

# GitHub Privacy Lockdown Runbook

Date: 10.12.2026
Owner: Mohammad Alamour
For: the malamour88 GitHub account, run from your Mac

This runbook makes the account as private as GitHub allows. Three parts: the token, the repository script, and the account settings that only the web UI can change.
Scripts in this folder: "GitHub Privacy Lockdown 10.12.2026.py" and "GitHub Privacy Lockdown 10.12.2026.sh".


## 0. One command does all of it

Files: "GitHub Privacy Automation 10.12.2026.command" (runner) and "GitHub Privacy Automation 10.12.2026.py" (the work).

    1. Create the token in Section 1, with the two extra Account permissions listed there.
    2. In Finder, right click "GitHub Privacy Automation 10.12.2026.command", choose Open, then Open again.
       The first run installs Playwright and a private Chromium copy (about 2 minutes).
    3. Paste the token when asked. It is held in memory only and never written to disk.
    4. A Chromium window opens on github.com. Sign in with your usual two factor. The script waits.
    5. Read the summary. "Done." means every check passed.

What it changes, in order: all your public repositories to private, email visibility to private,
profile card cleared, git on this Mac set to your noreply address, then in your signed in browser
"Keep my email addresses private" on, "Block command line pushes that expose my email" on,
"Private contributions" off, "Activity overview" off, "Show Achievements on my profile" off.

Preview first:  ./"GitHub Privacy Automation 10.12.2026.command" --dry-run
Report only:    ./"GitHub Privacy Automation 10.12.2026.command" --verify
Without browser: add --skip-browser

The browser profile lives in ~/Library/Application Support/GitHub Privacy Lockdown. Delete that folder to sign it out.
Screenshots of each settings page land in "GitHub Privacy Screenshots 10.12.2026" next to the script. They stay off GitHub.

Still manual after the run: unstar repositories, unfollow accounts, make public gists secret, revoke old OAuth apps (Section 4).


## 1. Token permissions (PAT)

Create one token. Use it for the script, then delete it.

Fine grained token (recommended)

    GitHub, top right profile picture, Settings
    Left sidebar, bottom, Developer settings
    Personal access tokens, Fine-grained tokens, Generate new token
    Token name: Privacy Lockdown 10.12.2026
    Expiration: 7 days
    Resource owner: malamour88
    Repository access: All repositories
    Repository permissions:
        Administration: Read and write        (required to change visibility, PATCH /repos/{owner}/{repo})
        Metadata: Read-only                   (added automatically, required to list repositories)
    Account permissions (needed by the automation script only):
        Email addresses: Read and write       (sets email visibility, reads the noreply address)
        Profile: Read and write               (clears the public profile card)
    Generate token, copy it once.

Classic token (only if you cannot use fine grained)

    Developer settings, Personal access tokens, Tokens (classic), Generate new token (classic)
    Scopes: repo        (full control of private repositories, which includes changing visibility)
            user        (email visibility and profile card, automation script only)
    Nothing else.

Why this is enough: the script calls two endpoints only. GET /user/repos needs Metadata read. PATCH /repos/{owner}/{repo} with {"private": true} needs Administration write. No account level permission is needed.


## 2. Make every public repository private

Option A, Python (no install, handles forks and non forks together)

    export GITHUB_TOKEN=github_pat_xxxxxxxx
    cd "~/Documents/<folder with these scripts>"
    python3 "GitHub Privacy Lockdown 10.12.2026.py"              dry run, lists what would change
    python3 "GitHub Privacy Lockdown 10.12.2026.py" --apply      makes the change and verifies
    python3 "GitHub Privacy Lockdown 10.12.2026.py" --verify     confirms zero public repositories
    unset GITHUB_TOKEN

The apply run writes "GitHub Privacy Change Log 10.12.2026.csv" next to the script. That file lists every repository touched, so you can reverse one later. It is git ignored.

Option B, GitHub CLI

    brew install gh
    gh auth login                                  pick GitHub.com, HTTPS, paste the token
    bash "GitHub Privacy Lockdown 10.12.2026.sh"            dry run
    bash "GitHub Privacy Lockdown 10.12.2026.sh" --apply    makes the change and verifies

The single commands behind the script, if you prefer to run them by hand:

    gh repo list malamour88 --visibility public --limit 1000 --json nameWithOwner --jq '.[].nameWithOwner'
    gh repo edit malamour88/bu --visibility private --accept-visibility-change-consequences

What changes when a repository goes private

    Stars and watchers are removed and do not come back if you flip it public again.
    Public forks are detached into their own network. Anyone who forked keeps their copy.
    A GitHub Pages site on that repository is unpublished (Pages on private repos needs GitHub Pro).
    Anonymous clone links stop working. Collaborators you invited keep access.
    GitHub Actions minutes start counting against your free quota (2,000 minutes a month on Free).

Status as of 10.12.2026: the account owns one public repository, malamour88/bu. The Claude session that wrote this runbook could not flip it because the session proxy blocks repository settings writes. Run Option A or B locally.


## 3. Hide your email from future commits

Step 1, GitHub web UI

    Top right profile picture, Settings
    Left sidebar under Access, Emails
    Check "Keep my email addresses private"
        GitHub shows your noreply address under this box. It looks like
        12345678+malamour88@users.noreply.github.com
        Copy it.
    Check "Block command line pushes that expose my email"
        GitHub then rejects any push whose newest commit carries your real address.

Step 2, Git on your Mac (one time)

    git config --global user.email "12345678+malamour88@users.noreply.github.com"
    git config --global user.name "malamour88"
    git config --global --get user.email            confirm

If a repository has its own local email set, clear it:

    git config --unset user.email

Step 3, remove the public email from your profile card

    Settings, left sidebar under Access, Public profile
    Public email: leave it on "Select a verified email to display"
    Update profile

What this does not fix: commits already pushed with your real address stay in history. The next section covers that.


## 4. Make profile activity private

Private contributions and the activity graph

    Top right profile picture, Your profile
    Above the contribution calendar, click "Contribution settings"
    Uncheck "Private contributions"
        Your private repository activity no longer shows as anonymized green squares.
    In the same menu, uncheck "Activity overview" if it is on.

Achievements

    Settings, left sidebar under Access, Public profile
    Scroll to "Profile settings"
    Uncheck "Show Achievements on my profile"
    Update preferences

Profile card

    Settings, Public profile
    Clear Name, Bio, Pronouns, URL, Company, Location, Social accounts
    Set "Display current local time" off
    Update profile

Other places that leak activity (do these too)

    Settings, Public profile, uncheck "Include private contributions on my profile" if your UI shows the checkbox there instead of on the calendar menu. GitHub has moved this control between the two places.
    Settings, Code, planning, and automation, Packages: delete any public packages.
    Your profile, Stars tab: unstar anything you do not want shown. Stars are always public.
    Your profile, Followers and Following: unfollow accounts. Follows are always public.
    Gists at gist.github.com: public gists are searchable. Open each one, Edit, "Make secret", or delete it.
    Settings, Applications, Authorized OAuth Apps and Authorized GitHub Apps: revoke anything you no longer use.
    Settings, Password and authentication: turn on two factor authentication and remove old SSH keys you do not use.


## 5. Scrub your real email from past commits (optional, destructive)

Only do this if the history matters to you. It rewrites every commit hash, and anyone with a clone must re-clone.

    brew install git-filter-repo
    git clone --mirror https://github.com/malamour88/<repo>.git
    cd <repo>.git
    git filter-repo --mailmap <(printf 'malamour88 <12345678+malamour88@users.noreply.github.com> <your.real@email>\n')
    git push --force --mirror

Once the repository is private, the old addresses are only visible to you and your collaborators, so most people skip this step.


## 6. Verification checklist

    python3 "GitHub Privacy Lockdown 10.12.2026.py" --verify prints "owns zero public repositories".
    Open https://github.com/malamour88 in a private browser window while signed out. No repositories, no green calendar activity, no email, no achievements.
    git log -1 --format=%ae in any repository shows the users.noreply.github.com address.
    A test commit with your real address set locally is rejected on push with "Your push would publish a private email address".
    Delete the token: Settings, Developer settings, Personal access tokens, Delete.
