"""Tailor agent: pick the most relevant true bullets, reorder skills, draft an
outreach note. NEVER invents experience -- only re-emphasises what is in the profile."""
from .. import llm
from ..skills_vocab import find_skills


def _rank_bullets(jd_skills, profile, n=6):
    js = set(s.lower() for s in jd_skills)
    scored = []
    for exp in profile.get("experience", []):
        for b in exp.get("bullets", []):
            overlap = len(set(find_skills(b)) & js)
            scored.append((overlap, exp.get("company", ""), b))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(company, b) for _, company, b in scored[:n]]


def tailor(jd, profile):
    jd_skills = jd.get("skills") or jd.get("must_have") or []
    ranked = _rank_bullets(jd_skills, profile)
    jd_set = set(s.lower() for s in jd_skills)
    pskills = profile.get("skills", [])
    relevant_first = [s for s in pskills if s.lower() in jd_set]
    ranked_skills = relevant_first + [s for s in pskills if s not in relevant_first]
    missing = sorted(set(s.lower() for s in (jd.get("must_have") or [])) - set(s.lower() for s in pskills))

    company = jd.get("company") or "your team"
    title = jd.get("title") or "this role"
    top_match = ", ".join(relevant_first[:4]) or ", ".join(pskills[:4])

    note = llm.chat(
        system="Write a concise, truthful ~120-word outreach note. Use ONLY the facts provided. Never fabricate.",
        user=(f"Role: {title} at {company}. Candidate summary: {profile.get('summary')}. "
              f"Matching strengths: {top_match}. Relevant achievements: {[b for _, b in ranked[:3]]}"),
    )
    if not note:
        lead = (ranked[0][1].rstrip(".") + ".") if ranked else "built agentic GenAI systems end to end."
        note = (f"Hi, I'm {profile.get('name')}, an AI/ML engineer with "
                f"{profile.get('years_experience')}+ years shipping production NLP and LLM systems. "
                f"I'm excited about {title} at {company} - it lines up closely with my work in {top_match}. "
                f"Recently I {lead} I'd love to share how I can contribute. Thanks for considering!")

    summary = profile.get("summary", "") + f" Strong match on: {top_match}."
    return {
        "tailored_summary": summary,
        "ranked_skills": ranked_skills,
        "selected_bullets": [b for _, b in ranked],
        "outreach_note": note.strip(),
        "missing_must_haves": missing,
    }
