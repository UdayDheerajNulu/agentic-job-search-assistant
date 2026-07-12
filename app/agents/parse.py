"""Parse agent: a job description -> structured fields.
Uses the LLM when configured; otherwise a deterministic heuristic parser."""
import json
import re

from ..skills_vocab import find_skills
from .. import llm

SENIORITY = [
    ("intern", "intern"), ("junior", "junior"), ("entry", "junior"),
    ("principal", "principal"), ("staff", "staff"), ("lead", "lead"),
    ("senior", "senior"), ("sr.", "senior"), ("mid", "mid"),
]
INDIA_CITIES = ["hyderabad", "bengaluru", "bangalore", "pune", "chennai", "mumbai",
                "delhi", "gurugram", "gurgaon", "noida", "kolkata", "india"]


def _heuristic(text):
    low = text.lower()
    skills = find_skills(text)
    req_hits = [low.find(k) for k in ["requirement", "required", "must have", "must-have", "qualifications"] if low.find(k) >= 0]
    req_idx = min(req_hits) if req_hits else -1
    nice_hits = [low.find(k) for k in ["nice to have", "preferred", "bonus", "good to have", "plus"] if low.find(k) >= 0]
    nice_idx = min(nice_hits) if nice_hits else 10 ** 9
    must, nice = [], []
    for s in skills:
        i = low.find(s)
        if i >= nice_idx:
            nice.append(s)
        elif req_idx >= 0 and i >= req_idx:
            must.append(s)
        else:
            must.append(s)
    seniority = "unspecified"
    for kw, lvl in SENIORITY:
        if kw in low:
            seniority = lvl
            break
    remote = any(w in low for w in ["remote", "work from home", "wfh", "distributed"])
    location = next((c.title() for c in INDIA_CITIES if c in low), "Remote" if remote else "Unspecified")
    visa = None
    if any(p in low for p in ["no sponsorship", "not provide sponsorship", "no visa", "without sponsorship"]):
        visa = False
    elif any(p in low for p in ["sponsorship", "visa", "relocation"]):
        visa = True
    comp = None
    m = re.search(r"(\d{1,3})\s*[-to]+\s*(\d{1,3})\s*(?:lpa|lakh)", low)
    if m:
        comp = m.group(0)
    company = "Unknown"
    cm = re.search(r"(?i)\bat\s+([A-Z][A-Za-z0-9&.\- ]{2,40})", text)
    if cm:
        company = cm.group(1).strip()
    first_line = text.strip().splitlines()[0][:80] if text.strip() else "Unknown"
    first_line = re.split(r"\s+\bat\b\s+", first_line)[0]            # drop "... at Company"
    first_line = re.sub(r"\s*[\(\[].*$", "", first_line).strip()      # drop trailing "(Remote, India)"
    tm = re.search(r"(?im)^(?:job title|role|position)\s*[:\-]\s*(.+)$", text)
    title = tm.group(1).strip() if tm else (first_line or "Unknown")
    return {
        "title": title, "company": company, "skills": skills,
        "must_have": sorted(set(must)) or skills, "nice_to_have": sorted(set(nice)),
        "seniority": seniority, "location": location, "remote": remote,
        "visa_sponsorship": visa, "comp": comp,
    }


def parse_jd(text):
    out = llm.chat(
        system="You extract structured data from a job description. Reply with ONLY a JSON object.",
        user=("Extract this JSON: {title, company, must_have (list of skills), "
              "nice_to_have (list of skills), seniority, location, remote (bool), "
              "visa_sponsorship (bool or null), comp (string or null)} from:\n\n" + text),
        json_mode=True,
    )
    if out:
        try:
            data = json.loads(out)
            data.setdefault("skills", sorted(set((data.get("must_have") or []) + (data.get("nice_to_have") or []))))
            return data
        except Exception:
            pass
    return _heuristic(text)
