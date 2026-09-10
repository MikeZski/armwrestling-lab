#!/usr/bin/env python3
"""Create a clean, reproducible-source ZIP. Run checks before packaging.
Usage: python scripts/package.py --output ../Armwrestling-LAB-complete-PL-EN.zip
"""
from __future__ import annotations
import argparse
import hashlib
import zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'node_modules', '.idea', '.vscode'}
EXCLUDE_NAMES = {'.DS_Store', 'Thumbs.db', '.env'}

def package(output: Path) -> int:
    output = output.resolve()
    if not (ROOT / 'site/index.html').is_file():
        raise FileNotFoundError('Build the site first: python scripts/build.py')
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or path.resolve() == output:
                continue
            relative = path.relative_to(ROOT)
            if EXCLUDE_DIRS.intersection(relative.parts) or path.name in EXCLUDE_NAMES:
                continue
            if path.suffix.lower() in {'.pyc', '.pyo', '.ttf', '.otf', '.woff', '.woff2'} or path.name.startswith('.env.'):
                continue
            # Exclude root-level release/input archives, not actual downloadable ZIPs.
            if len(relative.parts) == 1 and (path.suffix.lower() == '.zip' or path.name.endswith('.zip.sha256')):
                continue
            archive.write(path, 'armwrestling-lab/' + relative.as_posix())
            count += 1
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'ZIP integrity failure: {bad}')
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(checksum + '  ' + output.name + '\n', encoding='ascii')
    print(f'Packed {count} files: {output} ({output.stat().st_size:,} bytes)')
    print('SHA-256:', checksum)
    return count

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT.parent / 'Armwrestling-LAB-complete-PL-EN.zip')
    args = p.parse_args()
    package(args.output)

if __name__ == '__main__':
    main()
