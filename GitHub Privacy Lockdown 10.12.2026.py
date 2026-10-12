#!/usr/bin/env python3
"""
GitHub Privacy Lockdown                                        Date: 10.12.2026
Owner: Mohammad Alamour

Finds every public repository you own and switches it to private.

Requirements
    Python 3.8 or newer. Standard library only, nothing to install.
    A personal access token in the GITHUB_TOKEN environment variable.
        Fine grained token: Repository permissions "Administration: Read and write"
        on all repositories you own. "Metadata: Read only" is added automatically.
        Classic token: the "repo" scope.

Usage
    export GITHUB_TOKEN=github_pat_xxx          (macOS or Linux)
    python3 "GitHub Privacy Lockdown 10.12.2026.py"            preview only
    python3 "GitHub Privacy Lockdown 10.12.2026.py" --apply    make the change
    python3 "GitHub Privacy Lockdown 10.12.2026.py" --verify   confirm zero public repos

Safety
    The default run is a dry run. Nothing changes until you pass --apply.
    Every change is written to "GitHub Privacy Change Log MM.DD.YYYY.csv" next to
    this script so you can reverse any single repository later.
"""

import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
API_VERSION = "2022-11-28"


def token() -> str:
    value = os.environ.get("GITHUB_TOKEN", "").strip()
    if not value:
        sys.exit("GITHUB_TOKEN is not set. Export your personal access token first.")
    return value


def request(method: str, path: str, body: dict | None = None) -> tuple[int, dict | list, dict]:
    url = path if path.startswith("http") else API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token())
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", API_VERSION)
    req.add_header("User-Agent", "github-privacy-lockdown")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            parsed = json.loads(payload) if payload else {}
            return resp.status, parsed, dict(resp.headers)
    except urllib.error.HTTPError as err:
        payload = err.read()
        try:
            parsed = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            parsed = {"raw": payload.decode(errors="replace")}
        return err.code, parsed, dict(err.headers)


def who_am_i() -> dict:
    status, user, _ = request("GET", "/user")
    if status != 200:
        sys.exit(f"Token check failed ({status}): {user.get('message', user)}")
    return user


def owned_public_repos() -> list[dict]:
    """Walk every page of /user/repos and keep only public repos you own."""
    repos: list[dict] = []
    url = API + "/user/repos?" + urllib.parse.urlencode(
        {"visibility": "public", "affiliation": "owner", "per_page": 100}
    )
    while url:
        status, page, headers = request("GET", url)
        if status != 200:
            sys.exit(f"Could not list repositories ({status}): {page.get('message', page)}")
        repos.extend(r for r in page if not r.get("private"))
        url = next_link(headers.get("Link", ""))
    return sorted(repos, key=lambda r: r["full_name"].lower())


def next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        section = part.split(";")
        if len(section) == 2 and 'rel="next"' in section[1]:
            return section[0].strip().strip("<>")
    return None


def make_private(full_name: str) -> tuple[bool, str]:
    status, body, _ = request("PATCH", f"/repos/{full_name}", {"private": True})
    if status == 200 and body.get("private") is True:
        return True, "now private"
    return False, f"HTTP {status}: {body.get('message', body)}"


def log_path() -> str:
    stamp = dt.date.today().strftime("%m.%d.%Y")
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, f"GitHub Privacy Change Log {stamp}.csv")


def write_log(rows: list[dict]) -> str:
    path = log_path()
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "repository", "before", "after", "result"])
        if new_file:
            writer.writeheader()
        writer.writerows(rows)
    return path


def verify(user: dict) -> int:
    remaining = owned_public_repos()
    if not remaining:
        print(f"Verified: {user['login']} owns zero public repositories.")
        return 0
    print(f"Still public ({len(remaining)}):")
    for repo in remaining:
        print(f"    {repo['full_name']}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Make every public repository you own private.")
    parser.add_argument("--apply", action="store_true", help="perform the change (default is a dry run)")
    parser.add_argument("--verify", action="store_true", help="only check that no public repositories remain")
    args = parser.parse_args()

    user = who_am_i()
    print(f"Signed in as {user['login']}. Public repositories reported by GitHub: {user.get('public_repos', '?')}")

    if args.verify:
        return verify(user)

    repos = owned_public_repos()
    if not repos:
        print("Nothing to do. You own no public repositories.")
        return 0

    print(f"\n{len(repos)} public repositor{'y' if len(repos) == 1 else 'ies'} owned by {user['login']}:")
    for repo in repos:
        flags = []
        if repo.get("fork"):
            flags.append("fork")
        if repo.get("has_pages"):
            flags.append("GitHub Pages will be unpublished")
        if repo.get("stargazers_count"):
            flags.append(f"{repo['stargazers_count']} stars will be lost")
        if repo.get("forks_count"):
            flags.append(f"{repo['forks_count']} forks will be detached")
        note = f"  [{', '.join(flags)}]" if flags else ""
        print(f"    {repo['full_name']}{note}")

    if not args.apply:
        print("\nDry run. Re-run with --apply to make these private.")
        return 0

    print("\nApplying...")
    rows = []
    failures = 0
    for repo in repos:
        ok, message = make_private(repo["full_name"])
        failures += 0 if ok else 1
        print(f"    {repo['full_name']}: {message}")
        rows.append({
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "repository": repo["full_name"],
            "before": "public",
            "after": "private" if ok else "public",
            "result": message,
        })
    path = write_log(rows)
    print(f"\nChange log: {path}")

    print()
    verify_code = verify(user)
    return 1 if failures or verify_code else 0


if __name__ == "__main__":
    sys.exit(main())
