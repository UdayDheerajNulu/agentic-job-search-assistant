FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Streamlit UI (8501) and FastAPI (8000)
EXPOSE 8501 8000

# Default: run the Streamlit UI. Override CMD to run the API instead:
#   docker run -p 8000:8000 job-search-assistant uvicorn app.api.main:app --host 0.0.0.0 --port 8000
CMD ["streamlit", "run", "app/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
