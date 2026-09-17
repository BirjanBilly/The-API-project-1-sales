# Data provenance and publication notes

## Included source data

`data/gaf_contractors_10013.csv` is a dated, small public-business-listing seed associated with a GAF residential contractor search for ZIP 10013. It contains business names and, where captured, public profile URLs, business contact details, certification, ratings, and source metadata. Its `captured_at` value reflects a July 2026 collection process. Rows carry `source_type` values with differing collection and review provenance; do not describe the entire CSV as fully independently verified.

Some fields are incomplete. In the original readiness report, all 20 companies had no exact distance. The CSV should be treated as historical demonstration input, not a current source of truth or an authorized bulk feed. Review every row, the source site's current terms, and any right to redistribute the data before publishing or reusing it.

## Excluded local artifacts

Do not publish `roofing_leads.db`, `.env`, `.ruff_cache/`, `outputs/streamlit_debug_log.txt`, or other runtime logs or backups. The database may contain generated briefs, search snippets, contact candidates, and review notes. The logs and intermediate CSVs are debugging artifacts and can contain unreviewed or duplicate values.

The template `data/gaf_contractors_template.csv` is blank apart from headers and is useful as a schema reference. The existing `DATA_DICTIONARY.md` describes field meanings.

## Claims and verification

A matching evidence URL means the source URL was retrieved and included in the model's input; it does not prove a generated summary or named contact is accurate. Open sources, check names and roles, and note retrieval dates before using leads. The score is a heuristic and the offline fallback is intentionally low confidence.
