# Portfolio case study: roofing lead intelligence

## Brief and approach

The prototype explores how a sales representative could move from a list of contractor profiles to an evidence-linked queue for account planning. The work combines a reviewed source CSV, repeatable ingestion, public search, structured generation, a transparent ranking rule, and a review UI.

## Engineering decisions

1. **Store source facts separately from generated insights.** Relational tables let a reviewer inspect company records, search evidence, contact candidates, and pipeline outcomes.
2. **Keep ranking deterministic.** Seven visible score components make ranking debuggable and avoid delegating prioritization entirely to a language model.
3. **Constrain generated output.** The model returns a typed structure; source and contact URLs must match supplied evidence URLs. This is a limited guardrail and does not replace factual review.
4. **Support a local demonstration.** A low-confidence fallback provides a visible flow without API keys, while `--no-fallback` requests the live path and surfaces failures.
5. **Make the work inspectable.** Unit tests cover ingestion, intelligence, and scoring; CI runs pytest and Ruff.

## What the original local run showed

The supplied final-readiness report recorded 20 unique companies, five enriched companies, 52 evidence records, ten contact candidates, and three completed pipeline runs. All 20 companies lacked an exact `distance_miles` value in that report. Those numbers describe one historical local run using an excluded SQLite file; a fresh checkout importing the CSV does not reproduce the enriched records automatically.

## What I would improve next

- Audit and refresh source rows and contact candidates with explicit verification dates.
- Evaluate groundedness and ranking usefulness against a human-labeled sample.
- Add integration tests around live-provider failures and source freshness.
- Move ingestion and enrichment into authorized, monitored background jobs before any operational deployment.

## Recruiter walkthrough

Start in `README.md`, inspect `src/pipeline.py` for orchestration, `src/intelligence.py` for structured output and URL checks, `src/scoring.py` for the interpretable ranking, `src/models.py` for persistence, and `tests/` for validation. Run the local quick start to see the interface with seed data, then run a small offline pipeline batch to view clearly labelled fallback briefs.
