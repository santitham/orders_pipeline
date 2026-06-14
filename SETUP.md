# Classroom Setup — fork, clone as a Git folder, run CI

The hands-on path for **Module 3**. You'll fork the repo, run its tests inside Databricks,
and trigger a real CI build by pushing. Budget ~15 minutes the first time.

## 1. Fork the repo (GitHub)
- Open the instructor repo and click **Fork** (top-right) → creates `your-username/orders_pipeline`.
- In your fork, open the **Actions** tab once and click **"I understand my workflows, enable them"**
  (forked repos start with Actions disabled).

## 2. Link GitHub in Databricks (one time)
- Create a GitHub **Personal Access Token**: GitHub → Settings → Developer settings → Tokens.
  A fine-grained token with **Contents: read/write** on your fork is enough.
- In Databricks: **Settings → Linked accounts** (Git integration) → provider **GitHub** → paste the token.

## 3. Clone your fork as a Databricks Git folder
- Databricks **Workspace → Create → Git folder**.
- Repository URL: `https://github.com/your-username/orders_pipeline.git` → **Create**.
- It appears under `/Workspace/Users/<you>/orders_pipeline` (the path you set as `REPO_PATH`).

## 4. Run the tests in the workspace
- Open the **Module 3 notebook**, set `REPO_PATH` in the D0 cell to your Git-folder path, and run it —
  you should see `pytest` report all green and exit code 0.
- Or, from any notebook cell:
  ```
  %sh cd /Workspace/Users/<you>/orders_pipeline && PYTHONPATH=src python -m pytest -q
  ```

## 5. The dev loop → trigger CI
1. In the Git folder, create a short-lived **branch** and edit `src/orders_pipeline/transforms.py` or a test.
2. **Commit & push** from the Git-folder UI.
3. On GitHub, open a **pull request**. The **Actions** tab shows your CI run (lint → unit/schema/DQ tests).
   - **Green** → safe to merge. **Red** → read the failing test, fix, push again.

## Incident drill (the schema-break)
- Rename `revenue` → `amount` in `transforms.py`, commit & push → the **schema test fails** → a **red build**
  blocks the merge.
- Revert the rename, push → green again. That red build is CI doing exactly its job: catching a breaking change
  on the PR instead of in production.

---

**Note on deploy.** The `deploy-prod` job (`databricks bundle deploy -t prod`) runs **only on the instructor
repo** — it needs `DATABRICKS_HOST` / `DATABRICKS_TOKEN` secrets. Your fork runs the **test job only**, which is
the point: everyone gets real CI feedback; nobody needs production credentials.
