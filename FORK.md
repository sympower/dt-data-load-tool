# About this fork

This repository is Sympower's fork of [dlt](https://github.com/dlt-hub/dlt). The fork
renames the `dlt` package to `data_load_tool`, and the intent is to change nothing else.
Three differences go beyond the rename. The section "What the rename does not cover" lists
them.

The rename is not cosmetic. On Databricks, a `PostImportHook` binds the name `dlt` to
Delta Live Tables. An `import dlt` in a job therefore does not give you the data-loading
library. An `import data_load_tool` never triggers that hook, so the rename removes the
collision without a runtime workaround.

The consumer is [dt-shared-ingestion](https://github.com/sympower/dt-shared-ingestion).
Track 4 of its `TECH_DEBT.md` holds the decision record and the reasons to keep the fork.

This document exists because the fork erases its own origin. `data_load_tool/version.py`
only renames `dlt` to `data_load_tool`, so no file states which upstream version the fork
started from.

## What the fork is based on

| Item | Value |
|---|---|
| Upstream repository | `dlt-hub/dlt` |
| Base branch | `devel` |
| Base commit | `d7ee07541a8c6e61834c124c77909783149c9713` (`d7ee0754`) |
| Base commit date | 2025-03-05 |
| Distance to upstream tag `1.8.0` | 15 commits behind, 0 ahead |
| Distribution version | `1.8.0a0` |

The version string is an alpha, and that has a cause. Upstream commit `31cde9fc` ("bumps
to pre release 1.8.0a0", PR #2351, 2025-02-26) set the version to `1.8.0a0`. Upstream then
released `1.8.0` on 2025-03-05 at 18:39 UTC, about six hours after the base commit. The
base sits between the bump and the release, so the fork inherits the pre-release string.

The `devel` branch in this repository is an unmodified mirror of upstream at the same
point. So you can recover the base commit from the repository itself:

```bash
git merge-base rename-dlt devel   # -> d7ee07541a8c6e61834c124c77909783149c9713
```

The fork adds two commits on top of the base:

| Commit | What it does |
|---|---|
| `2e9101b0` | Adds `rename_dlt.sh`. |
| `eb289ce3` | Applies the rename to the whole tree. |

## Where dt-shared-ingestion pins this fork

`dt-shared-ingestion` pins the immutable commit `eb289ce3`, not a branch. It installs the
fork by three routes, because Databricks needs different ones from local dev.

| Consumer | Location | How |
|---|---|---|
| Local dev and CI | `requirements-test.txt:4` | `git+https://github.com/sympower/dt-data-load-tool.git@eb289ce3f83ad31045260e6221cc595ed2f923dd` |
| Databricks serverless | `requirements-databricks.txt:12` | The workspace wheel by direct path, `/Workspace/Shared/libs/data_load_tool/data_load_tool-1.8.0a0-py3-none-any.whl` |
| Databricks classic clusters | The job `.json` definition | The same wheel through a native `{"whl": ...}` library entry, because classic installs ignore paths in a requirements file |

Three notes on the pin:

- `requirements.txt` does not pin this fork. That file pins `setuptools==81.0.0`, which
  the fork needs because `data_load_tool 1.8.0a0` imports `pkg_resources`.
- The serverless route names the wheel by direct path on purpose. `data_load_tool` is
  unclaimed on PyPI, and `--find-links` would let a future upload shadow the wheel.
  `requirements-databricks.txt:11` records the sha256 of the wheel that is in use.
- The head of `rename-dlt` moves ahead of `eb289ce3` when a document like this one lands.
  The pin is a commit, so a new commit on the branch does not change what any job installs.

## How to repeat the rename

Use these steps for a rebase onto a newer upstream release. `<version>` is an upstream tag,
for example `1.30.0`.

1. Add upstream as a remote and fetch its tags:
   ```bash
   git remote add upstream https://github.com/dlt-hub/dlt.git
   git fetch upstream --tags
   ```
2. Create a branch at the upstream release:
   ```bash
   git switch -c rename-dlt-<version> <version>
   ```
3. Copy the two files that belong to the fork onto that branch:
   ```bash
   git checkout rename-dlt -- rename_dlt.sh FORK.md
   ```
4. Run the rename:
   ```bash
   ./rename_dlt.sh
   ```
5. Stage the result. The two `secrets.toml` test fixtures need `-f`, because
   `.gitignore` ignores them:
   ```bash
   git add -A
   git add -f tests/cli/cases/deploy_pipeline/.data_load_tool/secrets.toml
   git add -f tests/common/cases/configuration/.data_load_tool/secrets.toml
   ```
6. Commit the rename, then update the table in this document with the new base commit.
7. Build the wheel and upload it, so Databricks gets the new version:
   ```bash
   uv build --wheel
   databricks workspace import /Workspace/Shared/libs/data_load_tool/<wheel> --format RAW
   shasum -a 256 dist/<wheel>
   ```
8. Update the pin in `dt-shared-ingestion` at the three locations named earlier. Write the
   new sha256 into the comment in `requirements-databricks.txt`.

`rename_dlt.sh` runs once per tree. A second run stops with `Folder dlt not found!` and
exit code 1, because the `dlt` folder is gone. This is a guard, not a fault.

The script does not touch `rename_dlt.sh` or `FORK.md`. Both hold `dlt` as prose or as
data, so a rename inside them would corrupt them. If you add another fork-owned file, add
a `! -path` term for it to the `find` command that updates file contents.

## What the rename does not cover

`eb289ce3` is almost a pure rename, but not entirely. Three differences do not come from
`rename_dlt.sh`. A rebase must decide what to do with each one.

1. **`get-docker.sh`** — a 753-line Docker install script that `eb289ce3` added. Upstream
   `devel` does not have it. It looks like an accidental commit. Nothing imports it.
2. **`poetry.lock`** — the fork regenerated the lock file with Poetry 2.1.1, while the base
   used Poetry 1.7.1. Dependency versions moved as well, for example `adlfs` from
   `2024.7.0` to `2024.12.0`. So the claim "a rename with no functional changes" holds for
   the source tree, but not for the resolved dependencies.
3. **Two missing test fixtures** — `tests/cli/cases/deploy_pipeline/.dlt/secrets.toml` and
   `tests/common/cases/configuration/.dlt/secrets.toml` are in the base but not in the
   fork. `.gitignore:14` ignores `secrets.toml`. The script renames the `.dlt` folder, then
   `git add` skips the new path while the old path stages as a deletion. Step 5 of the
   recipe prevents this.

## How to make sure a rename is correct

This procedure compares a fresh rename against a tree that already exists. Run it after any
change to `rename_dlt.sh`.

1. Export the base tree and the renamed tree side by side:
   ```bash
   mkdir -p /tmp/base /tmp/fork
   git archive d7ee0754 | tar -x -C /tmp/base
   git archive eb289ce3 | tar -x -C /tmp/fork
   ```
2. Run the current script on the base tree:
   ```bash
   cp rename_dlt.sh /tmp/base/ && (cd /tmp/base && ./rename_dlt.sh)
   ```
3. Compare the two trees:
   ```bash
   diff -rq -x rename_dlt.sh /tmp/base /tmp/fork
   ```

Expect exactly these four lines, and nothing else. They are the three differences from
the section "What the rename does not cover". The missing fixtures give one line each:

```
Only in /tmp/fork: get-docker.sh
Files /tmp/base/poetry.lock and /tmp/fork/poetry.lock differ
Only in /tmp/base/tests/cli/cases/deploy_pipeline/.data_load_tool: secrets.toml
Only in /tmp/base/tests/common/cases/configuration/.data_load_tool: secrets.toml
```

The comparison covers 1531 files. It found no change to any of the 40 image, font and
Parquet files, so the rename is safe for binary content in this tree. A newer upstream tree
can add a binary file that holds the text `dlt`, so repeat this comparison on every rebase.

## Open decisions for a rebase

The rebase is tracked as
[DATA-3334](https://sympower.atlassian.net/browse/DATA-3334). These questions belong to it.

- **`poetry.lock`**: regenerate it again, or keep the lock file of the upstream tag?
- **`get-docker.sh`**: remove it, or keep it?
- **Version distance**: the base is 22 minor versions behind upstream `1.30.0`
  (2026-08-11), which is about 17 months. The 644 tests in `dt-shared-ingestion` mock the
  `data_load_tool` boundary, so they do not find API drift. Validate the cursor, backfill
  and reset paths on real compute, together with the deep imports `BasePaginator`,
  `common.jsonpath`, `extract.source.DltSource` and `pipeline.helpers.drop`.
- **A tag**: no tag marks `eb289ce3`. Track 4.1 of `TECH_DEBT.md` asked for one. A tag
  gives the pinned commit a name that a reader can recognize.
