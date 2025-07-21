import os
import subprocess
import logging
import json
from dependencies import DependencyManager


def create_vue_project(
    project_path,
    project_name,
    use_typescript,
    use_eslint,
    eslint_config,
    custom_eslint_rules,
    use_tailwind,
    use_prettier,
    prettier_config,
    auto_install,
    use_standalone,
    use_tests,
    package_manager,
    use_stylelint,
    env_vars,
):
    # Initialize DependencyManager
    log_file = os.path.join(project_path, "logs", "scaffold.log")
    dep_manager = DependencyManager(log_file)

    # Ensure dependencies
    success, error = dep_manager.ensure_dependencies()
    if not success:
        return False, error

    try:
        project_dir = os.path.join(project_path, project_name)
        os.makedirs(project_dir, exist_ok=True)

        # Construct vue create command
        cmd = [
            "vue",
            "create",
            project_name,
            "--default",
            "--force",
            f"--packageManager={package_manager}",
        ]
        logging.info(f"Running command: {' '.join(cmd)} in {project_path}")
        result = subprocess.run(
            cmd, cwd=project_path, check=True, capture_output=True, text=True
        )
        logging.info(f"Vue.js project created: {result.stdout}")

        # Post-creation configuration
        if use_typescript:
            logging.info("Installing TypeScript dependencies")
            subprocess.run(
                [package_manager, "install", "--save-dev", "typescript", "@types/node"],
                cwd=project_dir,
                check=True,
            )
        if use_eslint:
            logging.info(f"Installing ESLint with config {eslint_config}")
            subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "eslint",
                    f"eslint-config-{eslint_config}",
                ],
                cwd=project_dir,
                check=True,
            )
        if use_tailwind:
            logging.info("Installing Tailwind CSS with PostCSS plugin")
            subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "@tailwindcss/postcss",
                    "postcss",
                    "autoprefixer",
                ],
                cwd=project_dir,
                check=True,
            )
            # Manually create tailwind.config.js
            tailwind_config = {
                "content": ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
                "theme": {"extend": {}},
                "plugins": [],
            }
            tailwind_config_file = os.path.join(project_dir, "tailwind.config.js")
            with open(tailwind_config_file, "w") as f:
                f.write(f"module.exports = {json.dumps(tailwind_config, indent=2)}")
            logging.info(f"Created {tailwind_config_file}")
            # Manually create postcss.config.js
            postcss_config = {
                "plugins": {"@tailwindcss/postcss": {}, "autoprefixer": {}}
            }
            postcss_config_file = os.path.join(project_dir, "postcss.config.js")
            with open(postcss_config_file, "w") as f:
                f.write(f"module.exports = {json.dumps(postcss_config, indent=2)}")
            logging.info(f"Created {postcss_config_file}")
            # Update main.css or equivalent to include Tailwind directives
            css_file = os.path.join(project_dir, "src", "assets", "main.css")
            tailwind_directives = """
@tailwind base;
@tailwind components;
@tailwind utilities;
"""
            if os.path.exists(css_file):
                with open(css_file, "a") as f:
                    f.write(tailwind_directives)
                logging.info(f"Appended Tailwind directives to {css_file}")
            else:
                css_dir = os.path.dirname(css_file)
                os.makedirs(css_dir, exist_ok=True)
                with open(css_file, "w") as f:
                    f.write(tailwind_directives)
                logging.info(f"Created {css_file} with Tailwind directives")
        if use_prettier:
            logging.info("Installing Prettier")
            subprocess.run(
                [package_manager, "install", "--save-dev", "prettier"],
                cwd=project_dir,
                check=True,
            )

        # Apply custom ESLint rules
        if use_eslint and custom_eslint_rules:
            try:
                if not isinstance(custom_eslint_rules, dict):
                    raise ValueError("Custom ESLint rules must be a valid JSON object")
                eslint_config = {
                    "env": {"browser": True, "es2021": True},
                    "extends": [f"eslint-config-{eslint_config}"],
                    "parserOptions": {"ecmaVersion": 12, "sourceType": "module"},
                    "rules": custom_eslint_rules.get("rules", {}),
                }
                eslint_file = os.path.join(project_dir, ".eslintrc.json")
                with open(eslint_file, "w") as f:
                    json.dump(eslint_config, f, indent=2)
                logging.info(f"Applied custom ESLint rules to {eslint_file}")
            except ValueError as e:
                logging.error(f"Invalid ESLint configuration: {str(e)}")
                return False, f"Invalid ESLint configuration: {str(e)}"

        # Apply Prettier config
        if use_prettier and prettier_config:
            try:
                if not isinstance(prettier_config, dict):
                    raise ValueError("Prettier config must be a valid JSON object")
                prettier_file = os.path.join(project_dir, ".prettierrc")
                with open(prettier_file, "w") as f:
                    json.dump(prettier_config, f, indent=2)
                logging.info(f"Applied Prettier config to {prettier_file}")
            except ValueError as e:
                logging.error(f"Invalid Prettier configuration: {str(e)}")
                return False, f"Invalid Prettier configuration: {str(e)}"

        # Apply environment variables
        if env_vars:
            env_file = os.path.join(project_dir, ".env")
            with open(env_file, "w") as f:
                f.write(env_vars)
            logging.info(f"Applied environment variables to {env_file}")

        return True, ""
    except subprocess.CalledProcessError as e:
        error = f"Vue.js project creation failed: {e.stderr or e.stdout or 'No additional error details'}"
        logging.error(error)
        return False, error
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        logging.error(error)
        return False, error
