# Release Workflow Guide

This project uses **GitHub Actions** and **PyPI Trusted Publishing** to automate releases. You no longer need to manually build or upload artifacts.

## 1. One-Time Setup (PyPI)

Before the automation will work, you must tell PyPI to trust your GitHub repository.

1. Log in to [PyPI.org](https://pypi.org/).
2. Navigate to **Manage** > **neuromorphopy** > **Settings** > **Publishing**.
3. Click **Add a new publisher** and select **GitHub**.
4. Enter the following details:
    * **Owner:** `kpeez`
    * **Repository name:** `neuromorphopy`
    * **Workflow name:** `Publish to PyPI`
    * **Environment name:** (Leave blank)
5. Click **Add**.

*Once this is done, GitHub has permission to upload packages for this repo automatically.*

---

## 2. Routine Release Process

The general workflow is to develop features, merge them into `main`, bump the version, and let CI tag and publish the release.

### Step A: Development

1. Create branches for features/fixes (e.g., `feat-new-search`).
2. Make commits and open Pull Requests.
3. Merge these PRs into `main`.
4. Repeat until you are ready to bundle these changes into a version (e.g., `0.3.4`).

### Step B: Prepare Release

When you are ready to release the accumulated changes in `main`:

1. **Pull latest main:**

    ```bash
    git checkout main
    git pull origin main
    ```

2. **Bump the version:**
    Use `uv` to update `pyproject.toml` and `uv.lock`.

    ```bash
    uv version bump patch  # or minor, major
    # Example output: 0.3.3 -> 0.3.4
    ```

3. **Commit the bump:**

    ```bash
    git add pyproject.toml uv.lock
    git commit -m "bump: version 0.3.4"
    ```

4. **Push the commit:**

    ```bash
    git push origin main
    ```

### Step C: Tagging (automatic)

When `pyproject.toml` version changes on `main`, the **Tag release** workflow creates a `vX.Y.Z`
tag automatically. That tag is what triggers the PyPI publish workflow, which verifies the tag
matches the version in `pyproject.toml`.

If you need a manual release, you can still create and push a `vX.Y.Z` tag yourself and the
publish workflow will run as long as the tag matches the version in `pyproject.toml`.

### Step D: Verification

1. Go to the **Actions** tab in your GitHub repository.
2. You will see **Tag release** (on `main`) and **Publish to PyPI** (on the tag) running.
3. Once green, check [PyPI](https://pypi.org/project/neuromorphopy/) to see the new version.
