# orders_pipeline — CI/CD reference project

A minimal, working example of a tested, deployable Databricks data pipeline.
Used in **Module 3 — CI/CD for Data Engineering**.

> **Students:** see [`SETUP.md`](SETUP.md) for the classroom flow — fork this repo, clone your fork
> as a Databricks Git folder, run the tests, and trigger a real CI build by pushing.

## Layout

```
orders_pipeline/
├── src/orders_pipeline/
│   ├── transforms.py     # pure, testable transforms (no I/O)
│   └── quality.py        # data-quality rules + quarantine split
├── tests/
│   ├── conftest.py       # local SparkSession fixture
│   ├── test_transforms.py# unit + schema-validation tests (pytest + chispa)
│   └── test_quality.py   # data-quality tests
├── notebooks/
│   └── build_gold.py     # job entrypoint: does the I/O, calls the transforms
├── databricks.yml        # Asset Bundle: dev/prod targets + the job
├── .github/workflows/ci.yml  # GitHub Actions: lint -> test -> deploy
└── requirements.txt
```

The key idea: **logic lives in `src/` as pure functions** that take and return
DataFrames, so they run in seconds with no cluster and no real data. **I/O lives
in `notebooks/build_gold.py`.** That separation is what makes CI possible.

## Run the tests locally

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

## Deploy with Asset Bundles

```bash
databricks bundle validate -t dev
databricks bundle deploy   -t dev     # creates a username-prefixed job in dev
databricks bundle run orders_gold -t dev
```

## CI/CD flow

* **On a pull request** → GitHub Actions runs lint + unit/schema/DQ tests. A red
  build blocks the merge.
* **On merge to `main`** → tests run again, then `databricks bundle deploy -t prod`
  ships the job to the production target.

Branching: **trunk-based** (short-lived feature branches off `main`, merge via PR).
Promotion is by environment (dev → prod), not by long-lived branches.
