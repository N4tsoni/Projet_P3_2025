FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configure Poetry
# Don't create a virtual environment inside the container
RUN poetry config virtualenvs.create false

# Copy poetry configuration files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies
# --no-interaction: Don't ask any interactive questions
# --no-ansi: Disable ANSI output
# --no-root: Don't install the project package itself yet
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Install the project package
RUN poetry install --no-interaction --no-ansi

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "src.main"]
