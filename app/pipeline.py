"""End-to-end pipeline: parse -> match -> tailor. Shared by the API and the UI."""
import json
import os

from .agents.parse import parse_jd
from .agents.match import score_match
from .agents.tailor import tailor

_PROFILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "profile.json")


def load_profile(path=None):
    # PROFILE_PATH lets you point at a local, git-ignored real resume (e.g.
    # profile.local.json) while the committed profile.json stays a demo profile.
    resolved = path or os.getenv("PROFILE_PATH") or _PROFILE
    with open(resolved, encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(jd_text, profile=None):
    profile = profile or load_profile()
    parsed = parse_jd(jd_text)
    match = score_match(parsed, profile)
    tail = tailor(parsed, profile)
    return {"parsed": parsed, "match": match, "tailor": tail}
