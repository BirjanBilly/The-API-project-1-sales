# Four-Hour Case Study Runbook

## 0:00–0:15 — Protect credentials and inspect the task

- Revoke the exposed OpenAI and Perplexity keys.
- Generate replacement keys.
- Copy `.env.example` to `.env`.
- Confirm the required deliverables and presentation length.

## 0:15–0:40 — Acquire a small verified dataset

On the GAF page:

1. Select Residential.
2. Clear `SL1` with the red X.
3. Type `10013`.
4. Select the New York autocomplete result.
5. Search at 25 miles; increase to 50 only if necessary.
6. Record 15–20 contractors in the CSV template.

Prioritise company name, profile URL, public phone/site, distance and certification. Do not waste the first hour trying to reverse engineer a private endpoint.

## 0:40–1:10 — Install and initialise

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
python -m scripts.init_db
python -m scripts.import_csv data/gaf_contractors_10013.csv
```

## 1:10–1:50 — Complete one vertical slice

```powershell
python -m scripts.run_pipeline --limit 1 --no-fallback
streamlit run app.py
```

Check that one contractor has:

- stored source record;
- web evidence;
- structured insight;
- score breakdown;
- source links in the UI.

## 1:50–2:40 — Improve data and workflow

- import the remaining verified contractors;
- enrich the top 3–5 rather than every lead;
- check duplicates and missing fields;
- verify that unsupported people are not shown;
- add representative status/notes.

## 2:40–3:15 — Testing and failure handling

```powershell
pytest
ruff check .
```

Test:

- duplicate imports;
- blank ratings;
- missing API key fallback;
- one failed lead while the batch continues;
- unchanged evidence reuses an insight;
- unsupported citation is removed.

## 3:15–3:35 — Polish the UI

- sort by lead score;
- add filters;
- confirm evidence links work;
- use one polished high-priority lead for the demo;
- make uncertainty visible.

## 3:35–4:00 — Presentation preparation

Rehearse:

1. user problem;
2. architecture;
3. successful lead walkthrough;
4. trust and data-quality controls;
5. scaling plan;
6. limitations and next iteration.

Do not perform a risky live full-batch API run during the presentation. Use already stored evidence and demonstrate one controlled refresh if required.
