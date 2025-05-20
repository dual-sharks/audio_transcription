FROM python:3.11-slim

# 1. copy the dependency files into the WORKDIR -----------------------
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# 2. system deps ------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 3. Poetry & deps ----------------------------------------------------
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi

# 4. copy the rest of the service code (cache-friendly) --------------
COPY whisper_service/ .

CMD ["poetry", "run", "python", "main.py"]