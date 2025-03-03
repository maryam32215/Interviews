from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook
import requests
from datetime import datetime

class XKCDComicSensor(BaseSensorOperator):
    """
    Sensor to detect when a new XKCD comic is available for the current day.
    """
    
    @apply_defaults
    def __init__(
        self,
        *,
        postgres_conn_id='xkcd_db',  # Custom connection for XKCD database
        **kwargs
    ):
        super().__init__(**kwargs)
        self.postgres_conn_id = postgres_conn_id

    def get_latest_comic_id(self):
        """Get the latest comic ID from the database."""
        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        sql = "SELECT MAX(comic_id) FROM public.comics"  # Explicitly using public schema
        result = pg_hook.get_first(sql)
        return result[0] if result and result[0] is not None else 0

    def fetch_comic(self):
        """Fetch the latest comic data from XKCD API."""
        response = requests.get("https://xkcd.com/info.0.json")
        response.raise_for_status()
        return response.json()

    def is_comic_new(self, comic_data):
        """Check if the comic is new for today."""
        comic_date = datetime(
            int(comic_data['year']),
            int(comic_data['month']),
            int(comic_data['day'])
        )
        return comic_date.date() == datetime.now().date()

    def poke(self, context):
        """
        Function that the sensor calls to determine if it should move forward or not.
        Returns True if a new comic for today is available, False otherwise.
        """
        try:
            latest_known_id = self.get_latest_comic_id()
            comic_data = self.fetch_comic()
            current_id = comic_data['num']

            # Check if this is a new comic for today
            if current_id > latest_known_id:
            # and self.is_comic_new(comic_data):
                self.log.info(f"New comic {current_id} found!")
                context['task_instance'].xcom_push(key='comic_data', value=comic_data)
                return True
                
            self.log.info("No new comic available yet")
            return False

        except Exception as e:
            self.log.error(f"Error checking for new comic: {e}")
            return False