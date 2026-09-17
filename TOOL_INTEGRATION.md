# Optional Agent-Tool Integration

The main case-study objectives are data, pipeline and UI quality. If the interviewers ask how this fits an agentic orchestrator, register these deterministic Python functions from `src.agent_tools`:

1. `ingest_gaf_seed(csv_path)` — imports an approved or manually verified seed file.
2. `build_company_intelligence(company_id, force_research=False)` — performs web research, structured synthesis and persistence for one company.
3. `retrieve_lead_brief(company_id)` — returns the stored score, insight, contacts and sources.

The language model may decide which function to call, but the functions enforce validation, persistence and evidence controls. The scraper is deliberately not an autonomous tool because production source acquisition should be approved and governed.
