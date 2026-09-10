# Armwrestling LAB

Open **START.html** after extracting the entire archive. The ready-built site is in `site/`. No installation, account, API, framework or database is needed to read it. Videos and external papers require internet access.

This release contains 12 research articles in complete Polish and English editions, five topic categories, 12 sourced visual summaries and nine original supplied English PDFs. Search is local and indexes the complete article text. The interface includes responsive navigation, filtering, sorting, dark/light mode, same-page language switching, print styles and a download catalog ready for real software and 3D files.

For GitHub Pages, commit this entire project with `.github/` at repository root, select **Settings > Pages > Source: GitHub Actions**, then run the included workflow. It builds only the public `site/` artifact using the real Pages base URL. No account has been deployed by this archive itself.

Rebuild with Python 3.10+ (no third-party packages):

```sh
python scripts/build.py
python scripts/check.py
python -m unittest discover -s tests -p "test_*.py" -v
python preview.py
```

For another server: `python scripts/build.py --site-url https://your-actual-domain.example`, then upload the contents of `site/`.

Edit source in `content/` and `static/`, never generated HTML. Guides: `docs/CONTENT_GUIDE.md`, `docs/TRANSLATIONS.md`, `docs/QA.md`. The Polish deployment handoff is `AGENT_HANDOFF.md`.

Only PL and EN are published. The other 11 requested languages have configured identities, not pretend translations. Seven articles have matched direct video links; five use clearly labelled topic searches pending the owner's exact IDs. Software and 3D categories are intentionally empty until actual files are supplied.
