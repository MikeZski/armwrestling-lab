#!/usr/bin/env python3
"""Optional local HTTP preview. The built site also opens directly via START.html.
Run: python preview.py --port 8080 [--no-browser]
Serves only site/ and binds only to this computer (127.0.0.1).
"""
from __future__ import annotations
import argparse
import functools
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent / 'site'
    if not (root / 'index.html').is_file():
        print('Missing site/index.html. Run: python scripts/build.py', file=sys.stderr)
        return 1
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), functools.partial(SimpleHTTPRequestHandler, directory=str(root)))
    except (OSError, OverflowError) as exc:
        print(f'Cannot open preview port: {exc}\nTry: python preview.py --port 8081', file=sys.stderr)
        return 1
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Armwrestling LAB: {url}\nPress Ctrl+C to stop. This is a local preview, not a public server.')
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nPreview stopped.')
    finally:
        server.server_close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
