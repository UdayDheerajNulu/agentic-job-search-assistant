"""Canonical skill vocabulary + a simple, dependency-free skill extractor."""
import re

CANONICAL = [
    "python", "java", "c++", "c", "sql", "powershell", "go", "scala", "r",
    "nlp", "scikit-learn", "tfidf", "tf-idf", "shap", "linearsvc", "gridsearchcv",
    "machine learning", "deep learning", "pytorch", "tensorflow", "transformers",
    "llm", "llms", "agentic ai", "agents", "langchain", "langgraph", "llamaindex",
    "prompt engineering", "rag", "fine-tuning", "embeddings", "vector database",
    "faiss", "pinecone", "chroma", "pgvector",
    "fastapi", "flask", "django", "sqlalchemy", "streamlit", "react", "node",
    "docker", "kubernetes", "aws", "gcp", "azure", "mlops", "ci/cd", "git",
    "jira", "sonarqube", "autosys", "gemini", "openai", "anthropic", "huggingface",
    "spark", "airflow", "kafka", "statistics", "a/b testing", "experimentation",
]


def find_skills(text):
    """Return the sorted set of canonical skills mentioned in text (word-boundary match)."""
    t = " " + (text or "").lower() + " "
    found = []
    for s in CANONICAL:
        pat = r"(?<![a-z0-9])" + re.escape(s.lower()) + r"(?![a-z0-9])"
        if re.search(pat, t):
            found.append(s)
    return sorted(set(found))
