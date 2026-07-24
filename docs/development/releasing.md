# Releasing

Releases are fully automated by the **Release** workflow
(`.github/workflows/release.yaml`). Bumping the version in `pyproject.toml` on `main` is
the only action a maintainer takes; the workflow tags the commit, publishes to PyPI via
Trusted Publishing, and creates the GitHub release.

## Routine release

```bash
git checkout main
git pull origin main

uv version --bump patch   # or minor / major

git add pyproject.toml uv.lock
git commit -m "bump: version $(uv version --short)"
git push origin main
```

That push triggers **Release**, which:

1. Reads `version` from `pyproject.toml`.
2. Creates and pushes the `vX.Y.Z` tag — unless that tag already exists, in which case the
   run stops and nothing is published.
3. Builds the sdist and wheel with `uv build`.
4. Publishes to PyPI using OIDC (no API token stored anywhere).
5. Creates the GitHub release with generated notes and the built artifacts attached.

Watch it under the repository's **Actions** tab, then confirm the new version on
[PyPI](https://pypi.org/project/neuromorphopy/).

## Why tagging and publishing share one workflow

GitHub deliberately does not start a workflow run for events created with the default
`GITHUB_TOKEN`. A tag pushed by a job therefore **cannot** trigger a separate
tag-triggered publish workflow. Splitting the two is a silent failure: the tag appears,
the publish never runs, and the release looks half-finished with no error anywhere.

Keeping both steps in one workflow avoids this without needing a personal access token or
GitHub App. Re-running the workflow is safe — the tag-existence check makes it idempotent.

## One-time setup

### PyPI Trusted Publishing

On [PyPI](https://pypi.org/) go to **Manage → neuromorphopy → Publishing → Add a new
publisher**, choose **GitHub**, and enter:

| Field | Value |
| --- | --- |
| Owner | `kpeez` |
| Repository name | `neuromorphopy` |
| Workflow name | `release.yaml` |
| Environment name | `pypi` |

The workflow name must be the workflow's **filename**, not the `name:` shown in the
Actions UI. This is a common misconfiguration and produces an auth failure at upload time.

### GitHub environment

Create an environment named `pypi` under **Settings → Environments**. It must match the
`Environment name` registered with PyPI above. Add required reviewers there if you want
releases to pause for manual approval before upload.

## Manual release

Use **Actions → Release → Run workflow** to re-run against the current `main`. It publishes
only if `vX.Y.Z` for the current `pyproject.toml` version does not already exist, so it is
safe to trigger when a previous run failed partway.
