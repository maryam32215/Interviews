from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
from xkcd_sensor import XKCDComicSensor

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 22),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG - Start early in the day
dag = DAG(
    'xkcd_comic_datalake',
    default_args=default_args,
    description='Fetches new XKCD comics on M/W/F using a custom sensor',
    schedule_interval='0 5 * * 1,3,5',  # Run at 5:00 AM on Monday, Wednesday, and Friday
    catchup=False
)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS comics (
    comic_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    img TEXT NOT NULL,
    alt_text TEXT,
    publish_date DATE NOT NULL,
    transcript TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def save_comic(**context):
    """Save comic data to database using PostgreSQL."""
    # Get comic data from XCom
    task_instance = context['task_instance']
    comic_data = task_instance.xcom_pull(task_ids='wait_for_comic', key='comic_data')
    
    if not comic_data:
        raise ValueError("No comic data available in XCom")

    pg_hook = PostgresHook(postgres_conn_id='xkcd_db')
    
    insert_sql = """
        INSERT INTO comics 
        (comic_id, title, img, alt_text, publish_date, transcript, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (comic_id) 
        DO UPDATE SET 
            title = EXCLUDED.title,
            img = EXCLUDED.img,
            alt_text = EXCLUDED.alt_text,
            publish_date = EXCLUDED.publish_date,
            transcript = EXCLUDED.transcript,
            updated_at = CURRENT_TIMESTAMP;
    """
    
    values = (
        comic_data['num'],
        comic_data['title'],
        comic_data['img'],
        comic_data['alt'],
        f"{comic_data['year']}-{comic_data['month']}-{comic_data['day']}",
        comic_data.get('transcript', '')
    )
    
    
    pg_hook.run(insert_sql, parameters=values)

# Define tasks
setup_table = PostgresOperator(
    task_id='setup_table',
    postgres_conn_id='xkcd_db',
    sql=CREATE_TABLE_SQL,
    dag=dag
)

# Custom sensor task
wait_for_comic = XKCDComicSensor(
    task_id='wait_for_comic',
    postgres_conn_id='xkcd_db',
    poke_interval=300,  # Check every 5 minutes
    timeout=21600,      # Time out after 6 hours (in seconds)
    mode='poke',       # Use 'reschedule' mode to free up slots between checks
    soft_fail=True,    # Don't fail the task if we timeout
    dag=dag
)

save_comic_task = PythonOperator(
    task_id='save_comic',
    python_callable=save_comic,
    provide_context=True,
    dag=dag
)

# Set task dependencies
setup_table >> wait_for_comic >> save_comic_task