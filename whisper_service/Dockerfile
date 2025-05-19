# ──────────────────────────────────────────────────────────────
# whisper_service/Dockerfile
# ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

# 1. System-level libs first (ffmpeg for Whisper)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 2. Create workdir
WORKDIR /app

# 3. Install Poetry (latest)
RUN pip install --no-cache-dir poetry

# 4. Copy only the dependency manifests *first* so that
#    Docker can re-use this layer when source code changes
COPY pyproject.toml poetry.lock* ./

# 5. Tell Poetry to install into the system site-packages
RUN poetry config virtualenvs.create false

# 6. Install **production-only** deps
#    (new syntax ― replace --no-dev)
RUN poetry install --only main --no-interaction --no-ansi --no-root

# 7. Copy the actual application code
COPY . .

# 8. Expose the FastAPI port (purely documentary)
EXPOSE 8000

# 9. Start the service via Poetry-managed entry
CMD ["poetry", "run", "python", "main.py"]