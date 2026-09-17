from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import init_db, session_scope
from src.ingest import import_csv
from src.models import Company, LeadReview, PipelineRun
from src.pipeline import run_pipeline
from src.scoring import compute_score
from src.utils import normalized_company_name

st.set_page_config(
    page_title="Roofing Sales Intelligence",
    page_icon="🏠",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .lead-card {border: 1px solid #e4e7ec; border-radius: 14px; padding: 18px; background: white;}
    .small-muted {color: #667085; font-size: 0.9rem;}
    .priority {background:#ecfdf3; color:#027a48; border-radius:999px; padding:4px 10px; font-weight:600;}
    .warning-badge {background:#fffaeb; color:#b54708; border-radius:999px; padding:4px 10px; font-weight:600;}
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()


def load_companies() -> list[Company]:
    with session_scope() as session:
        companies = list(
            session.scalars(
                select(Company)
                .options(
                    selectinload(Company.evidence),
                    selectinload(Company.contacts),
                    selectinload(Company.insight),
                    selectinload(Company.reviews),
                )
                .order_by(Company.company_name)
            ).all()
        )
        for company in companies:
            session.expunge(company)
        return companies


def company_rows(companies: list[Company]) -> pd.DataFrame:
    rows = []
    for company in companies:
        score = compute_score(company)
        latest_review = max(company.reviews, key=lambda item: item.updated_at) if company.reviews else None
        rows.append(
            {
                "company_id": company.id,
                "Score": score.total,
                "Company": company.company_name,
                "Distance": company.distance_miles,
                "Certification": company.certification_level or company.award or "Unspecified",
                "Rating": company.rating,
                "Reviews": company.review_count,
                "Why now": company.insight.why_now if company.insight else "Research pending",
                "Confidence": company.insight.confidence_score if company.insight else None,
                "Status": latest_review.status if latest_review else "new",
            }
        )
    return pd.DataFrame(rows)


st.title("🏠 Roofing Sales Intelligence")
st.caption("Evidence-grounded account planning for roofing-distributor sales representatives")

with st.sidebar:
    st.subheader("Territory")
    source_zip_filter = st.text_input("Source ZIP", value="10013")
    max_distance = st.slider("Maximum distance (miles)", 5, 100, 25, 5)
    st.divider()
    st.info(
        "AI suggestions must be reviewed by a representative. The app does not invent or auto-contact decision-makers."
    )

companies = load_companies()
dataframe = company_rows(companies)

if not dataframe.empty:
    company_by_id = {company.id: company for company in companies}
    valid_ids = [
        company.id
        for company in companies
        if company.source_zip == source_zip_filter
        and (company.distance_miles is None or company.distance_miles <= max_distance)
    ]
    dataframe = dataframe[dataframe["company_id"].isin(valid_ids)].copy()

leads_tab, detail_tab, pipeline_tab, import_tab = st.tabs(
    ["Lead dashboard", "Lead detail", "Pipeline", "Data import"]
)

with leads_tab:
    if dataframe.empty:
        st.warning("No leads match the current filters. Import the GAF CSV in the Data import tab.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Territory leads", len(dataframe))
        col2.metric("Researched", int(dataframe["Confidence"].notna().sum()))
        col3.metric("Priority leads", int((dataframe["Score"] >= 55).sum()))
        col4.metric("Verified contacts", sum(bool(company.contacts) for company in companies if company.id in valid_ids))

        filters1, filters2 = st.columns(2)
        with filters1:
            certifications = sorted(dataframe["Certification"].dropna().unique().tolist())
            selected_certifications = st.multiselect("Certification filter", certifications)
        with filters2:
            statuses = sorted(dataframe["Status"].dropna().unique().tolist())
            selected_statuses = st.multiselect("Review status", statuses)

        filtered = dataframe.copy()
        if selected_certifications:
            filtered = filtered[filtered["Certification"].isin(selected_certifications)]
        if selected_statuses:
            filtered = filtered[filtered["Status"].isin(selected_statuses)]
        filtered = filtered.sort_values(["Score", "Company"], ascending=[False, True])

        st.dataframe(
            filtered.drop(columns=["company_id"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn(min_value=0, max_value=100),
                "Confidence": st.column_config.ProgressColumn(min_value=0.0, max_value=1.0),
                "Why now": st.column_config.TextColumn(width="large"),
            },
        )
        st.download_button(
            "Download filtered lead queue",
            data=filtered.drop(columns=["company_id"]).to_csv(index=False).encode("utf-8"),
            file_name="roofing_lead_queue.csv",
            mime="text/csv",
        )

        chart = px.histogram(filtered, x="Score", nbins=10, title="Lead-score distribution")
        st.plotly_chart(chart, use_container_width=True)

with detail_tab:
    if dataframe.empty:
        st.info("Import leads before opening the detail view.")
    else:
        options = {
            f"{row['Company']} — score {row['Score']}": int(row["company_id"])
            for _, row in dataframe.sort_values("Score", ascending=False).iterrows()
        }
        selected_label = st.selectbox("Open a lead", list(options))
        selected_company = next(company for company in companies if company.id == options[selected_label])
        score = compute_score(selected_company)

        title_col, badge_col = st.columns([4, 1])
        title_col.header(selected_company.company_name)
        badge_col.metric("Lead score", score.total)

        info_col, intelligence_col = st.columns([1, 2])
        with info_col:
            st.subheader("Account")
            st.write(f"**Certification:** {selected_company.certification_level or selected_company.award or 'Not recorded'}")
            st.write(f"**Distance:** {selected_company.distance_miles if selected_company.distance_miles is not None else 'Unknown'} miles")
            st.write(f"**Phone:** {selected_company.phone or 'Not available'}")
            st.write(f"**Address:** {selected_company.address or 'Not available'}")
            if selected_company.company_website:
                st.link_button("Company website", selected_company.company_website)
            if selected_company.gaf_profile_url:
                st.link_button("GAF profile", selected_company.gaf_profile_url)

            st.subheader("Score explanation")
            st.json(score.as_dict())

        with intelligence_col:
            st.subheader("Account intelligence")
            if selected_company.insight:
                insight = selected_company.insight
                st.markdown("#### Why now")
                st.write(insight.why_now)
                st.markdown("#### Summary")
                st.write(insight.company_summary)
                st.markdown("#### Possible pain points")
                for item in insight.pain_points:
                    st.write(f"- {item}")
                st.markdown("#### Product categories to discuss")
                for item in insight.recommended_products:
                    st.write(f"- {item}")
                st.markdown("#### Outreach angle")
                st.info(insight.outreach_angle)
                st.markdown("#### Next best action")
                st.success(insight.next_best_action)
                st.caption(
                    f"Confidence {insight.confidence_score:.0%} • generated with {insight.model_name} • {insight.generated_at}"
                )
            else:
                st.warning("Research has not been generated for this lead.")

        st.subheader("Public decision-maker candidates")
        if selected_company.contacts:
            for contact in selected_company.contacts:
                st.write(
                    f"**{contact.full_name}** — {contact.job_title} • confidence {contact.confidence:.0%}"
                )
                st.link_button("Supporting source", contact.source_url, key=f"contact-{contact.id}")
        else:
            st.info("No public decision-maker has been verified. Do not guess one.")

        st.subheader("Supporting evidence")
        if selected_company.evidence:
            for item in selected_company.evidence:
                with st.expander(item.source_title or item.source_url):
                    st.write(item.snippet or "No snippet returned.")
                    st.caption(f"Signal: {item.signal_type or 'general'} • retrieved {item.retrieved_at}")
                    st.link_button("Open source", item.source_url, key=f"evidence-{item.id}")
        else:
            st.info("No web evidence has been stored.")

        st.subheader("Representative review")
        default_review = max(selected_company.reviews, key=lambda item: item.updated_at) if selected_company.reviews else None
        review_status = st.selectbox(
            "Status",
            ["new", "researching", "ready_for_outreach", "contacted", "not_a_fit"],
            index=["new", "researching", "ready_for_outreach", "contacted", "not_a_fit"].index(default_review.status) if default_review else 0,
        )
        assigned_to = st.text_input("Assigned representative", value=default_review.assigned_to if default_review and default_review.assigned_to else "")
        notes = st.text_area("Notes", value=default_review.notes if default_review and default_review.notes else "")
        if st.button("Save review"):
            with session_scope() as session:
                review = session.scalar(
                    select(LeadReview).where(LeadReview.company_id == selected_company.id)
                )
                if review is None:
                    review = LeadReview(company_id=selected_company.id)
                    session.add(review)
                review.status = review_status
                review.assigned_to = assigned_to.strip() or None
                review.notes = notes.strip() or None
            st.success("Review saved. Refresh the page to update dashboard status.")

with pipeline_tab:
    st.subheader("Enrichment pipeline")
    if not companies:
        st.info("Import leads first.")
    else:
        company_options = {company.company_name: company.id for company in companies}
        selected_names = st.multiselect("Companies to enrich", list(company_options))
        force_research = st.checkbox("Force fresh research even if cached", value=False)
        allow_fallback = st.checkbox("Allow low-confidence deterministic fallback", value=True)
        if st.button("Run selected pipeline", type="primary", disabled=not selected_names):
            ids = [company_options[name] for name in selected_names]
            with st.spinner("Researching and generating account briefs..."):
                result = run_pipeline(
                    ids,
                    force_research=force_research,
                    allow_offline_fallback=allow_fallback,
                )
            st.json(result)
            st.success("Pipeline finished. Refresh the app to see the updated lead details.")

        with session_scope() as session:
            runs = list(session.scalars(select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(10)).all())
        if runs:
            st.subheader("Recent runs")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Run": run.id,
                            "Started": run.started_at,
                            "Status": run.status,
                            "Requested": run.companies_requested,
                            "Processed": run.companies_processed,
                            "Failed": run.companies_failed,
                        }
                        for run in runs
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )

with import_tab:
    st.subheader("Import GAF contractor data")
    st.write(
        "Use the included CSV template. For the prototype, manually verify public GAF records or use the optional browser-assisted capture script and review its output before import."
    )
    template_path = Path("data/gaf_contractors_template.csv")
    if template_path.exists():
        st.download_button(
            "Download CSV template",
            data=template_path.read_bytes(),
            file_name="gaf_contractors_template.csv",
            mime="text/csv",
        )
    uploaded = st.file_uploader("Upload completed CSV", type=["csv"])
    if uploaded is not None and st.button("Import uploaded CSV"):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(uploaded.getbuffer())
            temp_path = Path(tmp.name)
        try:
            summary = import_csv(temp_path)
            st.success("CSV processed.")
            st.json(summary.model_dump())
        finally:
            temp_path.unlink(missing_ok=True)

    st.divider()
    st.subheader("Add one lead manually")
    with st.form("manual-lead"):
        company_name = st.text_input("Company name *")
        source_zip = st.text_input("Source ZIP *", value="10013")
        gaf_url = st.text_input("GAF profile URL")
        website = st.text_input("Company website")
        phone = st.text_input("Public business phone")
        certification = st.text_input("Certification")
        distance = st.number_input("Distance miles", min_value=0.0, value=0.0)
        submitted = st.form_submit_button("Add lead")
        if submitted:
            if not company_name.strip() or not source_zip.strip():
                st.error("Company name and source ZIP are required.")
            else:
                with session_scope() as session:
                    company = Company(
                        company_name=company_name.strip(),
                        normalized_name=normalized_company_name(company_name),
                        source_zip=source_zip.strip(),
                        gaf_profile_url=gaf_url.strip() or None,
                        company_website=website.strip() or None,
                        phone=phone.strip() or None,
                        certification_level=certification.strip() or None,
                        distance_miles=distance or None,
                        source_type="manual_form",
                    )
                    session.add(company)
                st.success("Lead added. Refresh the page to display it.")
