"""Match agent: score a parsed JD against the candidate profile (0-100)."""
from .. import embeddings

_ORDER = {"intern": 0, "junior": 1, "mid": 2, "senior": 3, "lead": 4, "staff": 5, "principal": 6}


def _norm(s):
    return s.strip().lower()


def score_match(jd, profile):
    pskills = set(_norm(s) for s in profile.get("skills", []))
    must = [_norm(s) for s in (jd.get("must_have") or jd.get("skills") or [])]
    nice = [_norm(s) for s in (jd.get("nice_to_have") or [])]
    must_hit = [s for s in must if s in pskills]
    nice_hit = [s for s in nice if s in pskills]
    must_cov = len(must_hit) / len(must) if must else 1.0
    nice_cov = len(nice_hit) / len(nice) if nice else 0.0

    ptext = profile.get("summary", "") + " " + " ".join(profile.get("skills", []))
    jtext = (jd.get("title", "") or "") + " " + " ".join(jd.get("skills", []) or [])
    sim = embeddings.similarity(jtext, ptext)

    pj = _ORDER.get(_norm(profile.get("seniority", "mid")), 2)
    jj = _ORDER.get(_norm(jd.get("seniority", "") or ""), pj)
    sen_fit = max(0.0, 1.0 - abs(pj - jj) * 0.25)

    dealbreakers = []
    prefs = profile.get("preferences", {})
    loc = _norm(jd.get("location", "") or "")
    abroad = not (jd.get("remote") or "india" in loc or loc in {"unspecified", "remote", ""})
    if abroad and prefs.get("needs_visa_sponsorship_outside_india") and jd.get("visa_sponsorship") is False:
        dealbreakers.append("Role is abroad and explicitly offers no visa sponsorship.")

    score = round(100 * (0.5 * must_cov + 0.15 * nice_cov + 0.2 * sim + 0.15 * sen_fit))
    if dealbreakers:
        score = min(score, 40)

    gaps = sorted(set(must) - pskills)
    rationale = (f"Must-have coverage {round(must_cov * 100)}% "
                 f"({len(must_hit)}/{len(must) or 0}); nice-to-have {round(nice_cov * 100)}%; "
                 f"text similarity {sim}; seniority fit {round(sen_fit * 100)}%.")
    return {
        "score": score, "rationale": rationale, "gaps": gaps,
        "matched_skills": sorted(set(must_hit + nice_hit)), "dealbreakers": dealbreakers,
    }
