import os
import subprocess
import logging

GITIGNORE_TEMPLATES = {
    "node": """
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
    "default": """
*.pyc
__pycache__/
.env
.DS_Store
logs/
*.log
""",
}


def init_git_repo(project_path, project_type="node"):
    try:
        git_dir = os.path.join(project_path, ".git")
        if os.path.exists(git_dir):
            logging.info("Git already initialized")
            return

        subprocess.run(["git", "init"], cwd=project_path, check=True)
        logging.info("Initialized Git repository")

        # Write .gitignore
        gitignore_path = os.path.join(project_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            content = GITIGNORE_TEMPLATES.get(
                project_type, GITIGNORE_TEMPLATES["default"]
            )
            with open(gitignore_path, "w") as f:
                f.write(content.strip())
            logging.info(".gitignore created")

    except subprocess.CalledProcessError as e:
        logging.error(f"Git initialization failed: {e.stderr or e.stdout or str(e)}")
        raise RuntimeError("Git setup failed.")
