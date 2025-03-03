#!/bin/bash
set -e

# Install dbt if not already installed
pip install --no-cache-dir dbt-core dbt-postgres

# Navigate to the dbt project directory
cd /opt/dbt

# Run dbt commands or keep container running
if [ "$1" = "debug" ]; then
    dbt debug
elif [ "$1" = "run" ]; then
    dbt run
elif [ "$1" = "test" ]; then
    dbt test
else
    # Default to keeping the container running
    exec tail -f /dev/null
fi