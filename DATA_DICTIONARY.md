# Data Dictionary

## Company source fields

| Field | Meaning |
|---|---|
| company_name | Public business name |
| gaf_profile_url | Original GAF evidence URL |
| company_website | Public business website |
| address/city/state/postal_code | Public business location |
| phone | Public business phone only |
| distance_miles | Distance from territory ZIP |
| certification_level | Public GAF certification |
| award | Public GAF award, if displayed |
| rating/review_count | Public reputation fields, if displayed |
| source_zip | Territory/search ZIP, normally 10013 |
| captured_at | Date source record was captured |

## Evidence fields

| Field | Meaning |
|---|---|
| source_url | Public evidence URL |
| source_title | Page title returned by search |
| snippet | Search result text supplied to the model |
| published_at | Publication/update date if available |
| signal_type | Heuristic category such as project, hiring or leadership |
| query | Search query that produced the result |
| retrieved_at | Pipeline retrieval timestamp |

## Insight fields

| Field | Meaning |
|---|---|
| company_summary | Concise evidence-grounded overview |
| why_now | Current reason for representative review |
| pain_points | Possible discussion areas, explicitly treated as inference |
| recommended_products | Broad roofing product categories |
| outreach_angle | Suggested opening approach, not an auto-sent message |
| next_best_action | Human review/call/research recommendation |
| confidence_score | Model confidence constrained to 0–1 |
| source_urls | URLs allowed only from stored evidence |
| evidence_hash | Detects whether generation inputs changed |
