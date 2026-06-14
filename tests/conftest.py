"""Shared pytest fixtures. A single local SparkSession is reused across tests."""
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    spark = (SparkSession.builder
             .master("local[2]")
             .appName("orders-pipeline-tests")
             .config("spark.sql.shuffle.partitions", "2")
             .getOrCreate())
    yield spark
    spark.stop()
