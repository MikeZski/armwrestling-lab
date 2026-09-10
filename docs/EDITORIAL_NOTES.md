# Editorial notes and source selection

## Scope

The input archive contains 21 English subtitle sets and 9 PDF reports/decks. This edition selects 12 research-oriented topics and excludes 9 demonstrations or insufficiently interpretable items. The articles synthesize the relevant transcript and available report material; not every selected transcript has its own PDF. Where a PDF is absent, the article identifies the published evidence rather than inventing a report.

The worded conclusions do not copy every spoken claim uncritically. Animal/tissue-model, observational, acute biomarker and longitudinal human outcomes are kept distinct. Club data are not labelled a controlled scientific experiment.

## Article-to-video map

| Article ID | English title | Direct video ID |
|---|---|---|
| `rfd-armwrestling` | RFD: the strength you can use before the match moves on | Not confirmed: labelled search link |
| `train-rfd` | Training RFD: fast intent, specific adaptation | `XXUyS5iV9LI` |
| `tendon-stiffness` | Does an “explosive” drill really stiffen tendons? | `SC784mFIc6I` |
| `keith-baar-isometrics` | Keith Baar’s isometrics: useful ideas, not a magic hold time | `mBCTd_kZCZk` |
| `collagen-vitamin-c` | Collagen and vitamin C: what the tendon evidence really shows | `WC5TpDxxuv0` |
| `diet-armwrestling` | An armwrestler’s diet: enough fuel, not endless bulking | `KUzvLxYh0Qk` |
| `overtraining` | Fatigue, stalled progress or overtraining? Do not confuse them | Not confirmed: labelled search link |
| `body-mass-ffmi` | Body mass and FFMI: a useful estimate, not a doping detector | Not confirmed: labelled search link |
| `measure-progress` | Are you stronger—or has the test become easier? | Not confirmed: labelled search link |
| `side-pressure` | Side pressure: a system of forces, not one muscle | `Pw6SRarWPEA` |
| `great-armwrestler` | What makes a great armwrestler? A profile, not one superpower | `Pi8MRXDvF48` |
| `enhanced-games` | Enhanced Games: a spectacle is not a controlled experiment | Not confirmed: labelled search link |

The main channel link is also a labelled channel search because an exact channel handle was not present in the archive. Replace `channel_url` and set `channel_url_is_search` to false after owner confirmation. Direct video IDs were matched from available indexed video titles/descriptions; complete playback and future availability are not guaranteed.

## Excluded source folders

- `table time`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `why they quit`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `armwrestling handles`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `side rpessure ligament vs tendon`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `ból w nadgarstku`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `how to apply bfr`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `wiezadla w nadgarstku`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `devon larrat pronation`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.
- `rugby ball`: Demonstration, exercise/setup instruction, or commentary without enough independently interpretable research content for this edition.

Exclusion is an editorial scope decision, not a claim that these videos contain no valuable information. In particular, exercise setup and application of BFR should not be reconstructed as instructions from an ambiguous transcript. The supplied BFR PDF remains available as a source file, with no invented tutorial article.

## Figures and limits

Twelve visual summaries comprise eight numerical displays and four conceptual diagrams. Five displays reproduce reported values, three are explicit calculated examples, and four are non-quantitative concepts. Every figure has a localized caption, visible origin label and data JSON export.

The RFD club graphic reports two checkpoints from the supplied wrist-curl report; no raw CSV or continuous trace was supplied. The FFMI display uses a hypothetical 90 kg, 1.80 m person under different body-fat assumptions; it does not estimate any named athlete. The torque display is an elementary mechanical example, not an elbow joint model or injury threshold. The sampling table is arithmetic, not a device-performance validation.

The tendon meta-analysis display uses reported standardized changes and their 95% confidence intervals; these are not percentage gains or controlled causal effects. The protein graphic shows uncertainty around an estimated statistical breakpoint, not a prescribed intake band.

The Enhanced Games article is a reading of the supplied corrected report with its stated 30 June 2026 scope. It does not present the report as current governing-body ratification, a controlled doping experiment, or advice about performance-enhancing substances.

## Dates, authorship and revisions

2026-09-09 identifies this editorial website edition. It is not asserted to be the upload date of all videos. The author line is the channel editorial identity, not an invented individual credential. The owner should read the articles before publishing them under the channel brand and can edit all wording in the JSON source.

## Source retention

`sources/selection.json` records the 12 included and 9 excluded folders. `sources/archive-manifest.json` preserves the supplied manifest. The original large ZIP is not duplicated in the project; its SHA-256 is recorded in `sources/selection.json`. Original PDFs are included in `static/downloads/reports/`, and the build copies them byte-for-byte.
