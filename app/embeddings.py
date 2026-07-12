"""Text similarity. Uses a dependency-free TF cosine by default; if
sentence-transformers is installed it is used automatically for better results.
Swap in FAISS here when ranking thousands of JDs (see README roadmap)."""
import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-zA-Z0-9+#.]+")

try:  # optional upgrade
    from sentence_transformers import SentenceTransformer, util  # type: ignore
    _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    _HAVE_ST = True
except Exception:
    _HAVE_ST = False


def _tokens(t):
    return [w.lower() for w in _TOKEN.findall(t or "")]


def _cosine_counter(a, b):
    ca, cb = Counter(_tokens(a)), Counter(_tokens(b))
    common = set(ca) & set(cb)
    num = sum(ca[w] * cb[w] for w in common)
    da = math.sqrt(sum(v * v for v in ca.values()))
    db = math.sqrt(sum(v * v for v in cb.values()))
    return num / (da * db) if da and db else 0.0


def similarity(a, b):
    """Cosine similarity in [0, 1], rounded."""
    if _HAVE_ST:
        emb = _MODEL.encode([a or "", b or ""], convert_to_tensor=True)
        return round(float(util.cos_sim(emb[0], emb[1])), 4)
    return round(_cosine_counter(a, b), 4)
