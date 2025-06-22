from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.sensors.filesystem import FileSensor

default_args = {
    'owner': 'kenchu',
    'start_date': datetime(2024, 8, 1),
    'retries': 1,
}

dag = DAG(
    'fundus_example',
    default_args=default_args,
    schedule_interval='*/5 * * * *',  # Runs every 5 minutes
    catchup=False  # Ensures it does not backfill old runs
)

# Task 1: Run the hello world script
run_fundus = BashOperator(
    task_id='run_fundus',
    bash_command='python ~/airflow/data/src/fundus_example.py',
    dag=dag,
)


run_fundus
