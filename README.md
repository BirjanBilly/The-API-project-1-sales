# Roofing Sales Intelligence

This is a portfolio case study based on a software engineering interview project. This prototype turns a small set of public roofing contractor records into a sales review queue: it imports company data, gathers public search evidence when configured, drafts account briefs, ranks leads with an explainable score, and presents the results in a Streamlit app. The code is shared as a demonstration of data engineering, API integration, structured AI output, relational modeling, testing, and human review workflows.

## What you can inspect

| Area | Implementation | Entry point |
| --- | --- | --- |
| Data ingestion | CSV validation, normalization, and company upsert | `src/ingest.py`, `scripts/import_csv.py` |
| Research | Public-web search and stored source snippets | `src/research.py` |
| Intelligence | Pydantic-structured OpenAI response; source URL filtering; deterministic low-confidence fallback | `src/intelligence.py` |
| Prioritization | Seven weighted, inspectable components totaling at most 100 points | `src/scoring.py` |
| Persistence | SQLAlchemy company, evidence, contact, insight, review, and pipeline-run tables | `src/models.py`, `src/database.py` |
| User interface | Lead list, lead detail, sources, notes, and enrichment controls | `app.py` |
| Quality checks | Unit tests, Ruff, and GitHub Actions | `tests/`, `.github/workflows/ci.yml` |

See [the technical walkthrough](docs/ARCHITECTURE.md), [data provenance and limitations](docs/DATA_PROVENANCE.md), and [the portfolio case study](docs/PORTFOLIO_CASE_STUDY.md). The original [design notes](DESIGN.md) and [data dictionary](DATA_DICTIONARY.md) provide more detail.

## How the flow works

1. Import contractor records from a CSV. The importer requires `company_name` and `source_zip`, and uses a GAF profile URL or normalized name and postal code to find existing records.
2. Optionally run public-web research with a Perplexity API key. Evidence snippets and URLs are saved for review.
3. Optionally synthesize a structured account brief with an OpenAI API key. Returned source URLs and decision-maker source URLs are restricted to the retrieved evidence URLs. A URL match alone is not proof that every statement or person is correct; human verification remains necessary.
4. Compute a deterministic score from certification, proximity, reputation, profile completeness, recent activity, decision-maker confidence, and product-fit confidence. Missing distance receives zero proximity points; it is not imputed.
5. Review the queue in Streamlit and record status or notes. The app does not send outreach.

### Local quick start

Requires Python 3.10+ and a working Python package installer. Commands below use Windows PowerShell from the repository root.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m scripts.init_db
python -m scripts.import_csv data/gaf_contractors_10013.csv
streamlit run app.py
```

Open the local URL Streamlit prints (normally `http://localhost:8501`). The checked-in CSV provides seed companies; it does **not** include the enriched insights in the original local SQLite database. To create an offline, low-confidence brief without API keys:

```powershell
python -m scripts.run_pipeline --limit 2
```

To try live enrichment, copy `.env.example` to `.env`, supply your own valid `PERPLEXITY_API_KEY` and `OPENAI_API_KEY`, check the configured model and API access, and run:

```powershell
Copy-Item .env.example .env
python -m scripts.run_pipeline --limit 2 --no-fallback
```

The live path makes paid external API calls and may fail if a provider's model, API, or permissions have changed. Inspect each source and generated claim before use. For browser-assisted GAF capture, install Chromium separately with `playwright install chromium` and follow [the original runbook](CASE_STUDY_RUNBOOK.md).

On macOS or Linux, use `python3 -m venv .venv`, `source .venv/bin/activate`, and the equivalent `python`/`python3` invocation for the remaining commands.

## Checks

```powershell
python -m pytest
python -m ruff check .
```

CI runs these checks on pushes and pull requests. Local validation requires the dependencies in `requirements.txt`; this documentation update did not independently rerun the suite in an installed project environment.


## Prototype versus production

Prototype:

- SQLite;
- Streamlit;
- synchronous, user-triggered enrichment;
- manually verified GAF seed data.

Production path:

- approved/licensed source ingestion;
- PostgreSQL and migrations;
- queued background workers;
- tenant and territory permissions;
- rate limits, idempotency and dead-letter handling;
- secret manager and audit logs;
- API/backend separated from the web UI;
- quality evaluation and human verification.

## Scope and responsible use

The source CSV is a dated snapshot of public business listings, not a continuously updated or licensed production data feed. A manual review is needed before relying on a profile, company status, contact, source claim, or recommendation. The original local case-study report recorded 20 companies, five enriched leads, 52 evidence records, and ten contact candidates; these are historical local-run counts, not results reproduced from a fresh clone. The database and logs are intentionally excluded from a clean public repository. See [data provenance](docs/DATA_PROVENANCE.md).

Keep credentials in an untracked `.env` file, rotate any previously exposed keys, and review source-site terms before automated collection. No personal email guessing or automated outreach is part of the project. See [SECURITY.md](SECURITY.md).
