"""Stdlib-only tests for the core agents (no API key, no network)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipeline import run_pipeline, load_profile  # noqa: E402
from app.agents.parse import parse_jd  # noqa: E402
from app.agents.match import score_match  # noqa: E402
from app.agents.tailor import tailor  # noqa: E402
from app import db  # noqa: E402

SAMPLE = """Senior GenAI Engineer at Acme AI
We are hiring a Senior GenAI Engineer (remote, India).
Required: Python, LangChain, RAG, FastAPI, vector database, LLMs, prompt engineering.
Nice to have: Kubernetes, AWS.
Visa sponsorship available."""


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.p = load_profile()

    def test_parse_extracts_skills(self):
        jd = parse_jd(SAMPLE)
        low = [s.lower() for s in jd["skills"]]
        self.assertIn("rag", low)
        self.assertIn("langchain", low)
        self.assertIn("fastapi", low)

    def test_score_in_range_and_strong(self):
        m = score_match(parse_jd(SAMPLE), self.p)
        self.assertTrue(0 <= m["score"] <= 100)
        self.assertGreater(m["score"], 40)  # profile matches all must-haves

    def test_match_detects_gap(self):
        m = score_match(parse_jd("ML Engineer. Required: Python, Kubernetes, Spark, MLOps."), self.p)
        self.assertIn("kubernetes", m["gaps"])

    def test_tailor_never_fabricates(self):
        t = tailor(parse_jd(SAMPLE), self.p)
        pskills = set(s.lower() for s in self.p["skills"])
        for s in t["ranked_skills"]:
            self.assertIn(s.lower(), pskills)

    def test_db_roundtrip(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            jid = db.add_job({"title": "X", "company": "Y", "score": 50}, path=path)
            self.assertEqual(len(db.list_jobs(path=path)), 1)
            db.update_status(jid, "applied", path=path)
            self.assertEqual(db.list_jobs(path=path)[0]["status"], "applied")
        finally:
            os.remove(path)

    def test_pipeline_keys(self):
        res = run_pipeline(SAMPLE, self.p)
        self.assertEqual(set(res), {"parsed", "match", "tailor"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
