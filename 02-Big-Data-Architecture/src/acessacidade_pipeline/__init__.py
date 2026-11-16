"""AcessaCidade — pipeline de dados (disciplina Big Data Architecture & Data Integration).

ELT com DuckDB em camadas raw -> bronze -> silver -> gold, orquestrado pelo Airflow
(dags/acessacidade_elt_pipeline.py) ou pelo runner local (python -m acessacidade_pipeline).
"""
__version__ = "1.0.0"

__all__ = ["__version__"]
