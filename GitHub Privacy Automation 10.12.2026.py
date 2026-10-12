#!/usr/bin/env python3
"""
GitHub Privacy Automation                                      Date: 10.12.2026
Owner: Mohammad Alamour

One run makes the malamour88 GitHub account as private as GitHub allows.

What it does, in order
    1. API    Makes every public repository you own private.
    2. API    Sets your email visibility to private and finds your noreply address.
    3. API    Clears the public profile card (name, bio, company, location, website, X handle).
    4. Git    Points git on this Mac at the noreply address so new commits never carry your real email.
    5. Browser (your own signed in session, nothing stored by this script)
              Checks "Keep my email addresses private" and "Block command line pushes that expose my email".
              Unchecks "Private contributions" and "Activity overview" on your profile calendar.
              Unchecks "Show Achievements on my profile".
    6. Verifies everything it can through the API and prints a summary.

Token (fine grained, Resource owner malamour88, Repository access: All repositories)
    Repository permissions   Administration: Read and write      Metadata: Read only (automatic)
    Account permissions      Email addresses: Read and write      Profile: Read and write
    Classic alternative: scopes "repo" and "user".

Usage
    Double click "GitHub Privacy Automation 10.12.2026.command", or
    python3 "GitHub Privacy Automation 10.12.2026.py"                 full run, prompts for the token
    python3 "GitHub Privacy Automation 10.12.2026.py" --dry-run       shows what would change, changes nothing
    python3 "GitHub Privacy Automation 10.12.2026.py" --skip-browser  API and git steps only
    python3 "GitHub Privacy Automation 10.12.2026.py" --verify        read only report

Browser step
    The first run opens a Chromium window on github.com. Sign in there, with two factor, as you normally do.
    The window belongs to a profile folder under ~/Library/Application Support/GitHub Privacy Lockdown,
    so later runs are already signed in. Delete that folder to sign out.
    Screenshots of each settings page land in "GitHub Privacy Screenshots MM.DD.YYYY" next to this script.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import getpass
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
API_VERSION = "2022-11-28"
STAMP = dt.date.today().strftime("%m.%d.%Y")
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = ""


# ----------------------------------------------------------------------------- helpers

def say(line: str = "") -> None:
    print(line, flush=True)


def request(method: str, path: str, body: dict | None = None) -> tuple[int, dict | list, dict]:
    url = path if path.startswith("http") else API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", API_VERSION)
    req.add_header("User-Agent", "github-privacy-automation")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            return resp.status, (json.loads(payload) if payload else {}), dict(resp.headers)
    except urllib.error.HTTPError as err:
        payload = err.read()
        try:
            parsed = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            parsed = {"raw": payload.decode(errors="replace")}
        return err.code, parsed, dict(err.headers)


def message(body) -> str:
    return body.get("message", str(body)) if isinstance(body, dict) else str(body)


def next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        section = part.split(";")
        if len(section) == 2 and 'rel="next"' in section[1]:
            return section[0].strip().strip("<>")
    return None


def paged(path: str, params: dict) -> list:
    items: list = []
    url = API + path + "?" + urllib.parse.urlencode(params)
    while url:
        status, page, headers = request("GET", url)
        if status != 200:
            sys.exit(f"GET {path} failed ({status}): {message(page)}")
        items.extend(page)
        url = next_link(headers.get("Link", ""))
    return items


def log_rows(rows: list[dict]) -> str:
    path = os.path.join(HERE, f"GitHub Privacy Change Log {STAMP}.csv")
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "item", "before", "after", "result"])
        if new_file:
            writer.writeheader()
        writer.writerows(rows)
    return path


def row(item: str, before: str, after: str, result: str) -> dict:
    return {"timestamp": dt.datetime.now().isoformat(timespec="seconds"), "item": item,
            "before": before, "after": after, "result": result}


# ----------------------------------------------------------------------------- step 1 repositories

def owned_public_repos() -> list[dict]:
    repos = paged("/user/repos", {"visibility": "public", "affiliation": "owner", "per_page": 100})
    return sorted((r for r in repos if not r.get("private")), key=lambda r: r["full_name"].lower())


def step_repositories(apply: bool, rows: list[dict]) -> None:
    say("Step 1  Repositories")
    repos = owned_public_repos()
    if not repos:
        say("    You own no public repositories.")
        return
    for repo in repos:
        notes = []
        if repo.get("fork"):
            notes.append("fork")
        if repo.get("has_pages"):
            notes.append("Pages site will be unpublished")
        if repo.get("stargazers_count"):
            notes.append(f"{repo['stargazers_count']} stars will be lost")
        if repo.get("forks_count"):
            notes.append(f"{repo['forks_count']} forks will be detached")
        say(f"    {repo['full_name']}" + (f"  [{', '.join(notes)}]" if notes else ""))
        if not apply:
            continue
        status, body, _ = request("PATCH", f"/repos/{repo['full_name']}", {"private": True})
        ok = status == 200 and body.get("private") is True
        result = "now private" if ok else f"HTTP {status}: {message(body)}"
        say(f"        {result}")
        rows.append(row(repo["full_name"], "public", "private" if ok else "public", result))


# ----------------------------------------------------------------------------- step 2 email

def emails() -> list[dict]:
    status, body, _ = request("GET", "/user/emails")
    if status != 200:
        sys.exit(f"Could not read email addresses ({status}): {message(body)}. "
                 "The token needs Account permission Email addresses: Read and write.")
    return body


def noreply_address(login: str) -> str | None:
    for entry in emails():
        if entry["email"].endswith("@users.noreply.github.com"):
            return entry["email"]
    return None


def step_email(apply: bool, login: str, rows: list[dict]) -> str | None:
    say("Step 2  Email visibility")
    current = emails()
    primary = next((e for e in current if e.get("primary")), None)
    visibility = primary.get("visibility") if primary else None
    say(f"    Primary email visibility now: {visibility or 'unknown'}")
    if apply and visibility != "private":
        status, body, _ = request("PATCH", "/user/email/visibility", {"visibility": "private"})
        ok = status == 200
        result = "set to private" if ok else f"HTTP {status}: {message(body)}"
        say(f"        {result}")
        rows.append(row("primary email visibility", visibility or "unknown", "private" if ok else visibility or "unknown", result))
    noreply = noreply_address(login)
    if noreply:
        say(f"    Noreply address: {noreply}")
    else:
        say("    Noreply address not listed yet. GitHub creates it once email privacy is on. The browser step handles that.")
    return noreply


# ----------------------------------------------------------------------------- step 3 profile card

PROFILE_FIELDS = ("name", "bio", "company", "location", "blog", "twitter_username")


def step_profile(apply: bool, user: dict, rows: list[dict]) -> None:
    say("Step 3  Profile card")
    filled = {f: user.get(f) for f in PROFILE_FIELDS if user.get(f)}
    if not filled:
        say("    Already blank.")
        return
    for field, value in filled.items():
        say(f"    {field}: {value}")
    if not apply:
        return
    payload = {f: "" for f in PROFILE_FIELDS}
    payload["hireable"] = False
    status, body, _ = request("PATCH", "/user", payload)
    ok = status == 200
    result = "cleared" if ok else f"HTTP {status}: {message(body)}"
    say(f"        {result}")
    for field, value in filled.items():
        rows.append(row(f"profile {field}", str(value), "" if ok else str(value), result))


# ----------------------------------------------------------------------------- step 4 git config

def git(*args: str) -> str:
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    return done.stdout.strip()


def step_git(apply: bool, login: str, noreply: str | None, rows: list[dict]) -> None:
    say("Step 4  Git identity on this Mac")
    before = git("config", "--global", "--get", "user.email")
    say(f"    git user.email now: {before or '(not set)'}")
    if not noreply:
        say("    Skipped. Re-run after the browser step so the noreply address exists.")
        return
    if before == noreply:
        say("    Already set to the noreply address.")
        return
    if not apply:
        say(f"    Would set user.email to {noreply}")
        return
    subprocess.run(["git", "config", "--global", "user.email", noreply], check=True)
    if not git("config", "--global", "--get", "user.name"):
        subprocess.run(["git", "config", "--global", "user.name", login], check=True)
    say(f"        set to {noreply}")
    rows.append(row("git global user.email", before or "(not set)", noreply, "set"))


# ----------------------------------------------------------------------------- step 5 browser

def profile_dir() -> str:
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.path.expanduser("~/.local/share")
    path = os.path.join(base, "GitHub Privacy Lockdown")
    os.makedirs(path, exist_ok=True)
    return path


def step_browser(apply: bool, login: str, rows: list[dict]) -> None:
    say("Step 5  Browser settings (your own signed in session)")
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        say("    Playwright is not installed. Run the .command file, or: pip3 install playwright && playwright install chromium")
        return

    shots = os.path.join(HERE, f"GitHub Privacy Screenshots {STAMP}")
    os.makedirs(shots, exist_ok=True)

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(profile_dir(), headless=False, viewport={"width": 1280, "height": 900})
        page = context.pages[0] if context.pages else context.new_page()

        # Sign in. The script never sees the password. It only waits for GitHub to show your login name.
        page.goto("https://github.com/login", wait_until="domcontentloaded")
        say("    If a sign in page is open, sign in now (two factor included). Waiting up to 10 minutes...")
        deadline = time.time() + 600
        while time.time() < deadline:
            meta = page.locator('meta[name="user-login"]').first
            try:
                if meta.count() and meta.get_attribute("content") == login:
                    break
            except Exception:
                pass
            time.sleep(2)
        else:
            say("    Not signed in after 10 minutes. Browser step skipped.")
            context.close()
            return
        say(f"    Signed in as {login}.")

        def checkbox(label: str, want_checked: bool, submit_button: str | None, url: str, item: str) -> None:
            page.goto(url, wait_until="domcontentloaded")
            box = page.get_by_label(label, exact=False).first
            try:
                box.wait_for(timeout=15000)
            except PWTimeout:
                say(f"    Could not find \"{label}\" on {url}. Set it by hand.")
                rows.append(row(item, "unknown", "unknown", "control not found"))
                return
            before = box.is_checked()
            say(f"    {label}: {'on' if before else 'off'}")
            if before == want_checked:
                return
            if apply:
                box.set_checked(want_checked)
                if submit_button:
                    page.get_by_role("button", name=submit_button).first.click()
                page.wait_for_load_state("networkidle")
                page.goto(url, wait_until="domcontentloaded")
                after = page.get_by_label(label, exact=False).first.is_checked()
                say(f"        now {'on' if after else 'off'}")
                rows.append(row(item, "on" if before else "off", "on" if after else "off", "changed" if after == want_checked else "did not stick"))
            else:
                say(f"        would turn {'on' if want_checked else 'off'}")
            page.screenshot(path=os.path.join(shots, f"{item}.png"), full_page=True)

        checkbox("Keep my email addresses private", True, None, "https://github.com/settings/emails", "keep email private")
        checkbox("Block command line pushes that expose my email", True, None, "https://github.com/settings/emails", "block exposing pushes")
        checkbox("Show Achievements on my profile", False, "Update preferences", "https://github.com/settings/profile", "show achievements")

        # Contribution settings menu above the calendar. Each entry is a menu item with aria-checked.
        page.goto(f"https://github.com/{login}", wait_until="domcontentloaded")
        for label, item in (("Private contributions", "private contributions"), ("Activity overview", "activity overview")):
            try:
                page.get_by_text("Contribution settings", exact=False).first.click(timeout=15000)
                entry = page.get_by_role("menuitemcheckbox", name=label).first
                entry.wait_for(timeout=10000)
            except PWTimeout:
                say(f"    Could not open Contribution settings / \"{label}\". Set it by hand.")
                rows.append(row(item, "unknown", "unknown", "control not found"))
                continue
            before = (entry.get_attribute("aria-checked") or "").lower() == "true"
            say(f"    {label}: {'on' if before else 'off'}")
            if before and apply:
                entry.click()
                page.wait_for_load_state("networkidle")
                page.goto(f"https://github.com/{login}", wait_until="domcontentloaded")
                page.get_by_text("Contribution settings", exact=False).first.click()
                after = (page.get_by_role("menuitemcheckbox", name=label).first.get_attribute("aria-checked") or "").lower() == "true"
                say(f"        now {'on' if after else 'off'}")
                rows.append(row(item, "on", "on" if after else "off", "changed" if not after else "did not stick"))
            elif before:
                say("        would turn off")
            page.keyboard.press("Escape")
        page.screenshot(path=os.path.join(shots, "profile.png"), full_page=True)
        context.close()
    say(f"    Screenshots: {shots}")


# ----------------------------------------------------------------------------- step 6 verify

def step_verify(login: str) -> int:
    say("Step 6  Verification")
    problems = 0
    left = owned_public_repos()
    if left:
        problems += 1
        say(f"    Still public: {', '.join(r['full_name'] for r in left)}")
    else:
        say("    Public repositories: 0")
    primary = next((e for e in emails() if e.get("primary")), None)
    vis = primary.get("visibility") if primary else "unknown"
    say(f"    Primary email visibility: {vis}")
    problems += 0 if vis == "private" else 1
    status, user, _ = request("GET", "/user")
    filled = [f for f in PROFILE_FIELDS if user.get(f)]
    say(f"    Profile fields still filled: {', '.join(filled) if filled else 'none'}")
    problems += 1 if filled else 0
    email = git("config", "--global", "--get", "user.email")
    say(f"    Git email: {email or '(not set)'}")
    problems += 0 if email.endswith("@users.noreply.github.com") else 1
    say("    Browser settings: see the screenshots folder and the change log.")
    return problems


# ----------------------------------------------------------------------------- main

def main() -> int:
    global TOKEN
    parser = argparse.ArgumentParser(description="Make a GitHub account as private as GitHub allows.")
    parser.add_argument("--dry-run", action="store_true", help="show what would change, change nothing")
    parser.add_argument("--skip-browser", action="store_true", help="API and git steps only")
    parser.add_argument("--verify", action="store_true", help="read only report")
    args = parser.parse_args()

    TOKEN = os.environ.get("GITHUB_TOKEN", "").strip() or getpass.getpass("Paste your GitHub token (hidden): ").strip()
    if not TOKEN:
        sys.exit("No token given.")

    status, user, _ = request("GET", "/user")
    if status != 200:
        sys.exit(f"Token check failed ({status}): {message(user)}")
    login = user["login"]
    apply = not (args.dry_run or args.verify)
    say(f"Signed in as {login}. Mode: {'verify' if args.verify else 'dry run' if args.dry_run else 'apply'}")
    say()

    if args.verify:
        return 1 if step_verify(login) else 0

    rows: list[dict] = []
    step_repositories(apply, rows)
    say()
    noreply = step_email(apply, login, rows)
    say()
    step_profile(apply, user, rows)
    say()
    step_git(apply, login, noreply, rows)
    say()
    if not args.skip_browser:
        step_browser(apply, login, rows)
        say()
        if apply and not noreply:
            noreply = noreply_address(login)
            if noreply:
                step_git(apply, login, noreply, rows)
                say()
    if rows:
        say(f"Change log: {log_rows(rows)}")
        say()
    if apply:
        problems = step_verify(login)
        say()
        say("Done." if not problems else f"Done with {problems} item(s) to check above.")
        return 1 if problems else 0
    say("Dry run complete. Run again without --dry-run to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
