from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from database import SessionLocal
from models import UserToken

default_args = {
    'owner': 'akasha',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=15),
}

def sync_cultural_data():
    """Syncs Spotify, YouTube, and Kindle for all authorized users."""
    db = SessionLocal()
    try:
        tokens = db.query(UserToken).filter(UserToken.provider.in_(["spotify", "google"])).all()
        for token in tokens:
            print(f"Syncing cultural data for user {token.user_id} using {token.provider} token.")
            # Example: SpotifyConnector(token.user_id).sync(db, token.access_token)
    finally:
        db.close()

with DAG(
    'cultural_bulk_sync',
    default_args=default_args,
    description='Bulk sync for Cluster 2 (Cultural Mirror)',
    schedule_interval=timedelta(hours=2),
    catchup=False,
) as dag:

    sync_task = PythonOperator(
        task_id='sync_cultural',
        python_callable=sync_cultural_data,
    )
