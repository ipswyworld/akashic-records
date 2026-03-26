from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

default_args = {
    'owner': 'akasha',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def sync_arxiv_daily():
    print("Initiating daily ArXiv sync...")
    # In a real environment, we'd trigger the FastAPI endpoint or call the Akasha backend modules directly
    # requests.post("http://backend:8001/sync/arxiv", json={"query": "AI Agents"})
    print("Sync complete.")

with DAG(
    'arxiv_daily_sync',
    default_args=default_args,
    description='A simple DAG to sync ArXiv papers daily',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    sync_task = PythonOperator(
        task_id='sync_arxiv',
        python_callable=sync_arxiv_daily,
    )

    sync_task
