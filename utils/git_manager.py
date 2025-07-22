import os
import subprocess
import logging

GITIGNORE_TEMPLATES = {
    "node": """
# Node.js
node_modules/
dist/
.env
.DS_Store
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
""",
    "python": """
# Python
__pycache__/
*.py[cod]
*.egg-info/
*.egg
*.pyo
*.pyd
.env
.venv/
.DS_Store
logs/
*.log
""",
    "default": """
# General
.DS_Store
.env
*.log
logs/
""",
}


def detect_project_type(project_path):
    """Heuristic-based project type detection."""
    if os.path.exists(os.path.join(project_path, "package.json")):
        return "node"
    elif os.path.exists(os.path.join(project_path, "requirements.txt")) or any(
        f.endswith(".py") for f in os.listdir(project_path)
    ):
        return "python"
    return "default"


def init_git_repo(project_path):
    try:
        git_dir = os.path.join(project_path, ".git")
        if os.path.exists(git_dir):
            logging.info("Git already initialized")
            return

        subprocess.run(["git", "init"], cwd=project_path, check=True)
        logging.info("Initialized Git repository")

        gitignore_path = os.path.join(project_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            project_type = detect_project_type(project_path)
            content = GITIGNORE_TEMPLATES.get(
                project_type, GITIGNORE_TEMPLATES["default"]
            )
            with open(gitignore_path, "w") as f:
                f.write(content.strip())
            logging.info(f".gitignore created for {project_type} project")

    except subprocess.CalledProcessError as e:
        logging.error(f"Git initialization failed: {e.stderr or e.stdout or str(e)}")
        raise RuntimeError("Git setup failed.")
