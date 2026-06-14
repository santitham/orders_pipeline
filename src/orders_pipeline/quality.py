"""Data-quality rules for the orders pipeline.

Rules are expressed as (name, condition) pairs where the condition is TRUE for a
GOOD row. ``split`` returns (valid_df, quarantine_df) and ``summary`` returns the
violation counts a CI gate can assert on.
"""
from pyspark.sql import DataFrame, functions as F

# A row is good when every condition holds.
RULES = {
    "orderid_not_null":    "orderid IS NOT NULL",
    "itemid_not_null":     "itemid IS NOT NULL",
    "orderunits_positive": "orderunits >= 0",
}


def _is_good(df: DataFrame):
    cond = F.expr(" AND ".join(f"({c})" for c in RULES.values()))
    return df.withColumn("_is_good", cond)


def split(df: DataFrame):
    """Return (valid_df, quarantine_df) by applying all rules."""
    tagged = _is_good(df)
    valid = tagged.where("_is_good").drop("_is_good")
    quarantine = tagged.where("NOT _is_good OR _is_good IS NULL").drop("_is_good")
    return valid, quarantine


def summary(df: DataFrame) -> dict:
    """Per-rule violation counts (CI can fail the build if any are > 0)."""
    out = {}
    for name, cond in RULES.items():
        out[name] = df.where(f"NOT ({cond}) OR ({cond}) IS NULL").count()
    return out
