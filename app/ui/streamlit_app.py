"""Streamlit UI. Run from the project root: streamlit run app/ui/streamlit_app.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st  # noqa: E402

from app.pipeline import run_pipeline, load_profile  # noqa: E402
from app import db  # noqa: E402

st.set_page_config(page_title="Job-Search Assistant", layout="wide")
st.title("Agentic Job-Search Assistant")
st.caption("Demo uses a sample profile. Paste any job description to see it parse → score → tailor.")
profile = load_profile()

_SAMPLE_JD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample_jd.txt"
)


def _sample_jd():
    try:
        with open(_SAMPLE_JD_PATH, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""

tab_analyze, tab_tracker = st.tabs(["Analyze a JD", "Tracker"])

with tab_analyze:
    jd_text = st.text_area("Paste a job description", value=_sample_jd(), height=260)
    if st.button("Analyze", type="primary") and jd_text.strip():
        st.session_state["res"] = run_pipeline(jd_text, profile)
        st.session_state["jd"] = jd_text

    res = st.session_state.get("res")
    if res:
        p, m, t = res["parsed"], res["match"], res["tailor"]
        st.metric("Fit score", f"{m['score']}/100")
        st.caption(m["rationale"])
        if m["dealbreakers"]:
            st.error(" / ".join(m["dealbreakers"]))
        left, right = st.columns(2)
        with left:
            st.subheader("Parsed JD")
            st.json(p)
            if m["gaps"]:
                st.warning("Missing must-haves: " + ", ".join(m["gaps"]))
        with right:
            st.subheader("Tailored resume bullets")
            for b in t["selected_bullets"]:
                st.write("- " + b)
            st.subheader("Skills (reordered for this JD)")
            st.write(", ".join(t["ranked_skills"]))
            st.subheader("Outreach note (review before sending)")
            st.write(t["outreach_note"])
        if st.button("Save to tracker"):
            db.add_job({"title": p["title"], "company": p["company"], "location": p.get("location"),
                        "score": m["score"], "jd_text": st.session_state.get("jd"), "status": "saved"})
            st.success("Saved to tracker.")

with tab_tracker:
    rows = db.list_jobs()
    st.write(f"{len(rows)} saved role(s)")
    for r in rows:
        c1, c2, c3 = st.columns([5, 2, 3])
        c1.write(f"**{r['title']}** - {r['company']} ({r.get('location') or '-'})")
        c2.write(f"score {r['score']}")
        idx = db.STATUSES.index(r["status"]) if r["status"] in db.STATUSES else 0
        new = c3.selectbox("status", db.STATUSES, index=idx, key=f"st{r['id']}", label_visibility="collapsed")
        if new != r["status"]:
            db.update_status(r["id"], new)
