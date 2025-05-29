FROM python:3.11-slim

# 1. copy the dependency files into the WORKDIR -----------------------
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# 3. Poetry & deps ----------------------------------------------------
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi

# Copy application code
COPY app/ .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "python", "main.py"] 