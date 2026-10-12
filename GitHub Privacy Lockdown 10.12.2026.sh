#!/usr/bin/env bash
# GitHub Privacy Lockdown (gh CLI version)                     Date: 10.12.2026
# Owner: Mohammad Alamour
#
# Same job as the Python script, done with the GitHub CLI.
# Requires: gh (https://cli.github.com) signed in with a token that has
#   fine grained "Administration: Read and write" on all your repositories,
#   or the classic "repo" scope.
#
# Usage:
#   bash "GitHub Privacy Lockdown 10.12.2026.sh"           preview only
#   bash "GitHub Privacy Lockdown 10.12.2026.sh" --apply   make the change

set -euo pipefail

APPLY="${1:-}"

echo "Checking sign in..."
gh auth status
LOGIN="$(gh api user --jq .login)"
echo "Signed in as ${LOGIN}"
echo

echo "Public repositories owned by ${LOGIN}:"
mapfile -t REPOS < <(gh repo list "${LOGIN}" --visibility public --source --limit 1000 --json nameWithOwner --jq '.[].nameWithOwner' | sort -f)
gh repo list "${LOGIN}" --visibility public --limit 1000 --json nameWithOwner,isFork --jq '.[] | select(.isFork) | "    " + .nameWithOwner + "  [fork]"'

if [[ "${#REPOS[@]}" -eq 0 ]]; then
  echo "    (none that you created)"
else
  printf '    %s\n' "${REPOS[@]}"
fi
echo

if [[ "${APPLY}" != "--apply" ]]; then
  echo "Dry run. Re-run with --apply to make these private."
  exit 0
fi

# Forks are listed separately above because gh repo list --source hides them.
# Add any fork you want to keep private to the loop by name, or run the Python script,
# which handles forks and non forks together.

for REPO in "${REPOS[@]}"; do
  echo "Making ${REPO} private..."
  gh repo edit "${REPO}" --visibility private --accept-visibility-change-consequences
done

echo
echo "Verifying..."
LEFT="$(gh repo list "${LOGIN}" --visibility public --limit 1000 --json nameWithOwner --jq 'length')"
if [[ "${LEFT}" == "0" ]]; then
  echo "Verified: ${LOGIN} owns zero public repositories."
else
  echo "Still public: ${LEFT}"
  gh repo list "${LOGIN}" --visibility public --limit 1000 --json nameWithOwner --jq '.[].nameWithOwner'
  exit 1
fi
