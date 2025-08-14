
FROM python:3.10-slim as builder

WORKDIR /code
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv && \
    uv pip install -e .

# 🚀 Runtime
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    PATH="/venv/bin:$PATH"

WORKDIR /code

COPY --from=builder /venv /venv
COPY --chown=1000:1000 . .

RUN apt-get update && apt-get install -y curl && \
    pip install uvicorn && \
    mkdir -p /code/logs && \
    useradd -m appuser && \
    chown -R appuser /code

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]