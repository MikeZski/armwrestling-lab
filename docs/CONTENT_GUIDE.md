# Content and download maintenance

All source files are UTF-8 JSON. Build and audit after any change:

```sh
python scripts/build.py
python scripts/check.py
```

Do not edit generated `site/` files. The next build replaces that directory completely.

## Edit an article

`content/articles/en.json` and `content/articles/pl.json` are dictionaries keyed by stable article ID. Each entry has `title`, `summary`, `takeaway`, `sections`, `limitations`, and `figure`. A section has a `heading` and a list of `paragraphs`. Each article currently has four sections. Keep both language editions aligned.

Use plain text, not HTML. The generator escapes content. Numeric citations such as `[1]`, `[2, 3]` and `[2-4]` become local links to the bibliography. The order of reference IDs in `content/articles.json` defines the citation numbers. Do not renumber one language without updating the other.

`summary` is used on cards and in metadata. Keep it specific and relatively short. `takeaway` is a synthesis, not a promise of an individual result. `limitations` must remain visible and meaningful.

## Metadata and video addresses

`content/articles.json` is an ordered array. Its order is the default editorial order. Important fields:

| Field | Meaning |
|---|---|
| `id` | Stable URL slug, e.g. `train-rfd`. Do not change published IDs casually. |
| `category` | One of the IDs in `content/categories.json`. |
| `image` | Relative file under `static/`, e.g. `assets/img/train-rfd.webp`. |
| `video_id` | 11-character YouTube identifier or `null`. Never the full URL. |
| `video_query` | Honest fallback search query if there is no confirmed ID. |
| `references` | Ordered list of IDs in `content/references.json`. |
| `pdfs` | IDs of related reports in `content/downloads.json`. |
| `figure` | ID of the dataset/schematic in `content/figures.json`. |
| `date`, `modified` | ISO dates of the editorial publication and revision, not guessed video-upload dates. |
| `transcript` | Provenance path under `sources/transcripts/`; not served publicly by Pages. |

The global YouTube link is `channel_url` in `content/site.json`. When the owner supplies a confirmed channel address, also set `channel_url_is_search` to `false`.

## Add a new article

Add its metadata, complete text in every published language, bibliography records, image, and figure specification. Reuse an existing figure type instead of inventing undocumented formats. Include a source transcript where available. A new entry must exist in all enabled language dictionaries; otherwise the build refuses to publish a partially translated library.

Use the existing five categories unless the editorial scope really changes. Category titles/descriptions are translated in `content/categories.json`.

## Research references

`content/references.json` is keyed by citation ID. Entries contain `authors`, `year`, `title`, `journal`, and an HTTPS `url`; a supplied local report can use `file` instead. Prefer a DOI or the primary publication. Do not link a secondary blog as though it were the experiment. Keep reference titles in their original publication language.

Check that each citation supports the adjacent claim, not merely the broad topic. Distinguish population, protocol, outcome, effect estimate, confidence interval, and interpretation. Do not describe a confidence interval around a breakpoint as a prescribed daily intake range.

## Figures

Numerical data are in `content/figures.json`. Localized labels, titles and captions belong to each article's `figure` block. Supported `kind` values: `grouped`, `interval`, `table`, `numbers`, `concept`. Origins: `reported`, `calculation`, `editorial`.

For reported values retain their exact meaning and units, plus `source`/`pages` or `source_url`. For calculated examples retain assumptions and a `formula`. Concepts are not measured effects: do not add percentage weights or implied rankings. Preserve comparable scales in grouped charts. The generator produces both the visible figure and an inspectable `site/data/{language}/{article}.json` export.

Every figure needs a substantive caption explaining its source, population and limitations. No raw force-time curves were present in the supplied archive; the club figure deliberately shows reported checkpoints, not fabricated traces.

## Add a local download

Place the real file under `static/downloads/software/`, `static/downloads/models/` or `static/downloads/reports/`. Add an entry to `content/downloads.json`:

```json
{
  "id": "measurement-tool-v1",
  "type": "software",
  "path": "downloads/software/measurement-tool-v1.zip",
  "language": "en",
  "published": true,
  "title": {"en": "Measurement tool", "pl": "Program pomiarowy"},
  "description": {"en": "A factual description and platform requirements.", "pl": "Opis funkcji i wymagania systemowe."},
  "version": "1.0.0"
}
```

This is a documentation example, not a shipped download. Add the actual archive before enabling it. The builder checks that local files exist, calculates their byte size and SHA-256 checksum, and copies them unchanged. Use `type: "model3d"` for 3D files and `type: "report"` for PDFs. For reports, include a numeric `pages` field. All enabled languages need a title and description.

The section is a static catalog, not an upload administration panel. To publish a new file, commit its catalog entry and source file (or a Release URL), then deploy.

## GitHub Releases / external downloads

For a large binary, upload it to the owner's actual GitHub Release first. Use its HTTPS asset URL as `url`, and omit `path`. Optional `bytes` and `sha256` fields may be supplied only after measuring the real asset. Cross-origin download behavior depends on the remote server; the explicit open link remains available.

Do not put a guessed release URL or a nonexisting file in the published catalog. Entries with `published: false` are excluded from the site.

## Build settings

`site_url` may remain empty for an offline preview. On GitHub, the workflow supplies it automatically. For another server, use `--site-url https://your-real-domain.example/subfolder` with the actual destination. `default_language` must be an enabled language. `featured_article` is an article ID. Counts are derived from actual published records.

Keep third-party tracking, embeds, user accounts and forms out of this version unless you intentionally implement their infrastructure and update the privacy page. The existing YouTube cards are links, not automatically loaded players.
