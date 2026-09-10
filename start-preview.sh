#!/bin/sh
set -eu
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
    exec python3 preview.py "$@"
elif command -v python >/dev/null 2>&1; then
    exec python preview.py "$@"
else
    printf '%s\n' 'Python was not found. Open START.html directly in your browser instead.'
    exit 1
fi
