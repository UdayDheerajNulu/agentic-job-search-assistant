# Agentic Job-Search Assistant

**🔗 Live demo:** https://agentic-job-search-assistant-wokmvixurxkpkx8jvjop5a.streamlit.app/

An agentic job-search assistant that parses job descriptions, scores fit against your profile, tailors your resume bullets, and drafts outreach notes. It is designed as a portfolio project that demonstrates parsing, matching, tailoring, embeddings, and a small FastAPI + Streamlit workflow.

## What it does

- Parses a job description into structured fields
- Scores how well your profile matches the role
- Tailors resume bullets to the job
- Drafts a short outreach note for the recruiter
- Stores progress in a simple SQLite tracker

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the tests:

```bash
python tests/test_agents.py
```

Start the UI:

```bash
streamlit run app/ui/streamlit_app.py
```

Or start the API:

```bash
uvicorn app.api.main:app --reload
```

## Configuration

Edit [profile.json](profile.json) to update your skills, bullets, and preferences.

## Notes

This project runs in heuristic mode by default and can optionally use an LLM provider for higher-quality parsing and tailoring.

## Important

Please respect job-board rules and use this tool as a human-in-the-loop assistant rather than an automated scraping or applying system.
