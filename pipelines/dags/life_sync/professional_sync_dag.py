from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from database import SessionLocal
from models import UserToken

default_args = {
    'owner': 'akasha',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def sync_professional_data():
    """Syncs GitHub, Gmail, and Jira for all authorized users."""
    db = SessionLocal()
    try:
        tokens = db.query(UserToken).filter(UserToken.provider.in_(["github", "google"])).all()
        for token in tokens:
            print(f"Syncing professional data for user {token.user_id} using {token.provider} token.")
            # In a real impl, call the respective connector.sync() method
            # Example: GitHubConnector(token.user_id).sync(db, token.access_token)
    finally:
        db.close()

with DAG(
    'professional_bulk_sync',
    default_args=default_args,
    description='Bulk sync for Cluster 1 (Professional Brain)',
    schedule_interval=timedelta(hours=6),
    catchup=False,
) as dag:

    sync_task = PythonOperator(
        task_id='sync_professional',
        python_callable=sync_professional_data,
    )
