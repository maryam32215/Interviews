FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dbt
RUN pip install --no-cache-dir \
    dbt-core \
    dbt-postgres

# Copy entrypoint script
COPY docker/dbt-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set working directory
WORKDIR /opt/dbt

# Create necessary directories
RUN mkdir -p models macros seeds

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]