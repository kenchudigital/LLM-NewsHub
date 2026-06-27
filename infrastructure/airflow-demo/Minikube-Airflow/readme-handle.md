# Airflow

## How to use?

Find the target pod:

```
kubectl get pods -n airflow
```

Copy the dag file to sceduler

```
kubectl cp dag.py airflow-scheduler-XXXXX:/opt/airflow/dags/ -n airflow
```

