FROM apache/airflow:2.7.1-python3.9

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
# In docker/airflow.Dockerfile, add:
RUN pip install --no-cache-dir dbt-core dbt-postgres