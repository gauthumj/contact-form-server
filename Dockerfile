FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=4000

WORKDIR /app

# Install build dependencies (kept minimal) and cleanup apt cache
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Create an unprivileged user to run the app
RUN addgroup --system app && adduser --system --ingroup app app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt ./

# Install Python dependencies. If no requirements.txt is present, install a minimal FastAPI stack
RUN python -m pip install --upgrade pip \
    && if [ -s requirements.txt ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    else \
    pip install --no-cache-dir fastapi uvicorn httpx pydantic[email] python-dotenv; \
    fi

# Copy application source
COPY . .

# Ensure files are owned by the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose the port the app listens on
EXPOSE 4000

# Start Uvicorn with the PORT env variable. Using a shell form so ${PORT} is expanded.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --loop auto"]