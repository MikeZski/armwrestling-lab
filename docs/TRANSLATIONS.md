# Language editions

## Release status

**Fully published:** Polish (`pl`) and English (`en`). Each has the complete 12-article library, UI, categories, download descriptions, captions, about page and privacy page.

**Planned, not translated in this package:** Spanish (`es`), Filipino (`fil`), French (`fr`), Japanese (`ja`), Korean (`ko`), Russian (`ru`), Thai (`th`), Vietnamese (`vi`), Chinese (`zh`), Turkish (`tr`) and Georgian (`ka`). These are the screenshot languages plus Turkish and Georgian. There are 13 configured language identities in total, not 13 complete translations.

The language picker exposes only real published editions. It preserves the current article/category/download route. There is no machine-translation widget, remote translation API, English content silently relabelled as another language, or empty localized page.

## Add a complete edition

1. Create `content/articles/CODE.json` with exactly the same article keys as the English file. Translate every title, summary, takeaway, heading, paragraph, limitation, figure title/caption and label. Preserve numeric citations and study numbers.
2. Create `content/ui/CODE.json` with exactly the same keys as `content/ui/en.json`. Translate the whole UI, including error messages, caveats and privacy wording. Update `language_intro` in existing UIs so it accurately describes the new release state.
3. Add the new language's `title` and `description` to every category in `content/categories.json` and every published item in `content/downloads.json`.
4. In `content/site.json`, add the code to `published_languages` and set its status to `published` in `languages`. Keep `default_language` enabled. Do not enable an unfinished language just to make its flag appear.
5. Build, run `scripts/check.py`, and run the regression tests. Review numbers, citation alignment, headings and long captions. Test 320px and 390px layouts. The root language landing, header links and sitemap alternate links are generated automatically.

## Editorial review

Do not translate author surnames, DOI identifiers, software filenames or data values. Translate explanatory labels while preserving units. For scientific terms, keep a short internationally recognizable abbreviation where useful (RFD, FFMI, CSA). Distinguish stiffness from Young's modulus, muscle from tendon, association from causation, and a tissue model from a clinical trial.

Native-language scientific review is especially valuable for medical nuance and unfamiliar terminology. No translation should upgrade a cautious association into a treatment promise. Original supplied PDF downloads remain English unless actual translated PDFs are created separately; the UI already says so.

The site currently uses system fonts; it does not distribute font files. A viewer's operating system supplies the glyph coverage for additional scripts. For non-space-separated scripts, review the reading-time estimator in `scripts/build.py`; its current word-count formula is calibrated to the published PL/EN editions.
