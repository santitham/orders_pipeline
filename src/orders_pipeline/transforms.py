"""Pure, testable transforms for the orders pipeline.

These functions take and return Spark DataFrames and do NO I/O — that is what
makes them fast and deterministic to unit-test. Reading from Kafka/Delta and
writing to tables happens in the job entrypoint (see notebooks/build_gold.py),
NOT here.
"""
from pyspark.sql import DataFrame, functions as F

# Default unit price used to turn order units into revenue.
PRICE = 9.99


def add_revenue(df: DataFrame, price: float = PRICE) -> DataFrame:
    """Add a ``revenue`` column = orderunits * price (rounded to 2 dp)."""
    return df.withColumn("revenue", F.round(F.col("orderunits") * price, 2))


def enrich_category(orders: DataFrame, items: DataFrame) -> DataFrame:
    """Left-join the item -> category lookup onto the orders."""
    return orders.join(items, "itemid", "left")


def revenue_by_category(orders: DataFrame, items: DataFrame,
                        price: float = PRICE) -> DataFrame:
    """Business 'gold' result: revenue + order count per category."""
    return (enrich_category(add_revenue(orders, price), items)
            .groupBy("category")
            .agg(F.sum("revenue").alias("revenue"),
                 F.count("*").alias("orders")))
