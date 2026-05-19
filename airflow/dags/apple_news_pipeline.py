"""Airflow DAGs for the Apple News Intelligence Platform."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "data-platform",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

PROJECT_DIR = "/opt/airflow/project"


def make_pipeline_dag(dag_id: str, schedule: str, command: str, tags: list[str]) -> DAG:
    with DAG(
        dag_id=dag_id,
        default_args=DEFAULT_ARGS,
        description=f"{dag_id} for Apple news intelligence",
        schedule=schedule,
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=tags,
    ) as dag:
        BashOperator(
            task_id="run_task",
            bash_command=f"cd {PROJECT_DIR} && PYTHONPATH={PROJECT_DIR} {command}",
        )
    return dag


ingest_news_daily = make_pipeline_dag(
    "ingest_news_daily",
    "@daily",
    "python scripts/run_pipeline_once.py",
    ["ingestion", "news", "gdelt", "rss"],
)

ingest_social_hourly = make_pipeline_dag(
    "ingest_social_hourly",
    "@hourly",
    "python scripts/run_pipeline_once.py",
    ["ingestion", "social", "reddit", "twitter"],
)

process_bronze_to_silver = make_pipeline_dag(
    "process_bronze_to_silver",
    "0 * * * *",
    "SKIP_GRAPH_LOAD=true SKIP_VECTOR_INDEX=true python scripts/run_pipeline_once.py",
    ["processing", "silver"],
)

build_gold_metrics = make_pipeline_dag(
    "build_gold_metrics",
    "15 * * * *",
    "SKIP_GRAPH_LOAD=true SKIP_VECTOR_INDEX=true python scripts/run_pipeline_once.py",
    ["analytics", "gold"],
)

update_neo4j_graph = make_pipeline_dag(
    "update_neo4j_graph",
    "30 * * * *",
    "SKIP_VECTOR_INDEX=true python scripts/run_pipeline_once.py",
    ["neo4j", "graph"],
)

update_qdrant_embeddings = make_pipeline_dag(
    "update_qdrant_embeddings",
    "45 * * * *",
    "SKIP_GRAPH_LOAD=true python scripts/run_pipeline_once.py",
    ["qdrant", "embeddings"],
)

calculate_trends = make_pipeline_dag(
    "calculate_trends",
    "*/30 * * * *",
    "SKIP_GRAPH_LOAD=true SKIP_VECTOR_INDEX=true python scripts/run_pipeline_once.py",
    ["trends"],
)
