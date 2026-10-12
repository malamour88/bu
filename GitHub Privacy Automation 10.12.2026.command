#!/bin/zsh
# GitHub Privacy Automation runner                               Date: 10.12.2026
# Double click this file on your Mac. It sets up Python Playwright once, then runs the automation.
# Pass arguments through, for example:  ./"GitHub Privacy Automation 10.12.2026.command" --dry-run

cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is missing. Install the Xcode Command Line Tools: xcode-select --install"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Setting up a private Python environment (one time)..."
  python3 -m venv .venv || exit 1
fi
.venv/bin/python -m pip install --quiet --upgrade pip playwright || exit 1
.venv/bin/python -m playwright install chromium || exit 1

.venv/bin/python "GitHub Privacy Automation 10.12.2026.py" "$@"
STATUS=$?
echo
echo "Finished with status ${STATUS}. You can close this window."
exit ${STATUS}
