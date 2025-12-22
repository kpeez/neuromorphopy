# Release Workflow Guide

This project uses **GitHub Actions** and **PyPI Trusted Publishing** to automate releases. You no longer need to manually build or upload artifacts.

## 1. One-Time Setup (PyPI)

Before the automation will work, you must tell PyPI to trust your GitHub repository.

1.  Log in to [PyPI.org](https://pypi.org/).
2.  Navigate to **Manage** > **neuromorphopy** > **Settings** > **Publishing**.
3.  Click **Add a new publisher** and select **GitHub**.
4.  Enter the following details:
    *   **Owner:** `kpeez`
    *   **Repository name:** `neuromorphopy`
    *   **Workflow name:** `publish.yml`
    *   **Environment name:** (Leave blank)
5.  Click **Add**.

*Once this is done, GitHub has permission to upload packages for this repo automatically.*

---

## 2. Routine Release Process

The general workflow is to develop features, merge them into `main`, and then "cut a release" by tagging a specific commit.

### Step A: Development
1.  Create branches for features/fixes (e.g., `feat-new-search`).
2.  Make commits and open Pull Requests.
3.  Merge these PRs into `main`.
4.  Repeat until you are ready to bundle these changes into a version (e.g., `0.3.4`).

### Step B: Prepare Release
When you are ready to release the accumulated changes in `main`:

1.  **Pull latest main:**
    ```bash
    git checkout main
    git pull origin main
    ```

2.  **Bump the version:**
    Use `uv` to update `pyproject.toml` and `uv.lock`.
    ```bash
    uv version bump patch  # or minor, major
    # Example output: 0.3.3 -> 0.3.4
    ```

3.  **Commit the bump:**
    ```bash
    git add pyproject.toml uv.lock
    git commit -m "bump: version 0.3.4"
    ```

4.  **Push the commit:**
    ```bash
    git push origin main
    ```

### Step C: Trigger Release (Tagging)
The automation only runs when you push a tag starting with `v`.

1.  **Create the tag:**
    ```bash
    git tag v0.3.4
    ```

2.  **Push the tag:**
    ```bash
    git push origin v0.3.4
    ```

### Step D: Verification
1.  Go to the **Actions** tab in your GitHub repository.
2.  You will see a workflow named **Publish to PyPI** running.
3.  Once green, check [PyPI](https://pypi.org/project/neuromorphopy/) to see the new version.
