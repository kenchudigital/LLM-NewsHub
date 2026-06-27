# Airflow Demo

This folder records the Airflow orchestration experiments from the LLM-NewsHub development process.

The current showcase pipeline does not require Airflow. For the main demo, use:

```bash
python pipeline/run.py --date "2025-06-21"
```

Airflow was explored as a possible scheduler/orchestrator for the scraping and data-processing workflow. The scripts and notes here are kept to show the project thinking process, but they are not the canonical production path.

## Contents

```text
infrastructure/airflow-demo/
├── Standalone-Airflow/     # Local Airflow standalone experiment
├── Minikube-Airflow/       # Kubernetes / Minikube Airflow experiment
└── scraper/                # Notebook-based scraper experiments
```

## When To Use This Folder

- Use it if you want to understand how Airflow was evaluated during development.
- Do not use it for the basic GitHub showcase quick start.
- Treat the notebooks as exploratory references; the maintained scraper code lives in `scrapers/`.

## Follow-Up Direction

If this project is converted into a scheduled production workflow, the current `pipeline/run.py` steps can be mapped into Airflow DAG tasks:

```text
scrape -> cards -> cluster -> generate -> media -> migrate -> evaluate
```

