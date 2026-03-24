FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY components/services/dark-core-resolver-api/requirements.txt /tmp/requirements.txt
COPY components/core/dark-core-lib /tmp/dark-core-lib
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir /tmp/dark-core-lib

COPY components/services/dark-core-resolver-api/app/ ./app/

RUN useradd -m appuser \
    && chown -R appuser:appuser /app

EXPOSE 8003

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
