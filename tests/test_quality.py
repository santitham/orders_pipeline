"""Data-quality tests: the quarantine split and the CI gate summary."""
from orders_pipeline.quality import split, summary

ORDERS_SCHEMA = "orderid long, itemid string, orderunits double"


def test_split_quarantines_bad_rows(spark):
    df = spark.createDataFrame([
        (1, "Item_1", 2.0),       # good
        (2, "Item_2", 1.5),       # good
        (None, "Item_3", 1.0),    # bad: null orderid
        (4, "Item_4", -3.0),      # bad: negative units
    ], ORDERS_SCHEMA)
    valid, quarantine = split(df)
    assert valid.count() == 2
    assert quarantine.count() == 2


def test_summary_counts_violations(spark):
    df = spark.createDataFrame([
        (1, "Item_1", 2.0),
        (None, "Item_2", 1.0),
        (3, "Item_3", -1.0),
    ], ORDERS_SCHEMA)
    s = summary(df)
    assert s["orderid_not_null"] == 1
    assert s["orderunits_positive"] == 1


def test_clean_data_has_no_violations(spark):
    df = spark.createDataFrame([(1, "Item_1", 2.0)], ORDERS_SCHEMA)
    assert sum(summary(df).values()) == 0
