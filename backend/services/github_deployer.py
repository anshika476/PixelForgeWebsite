import os
import subprocess
import shutil
import re

GITHUB_USER = os.getenv("GITHUB_USERNAME")


def deploy_project(project_path, repo_name):

    repo_name = re.sub(
        r"[^a-zA-Z0-9-]",
        "-",
        repo_name
    ).lower().strip("-")

    workflow_dir = os.path.join(
        project_path,
        ".github",
        "workflows"
    )

    os.makedirs(workflow_dir, exist_ok=True)

    shutil.copy(
        "templates/deploy.yml",
        os.path.join(
            workflow_dir,
            "deploy.yml"
        )
    )

    # -------------------------
    # GIT INIT
    # -------------------------

    subprocess.run(
        ["git", "init"],
        cwd=project_path,
        check=True
    )

    subprocess.run(
        ["git", "branch", "-M", "main"],
        cwd=project_path,
        check=True
    )

    # -------------------------
    # COMMIT FILES FIRST
    # -------------------------

    subprocess.run(
        ["git", "add", "."],
        cwd=project_path,
        check=True
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Initial AI generated website"
        ],
        cwd=project_path,
        check=True
    )

    # -------------------------
    # CREATE GITHUB REPO
    # -------------------------

    subprocess.run(
        [
            "gh",
            "repo",
            "create",
            repo_name,
            "--public",
            "--source=.",
            "--remote=origin"
        ],
        cwd=project_path,
        check=True
    )

    # -------------------------
    # PUSH TO GITHUB
    # -------------------------

    subprocess.run(
        [
            "git",
            "push",
            "-u",
            "origin",
            "main"
        ],
        cwd=project_path,
        check=True
    )

    print(f"Repository deployed: {repo_name}")

    return {
        "repo_url":
            f"https://github.com/{GITHUB_USER}/{repo_name}",

        "live_url":
            f"https://{GITHUB_USER.lower()}.github.io/{repo_name}/"
    }
