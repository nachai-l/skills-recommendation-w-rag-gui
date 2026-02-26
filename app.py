from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from functions.core.api_client import ApiError, RecommendRequest, recommend_skills
from functions.core.state import AppState, add_selected, remove_selected, selected_list
from functions.core.export import build_export_rows, export_csv_bytes, export_xlsx_bytes
from functions.utils.config import load_config
from functions.utils.text import evidence_to_display, truncate


@st.cache_resource
def _cfg():
    return load_config()


def _init_state() -> AppState:
    if "app_state" not in st.session_state:
        st.session_state["app_state"] = AppState()
    return st.session_state["app_state"]


def _results_df(results, preview_chars: int):
    rows = []
    for s in results:
        rows.append(
            {
                "skill_id": s.get("skill_id", ""),
                "skill_name": s.get("skill_name", ""),
                "relevance_score": s.get("relevance_score", 0.0),
                "source": s.get("source", ""),
                "preview": truncate(s.get("skill_text", "") or "", preview_chars),
            }
        )
    return pd.DataFrame(rows)


def main():
    cfg = _cfg()
    st.set_page_config(page_title=cfg.ui.page_title, page_icon=cfg.ui.page_icon, layout="wide")

    state = _init_state()

    st.title(cfg.ui.page_title)

    # --- Sidebar controls ---
    with st.sidebar:
        st.subheader("API")
        st.caption(cfg.api.base_url)

        st.subheader("Request settings")
        top_k = st.slider("top_k", min_value=1, max_value=100, value=int(cfg.defaults.top_k))
        top_k_vector = st.slider("top_k_vector", min_value=1, max_value=200, value=int(cfg.defaults.top_k_vector))
        top_k_bm25 = st.slider("top_k_bm25", min_value=1, max_value=200, value=int(cfg.defaults.top_k_bm25))
        require_judge_pass = st.toggle("require_judge_pass", value=bool(cfg.defaults.require_judge_pass))
        require_all_meta = st.toggle("require_all_meta", value=bool(cfg.defaults.require_all_meta))
        debug = st.toggle("debug", value=bool(cfg.defaults.debug))

        st.divider()
        st.subheader("Selected Skills")
        st.write(f"{len(state.selected)} selected")
        if st.button("Clear selected", use_container_width=True):
            state.selected = {}

    # --- Main search input ---
    # Use st.form so that pressing Enter in the text box submits the search
    # (without a form, Enter reruns the app but st.button stays False, causing
    # the user to have to submit twice).
    with st.form("search_form"):
        query = st.text_input(
            "Query",
            value=state.last_query,
            placeholder="e.g., data scientist / PCR / account executive",
        )
        submitted = st.form_submit_button("Search", type="primary")

    if submitted:
        q = (query or "").strip()
        if not q:
            st.error("Query cannot be empty.")
        else:
            req = RecommendRequest(
                query=q,
                top_k=top_k,
                debug=debug,
                require_judge_pass=require_judge_pass,
                top_k_vector=top_k_vector,
                top_k_bm25=top_k_bm25,
                require_all_meta=require_all_meta,
            )
            try:
                resp = recommend_skills(cfg.api, req)
                payload = resp.get("payload") or {}
                meta = resp.get("meta") or {}

                state.last_query = payload.get("query", q)
                state.generation_cache_id = (meta.get("generation_cache_id") or "") if isinstance(meta, dict) else ""
                state.last_results = payload.get("recommended_skills") or []

                st.success(f"Got {len(state.last_results)} skills.")
            except ApiError as e:
                st.error(str(e))
                if e.detail is not None:
                    st.code(json.dumps(e.detail, ensure_ascii=False, indent=2))
            except Exception as e:
                st.error("Unexpected error")
                st.exception(e)

    colA, colB = st.columns([1, 2], gap="large")

    with colA:
        # show analysis summary
        if state.last_results:
            st.subheader("Analysis summary")
            st.caption("Tip: click a row on the right to see details, then add to selected.")

    with colB:
        st.subheader("Results")
        if not state.last_results:
            st.info("No results yet. Enter a query and click Search.")
        else:
            df = _results_df(state.last_results, cfg.ui.preview_chars)
            df = df.head(cfg.ui.max_display_rows)

            st.dataframe(
                df[["skill_name", "relevance_score", "source", "preview"]],
                use_container_width=True,
                hide_index=True,
            )

            # select a skill to view details
            options = {f"{row['skill_name']} ({row['source']}, {row['relevance_score']:.2f})": row["skill_id"] for _, row in df.iterrows()}
            selected_label = st.selectbox("Select a skill to view details", options=list(options.keys()))
            selected_skill_id = options[selected_label]

            # find full object
            skill_obj = next((s for s in state.last_results if str(s.get("skill_id")) == str(selected_skill_id)), None)
            if skill_obj:
                st.markdown("### Details")
                st.write("**Skill name:**", skill_obj.get("skill_name", ""))
                st.write("**Skill id:**", skill_obj.get("skill_id", ""))
                st.write("**Source:**", skill_obj.get("source", ""))
                st.write("**Score:**", skill_obj.get("relevance_score", ""))

                st.markdown("**Skill text**")
                st.write(skill_obj.get("skill_text", ""))

                st.markdown("**Reasoning**")
                st.write(skill_obj.get("reasoning", ""))

                st.markdown("**Evidence**")
                st.write(evidence_to_display(skill_obj.get("evidence")))

                with st.expander("Criteria"):
                    st.markdown("**Foundational**")
                    st.write(skill_obj.get("Foundational_Criteria", ""))
                    st.markdown("**Intermediate**")
                    st.write(skill_obj.get("Intermediate_Criteria", ""))
                    st.markdown("**Advanced**")
                    st.write(skill_obj.get("Advanced_Criteria", ""))

                if st.button("Add to Selected Skills", use_container_width=True):
                    add_selected(state, skill_obj)
                    st.success("Added (deduped by skill_id).")

    # --- Selected section + export ---
    st.divider()
    st.subheader("Selected Skills")

    sel = selected_list(state)
    if not sel:
        st.info("No selected skills yet.")
        return

    sel_df = _results_df(sel, cfg.ui.preview_chars)
    st.dataframe(sel_df[["skill_name", "relevance_score", "source", "preview"]], use_container_width=True, hide_index=True)

    # remove control
    rm_options = {f"{s.get('skill_name','')} ({s.get('source','')})": s.get("skill_id", "") for s in sel}
    rm_label = st.selectbox("Remove a selected skill", options=["(none)"] + list(rm_options.keys()))
    if rm_label != "(none)":
        if st.button("Remove", use_container_width=True):
            remove_selected(state, rm_options[rm_label])
            st.success("Removed.")

    # exports
    export_rows = build_export_rows(
        selected_skills=sel,
        query=state.last_query,
        generation_cache_id=state.generation_cache_id,
        evidence_mode="pipe",
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"selected_skills_{ts}"

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download CSV",
            data=export_csv_bytes(export_rows),
            file_name=f"{base}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "Download XLSX",
            data=export_xlsx_bytes(export_rows),
            file_name=f"{base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.caption(f"Query: {state.last_query} | generation_cache_id: {state.generation_cache_id}")


if __name__ == "__main__":
    main()