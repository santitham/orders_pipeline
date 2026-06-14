# Databricks notebook source
# MAGIC %md
# MAGIC # orders_gold — job entrypoint
# MAGIC The Asset Bundle deploys this notebook as a Job. It does the **I/O** (read Silver,
# MAGIC write Gold) and calls the **pure, tested transforms** from `orders_pipeline`.
# MAGIC Keeping I/O here and logic in `src/` is what makes the logic unit-testable in CI.

# COMMAND ----------

# the bundle passes the target catalog as a job parameter
dbutils.widgets.text("catalog", "ctl_training_dev")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = "bootcamp_m2"

import sys
sys.path.append("../src")                       # make orders_pipeline importable
from orders_pipeline.transforms import revenue_by_category
from orders_pipeline.quality import split

# COMMAND ----------

orders = spark.read.table(f"{CATALOG}.{SCHEMA}.orders_silver") \
              .select("orderid", "itemid", "orderunits")
items = spark.read.table(f"{CATALOG}.{SCHEMA}.items")          # item -> category lookup

# data-quality gate before publishing
valid, quarantine = split(orders)
if quarantine.count() > 0:
    quarantine.write.mode("append").saveAsTable(f"{CATALOG}.{SCHEMA}.orders_quarantine")

gold = revenue_by_category(valid, items)
gold.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.revenue_by_category")
print("wrote", f"{CATALOG}.{SCHEMA}.revenue_by_category")
