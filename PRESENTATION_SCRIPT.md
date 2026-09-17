# Five-Minute Presentation Script

## 0:00–0:35 — Problem

"I interpreted the task as reducing pre-account-planning research time for roofing-distributor sales representatives. I focused on a reliable workflow: ingest a publicly listed contractor, gather current public evidence, create a structured brief, rank the opportunity transparently, and show the next action in a review interface."

## 0:35–1:10 — Architecture

"I separated source ingestion, web research, AI synthesis, deterministic scoring, storage, and presentation. Perplexity returns current ranked web evidence. OpenAI converts only that evidence into a typed account brief. SQLite stores the prototype data, while the data-access pattern can migrate to PostgreSQL."

## 1:10–2:40 — Demo

- Open the lead dashboard.
- Select a high-priority lead.
- Show company/GAF facts.
- Show the score breakdown.
- Show why-now, products, outreach angle and next action.
- Open one supporting source.
- Show the public decision-maker section or the honest “not verified” state.

## 2:40–3:35 — Trust

"The model cannot invent a decision-maker, email, project or source. Structured output is validated with Pydantic, and any source URL not in the evidence supplied to the model is removed. The score is deterministic and visible. Evidence is stored with retrieval time, and unchanged evidence does not trigger another model call."

## 3:35–4:25 — Scale

"The local demo uses synchronous processing and SQLite. At production scale I would use approved source ingestion, PostgreSQL, queued background workers, tenant and territory permissions, rate limits, idempotency, dead-letter handling, secrets management, and observability for cost, latency, freshness and quality."

## 4:25–5:00 — Trade-off and close

"I deliberately prioritised one auditable end-to-end flow over a large, fragile scraper. The system supports the sales representative rather than replacing judgement. With more time, I would add licensed data sources, contact verification, a FastAPI backend, background jobs and an evaluation set built with sales-team feedback."
