FROM python:3.11-slim

WORKDIR /app

# Copy from backend subdirectory (context is repo root on Render)
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir .
RUN playwright install chromium

COPY backend/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
