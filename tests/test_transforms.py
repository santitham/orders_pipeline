"""Unit + schema tests for the pure transforms (pytest + chispa)."""
from chispa import assert_df_equality
from orders_pipeline.transforms import add_revenue, revenue_by_category

ORDERS_SCHEMA = "orderid long, itemid string, orderunits double"


def test_add_revenue(spark):
    inp = spark.createDataFrame([(1, "Item_5", 2.0)], ORDERS_SCHEMA)
    got = add_revenue(inp, price=10.0)
    exp = spark.createDataFrame(
        [(1, "Item_5", 2.0, 20.0)],
        "orderid long, itemid string, orderunits double, revenue double")
    assert_df_equality(got, exp)


def test_add_revenue_schema(spark):
    """Schema-validation test: catches drift before it reaches production."""
    got = add_revenue(spark.createDataFrame([(1, "Item_5", 2.0)], ORDERS_SCHEMA))
    assert [f.name for f in got.schema.fields] == \
        ["orderid", "itemid", "orderunits", "revenue"]


def test_revenue_by_category(spark):
    orders = spark.createDataFrame(
        [(1, "Item_1", 2.0), (2, "Item_2", 1.0)], ORDERS_SCHEMA)
    items = spark.createDataFrame(
        [("Item_1", "A"), ("Item_2", "A")], "itemid string, category string")
    got = revenue_by_category(orders, items, price=10.0)
    assert got.count() == 1
    row = got.first()
    assert row["category"] == "A"
    assert row["orders"] == 2
    assert row["revenue"] == 30.0   # (2.0 + 1.0) * 10.0
