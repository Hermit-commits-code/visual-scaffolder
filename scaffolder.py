import os
import logging
from frameworks.vue import create_vue_project


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
            project_path = config["project_path"]
            framework = config.get("framework", "Vue.js")
            os.makedirs(os.path.join(project_path, project_name), exist_ok=True)
            logging.info(
                f"Created project directory: {os.path.join(project_path, project_name)}"
            )

            if framework == "Vue.js":
                success, error = create_vue_project(
                    project_path,
                    project_name,
                    config.get("use_typescript", False),
                    config.get("use_eslint", False),
                    config.get("eslint_config", "prettier"),
                    config.get("custom_eslint_rules", {}),
                    config.get("use_tailwind", False),
                    config.get("use_prettier", False),
                    config.get("prettier_config", {}),
                    config.get("auto_install", False),
                    config.get("use_standalone", False),
                    config.get("use_tests", False),
                    config.get("package_manager", "npm"),
                    config.get("use_stylelint", False),
                    config.get("env_vars", ""),
                )
                if not success:
                    return False, error
            else:
                logging.info(
                    f"Framework {framework} not yet supported, created empty directory"
                )
                return True, ""

            return True, ""
        except Exception as e:
            logging.error(f"Failed to create project: {str(e)}")
            return False, f"Failed to create project: {str(e)}"
