"""FastAPI service. Run: uvicorn app.api.main:app --reload"""
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .. import db
from ..pipeline import run_pipeline, load_profile

app = FastAPI(title="Agentic Job-Search Assistant")
profile = load_profile()


class JD(BaseModel):
    jd_text: str
    source: Optional[str] = None
    url: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


@app.post("/analyze")
def analyze(jd: JD):
    return run_pipeline(jd.jd_text, profile)


@app.post("/jobs")
def save_job(jd: JD):
    res = run_pipeline(jd.jd_text, profile)
    p, m = res["parsed"], res["match"]
    job_id = db.add_job({
        "title": p.get("title"), "company": p.get("company"), "location": p.get("location"),
        "score": m.get("score"), "source": jd.source, "url": jd.url, "jd_text": jd.jd_text,
        "status": "saved",
    })
    return {"id": job_id, **res}


@app.get("/jobs")
def jobs():
    return db.list_jobs()


@app.patch("/jobs/{job_id}")
def patch(job_id: int, s: StatusUpdate):
    db.update_status(job_id, s.status)
    return {"ok": True}
