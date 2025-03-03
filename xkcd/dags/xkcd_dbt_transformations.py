from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 22),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'xkcd_dbt_transformations',
    default_args=default_args,
    description='Run dbt transformations for XKCD data',
    schedule_interval='0 6 * * 1,3,5',  # Run at 6:00 AM on Monday, Wednesday, and Friday
    catchup=False
)

# Set environment variables
env_vars = {
    'DBT_DISABLE_VERSION_CHECK': 'true',
    'DBT_NO_DEPRECATIONS_WARN': 'true',
    'DBT_DEBUG': 'true',
    'PATH': '/home/airflow/.local/bin:${PATH}'  # Add the dbt path to PATH
}

# Install dbt and save path
install_dbt = BashOperator(
    task_id='install_dbt',
    bash_command='pip install --no-cache-dir dbt-core dbt-postgres && echo "dbt installed at: $(which dbt)"',
    dag=dag
)

# Run dbt debug using full path
dbt_debug = BashOperator(
    task_id='dbt_debug',
    bash_command='cd /opt/dbt && /home/airflow/.local/bin/dbt debug --no-use-colors',
    env=env_vars,
    dag=dag
)

# Run dbt tests to check source data
dbt_test_source = BashOperator(
    task_id='dbt_test_source',
    bash_command='cd /opt/dbt && /home/airflow/.local/bin/dbt test --select source:* --no-use-colors',
    env=env_vars,
    dag=dag
)

# Run dbt models
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/dbt && /home/airflow/.local/bin/dbt run --no-use-colors',
    env=env_vars,
    dag=dag
)

# Run dbt tests on models
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /opt/dbt && /home/airflow/.local/bin/dbt test --exclude source:* --no-use-colors',
    env=env_vars,
    dag=dag
)

# Set dependencies
install_dbt >> dbt_debug >> dbt_test_source >> dbt_run >> dbt_test