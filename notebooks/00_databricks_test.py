# Databricks notebook source
"""Smoke test for the Databricks Free Edition environment."""

python_result = 2 + 2

rows = [
    (1, "COMBUSTAO"),
    (2, "HIBRIDO"),
    (3, "ELETRICO"),
]

df = spark.createDataFrame(rows, ["id", "tecnologia"])
grouped = df.groupBy("tecnologia").count().orderBy("tecnologia").collect()
groups_result = ",".join(f"{row['tecnologia']}={row['count']}" for row in grouped)

result = (
    f"PYTHON_OK={python_result};"
    f"PYSPARK_OK=rows:{df.count()};groups:{groups_result}"
)

print(result)
dbutils.notebook.exit(result)

