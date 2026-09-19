# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download the Hugging Face sentence-transformers model weights during build step
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/torch/sentence_transformers
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')"

# Stage 2: Production Runtime
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python dependencies and pre-downloaded model weights
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache /root/.cache

# Setup environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data \
    ALLOWED_ORIGINS="*" \
    EMBEDDING_BATCH_SIZE=16 \
    SENTENCE_TRANSFORMERS_HOME=/root/.cache/torch/sentence_transformers

# Support persistent volume mount
VOLUME ["/app/data"]

# Copy application source code
COPY app/ ./app/
COPY seed_data.py ./

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').getcode()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
