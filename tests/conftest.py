"""Shared pytest fixtures — one SparkSession is reused across the whole test session.

Portable on purpose: the same tests run in two very different places.
* GitHub CI / a laptop  -> no Spark is running, so build a small local one (local[2]).
* A Databricks cluster  -> a Spark session already exists (and on shared/Spark-Connect
  clusters you're not allowed to build another), so reuse it.

SparkSession.getActiveSession() is the switch: it returns the running session on
Databricks (reuse) and None in CI (build a local one).
"""
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    active = SparkSession.getActiveSession()
    if active is not None:
        # Databricks: reuse the cluster's session; don't stop it (we don't own it).
        yield active
        return
    # CI / local: no session yet, so create a lightweight local one and clean it up.
    session = (SparkSession.builder
               .master("local[2]")
               .appName("orders-pipeline-tests")
               .config("spark.sql.shuffle.partitions", "2")
               .getOrCreate())
    yield session
    session.stop()
