import os
import logging


class ProjectScaffolder:
    def __init__(self, project_path):
        self.project_path = project_path
        self.log_file = os.path.join(project_path, "logs", "scaffold.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def create_project(self, config):
        try:
            project_name = config["project_name"]
            project_path = os.path.join(config["project_path"], project_name)
            os.makedirs(project_path, exist_ok=True)
            logging.info(f"Created project directory: {project_path}")
            return True, ""
        except Exception as e:
            logging.error(f"Failed to create project directory: {str(e)}")
            return False, f"Failed to create project: {str(e)}"
