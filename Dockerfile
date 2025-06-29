
# Build stage
FROM ubuntu:22.04 AS builder

WORKDIR /app

# Install Python and build dependencies (including PostgreSQL dev libraries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python3 -m venv venv1 && \
    . venv1/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM ubuntu:22.04 AS production

WORKDIR /app

# Install only runtime dependencies (including PostgreSQL client libraries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    libpq5 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /app/venv1 /app/venv1

# Copy application code
COPY . /app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["/bin/bash", "-c", "source venv1/bin/activate && python manage.py migrate && python manage.py createsuperuser --noinput && python manage.py runserver 0.0.0.0:8000"]
