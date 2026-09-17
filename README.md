# Roofing Sales Intelligence Case Study

A time-boxed, evidence-grounded B2B lead-intelligence prototype for a roofing distributor.

The application lets a sales representative:

- import public GAF contractor records for a territory;
- enrich selected companies with current public-web evidence;
- create structured, source-grounded account briefs;
- rank leads using a transparent deterministic score;
- review public decision-maker candidates without inventing people or contact details;
- store review status and notes in a relational database.

## Security first

The API keys pasted into the conversation are exposed. Revoke them and generate replacements before running this project. Copy `.env.example` to `.env` and add only the replacement keys. Never commit `.env`.

## 1. Fix the GAF search

The supplied printout shows `SL1` in the location field, which is why the page returned zero results.

1. Open the GAF residential contractor page.
2. Select **Residential**.
3. In **Refine by location**, click the red X next to `SL1`.
4. Type `10013`.
5. Select the **New York, NY 10013** autocomplete suggestion.
6. Leave 25 miles selected; use 50 miles only if needed.
7. Run the search and wait for contractor cards.

For the prototype, manually verify 15–40 public records and place them in the included CSV template. The optional Playwright script can assist in collecting visible public profile links, but its output must be reviewed manually and must not be used to bypass access controls or contrary to the site's terms.

## 2. Windows setup

```powershell
mkdir roofing-sales-intelligence
cd roofing-sales-intelligence
# Extract the ZIP contents into this folder.

py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

Copy-Item .env.example .env
notepad .env
```

Insert newly rotated keys into `.env`.

## 3. Prepare data

### Recommended reliable method

1. Open `data/gaf_contractors_template.csv` in Excel.
2. Add the public contractor fields from the GAF result/profile pages.
3. Save it as `data/gaf_contractors_10013.csv`.

### Optional browser-assisted collection

```powershell
python -m scripts.gaf_browser_capture --zip 10013 --output data/gaf_contractors_10013_capture.csv
```

The browser opens. Perform the ZIP search manually, wait for the result cards, and press Enter in the terminal. Open the resulting CSV and correct or complete every row before import.

## 4. Initialise and import

```powershell
python -m scripts.init_db
python -m scripts.import_csv data/gaf_contractors_10013.csv
```

## 5. Run a small enrichment batch

Start with one or two leads to control time and API cost:

```powershell
python -m scripts.run_pipeline --limit 2
```

To require live APIs and fail rather than use the low-confidence offline fallback:

```powershell
python -m scripts.run_pipeline --limit 2 --no-fallback
```

## 6. Launch the UI

```powershell
streamlit run app.py
```

The app normally opens at `http://localhost:8501`.

## 7. Run tests and linting

```powershell
pytest
ruff check .
```

## 8. Optional integration with an agent orchestrator

See `TOOL_INTEGRATION.md` and `src/agent_tools.py`. The wrappers expose ingestion, enrichment and retrieval as typed deterministic tools without making the LLM responsible for data integrity.

## 9. Five-minute demonstration

1. Show the lead dashboard and filters.
2. Open a high-scoring company.
3. Explain the deterministic score breakdown.
4. Show the evidence links and freshness.
5. Show the account summary, why-now signal, products and outreach angle.
6. Demonstrate that an unsupported decision-maker is not invented.
7. Show a pipeline run and explain the production migration path.

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
