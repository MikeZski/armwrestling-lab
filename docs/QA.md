# Release QA - 2026-09-09

## Structural checks

`python scripts/check.py` checks every generated HTML document, local target, fragment ID, language tag, image attributes and numeric citation. The release has 44 HTML files and 24 article editions. The report is `structural-test-report.json`.

Expected nonfatal warnings: five article video IDs are unknown. Those links are labelled YouTube searches, not broken or fabricated watch URLs. External publishers and videos are not batch-network-tested by this validator.

## Browser checks

`browser-test-report.json` contains 132 responsive layout cases: every HTML page at 320, 390 and 1440 CSS pixels. Additional functional checks cover search, category filtering, alphabetical sorting, reset/clear, dark/light theme switching, language menus and Escape, download filtering, truthful empty states, checksums, mobile menus and contents, same-article language links, print layout, and no-JavaScript access.

**Important test boundary:** this execution environment blocks Chromium navigation to both `file://` and loopback HTTP URLs by administrator policy. Browser checks therefore use the exact generated HTML with its exact local CSS, JavaScript and images inlined in an isolated Chromium document. This validates rendering and interactions, but it is not an end-to-end visit to a deployed site and does not prove browser-specific file-navigation or clipboard permissions. The report records this mode explicitly. No external assets are substituted.

The optional test runner supports normal local-server navigation on an unrestricted machine:

```sh
python -m pip install playwright beautifulsoup4
python -m playwright install chromium
python tests/browser_smoke.py --mode http
```

The `--mode isolate --browser /path/to/chromium` mode reproduces the isolated checks. These packages are test-only; they are not required to build, open or host the site. Review snapshots in this directory. No Safari/Firefox audit or formal accessibility certification is claimed.

## Independent build and HTTP checks

`python -m unittest discover -s tests -p "test_*.py" -v` runs nine standard-library tests. They check translation completeness, calculated figures, PDF signatures and identical copies, public-URL metadata and sitemap, structural integrity in a repository subpath, deterministic rebuilding, actual local HTTP delivery at a root and a nested path, removal of fake-domain metadata from an offline build, and preservation of real downloadable ZIP archives in project packages.

Actual HTTP requests use Python's HTTP client, independently of the browser navigation restriction. The build tests operate on a fresh temporary copy of the source. Results are in `unit-test-report.txt`.

## Packaging and release boundary

The ZIP is integrity-checked and extracted into a clean directory. The source in that extracted directory is rebuilt and audited again. Results are recorded in `package-check-report.json`. The project contains no fonts, node_modules, virtual environment, credentials or dependency on the original input archive.

The public GitHub Actions workflow is supplied and its YAML is checked, but it has not been executed on the owner's GitHub account in this conversation. The owner's agent must enable Pages, push the repository and verify the resulting public URL. That final deployment check is specified in `AGENT_HANDOFF.md`.

## Content boundary

This is an editorial research synthesis. The supplied PDFs are editorial reports/slides, not a substitute for the original papers. Figure captions distinguish reported measurements, calculated examples and concepts. Source selection and video-link gaps are documented in `EDITORIAL_NOTES.md`. No bulk live availability guarantee is made for future external research links or videos.
