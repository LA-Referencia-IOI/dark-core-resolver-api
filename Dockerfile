FROM python:3.10-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY dark-core-resolver-api/requirements.txt /tmp/requirements.txt
COPY dark-core-lib /tmp/dark-core-lib
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir /tmp/dark-core-lib

COPY dark-core-resolver-api/app/ ./app/

RUN useradd -m appuser \
    && chown -R appuser:appuser /app

EXPOSE 8002

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
