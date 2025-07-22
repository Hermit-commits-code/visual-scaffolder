import os
import subprocess
import logging
import json
import shutil
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
    use_router,
    use_vuex,
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
        # Remove existing project directory to avoid conflicts
        if os.path.exists(project_dir):
            logging.info(f"Removing existing project directory: {project_dir}")
            try:
                shutil.rmtree(project_dir)
                logging.info(f"Successfully removed {project_dir}")
            except Exception as e:
                logging.error(
                    f"Failed to remove existing directory {project_dir}: {str(e)}"
                )
                return False, f"Failed to remove existing directory: {str(e)}"
        os.makedirs(project_dir, exist_ok=True)
        logging.info(f"Created project directory: {project_dir}")

        # Construct vue create command
        cmd = [
            "vue",
            "create",
            project_name,
            "--default",
            "--force",
            f"--packageManager={package_manager}",
            "--no-git",
        ]
        if use_typescript:
            cmd.append("--typescript")
        if use_router:
            cmd.append("--router")
        if use_vuex:
            cmd.append("--vuex")
        logging.info(f"Running command: {' '.join(cmd)} in {project_path}")
        result = subprocess.run(
            cmd, cwd=project_path, check=True, capture_output=True, text=True
        )
        logging.info(f"Vue.js project created: {result.stdout}")

        # Log project directory contents for debugging
        dir_contents = os.listdir(project_dir)
        logging.info(f"Project directory contents: {dir_contents}")
        src_dir = os.path.join(project_dir, "src")
        if os.path.exists(src_dir):
            src_contents = os.listdir(src_dir)
            logging.info(f"src directory contents: {src_contents}")
        else:
            logging.error("src directory not found")
            return False, "Vue project creation failed: src directory not found"

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
                    "eslint-plugin-vue",
                ],
                cwd=project_dir,
                check=True,
            )
            # Create .eslintrc.json
            eslint_config_json = {
                "env": {"browser": True, "es2021": True},
                "extends": [
                    f"eslint-config-{eslint_config}",
                    "plugin:vue/vue3-essential",
                ],
                "parserOptions": {"ecmaVersion": 12, "sourceType": "module"},
                "plugins": ["vue"],
                "rules": custom_eslint_rules.get("rules", {}),
            }
            eslint_file = os.path.join(project_dir, ".eslintrc.json")
            with open(eslint_file, "w") as f:
                json.dump(eslint_config_json, f, indent=2)
            logging.info(f"Created {eslint_file} with ESLint configuration")
            # Run eslint --fix to auto-correct linting issues
            logging.info("Running ESLint auto-fix on src/ files")
            try:
                subprocess.run(
                    [package_manager, "run", "eslint", "src/**/*.{js,ts,vue}", "--fix"],
                    cwd=project_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logging.info("ESLint auto-fix completed successfully")
            except subprocess.CalledProcessError as e:
                logging.warning(
                    f"ESLint auto-fix failed: {e.stderr or e.stdout or 'No additional error details'}"
                )
                # Continue despite ESLint fix failure, as it’s not critical
            except Exception as e:
                logging.warning(f"Unexpected error during ESLint auto-fix: {str(e)}")

        if use_tailwind:
            logging.info("Installing Tailwind CSS with PostCSS plugin")
            subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "tailwindcss",
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
            postcss_config = {"plugins": {"tailwindcss": {}, "autoprefixer": {}}}
            postcss_config_file = os.path.join(project_dir, "postcss.config.js")
            with open(postcss_config_file, "w") as f:
                f.write(f"module.exports = {json.dumps(postcss_config, indent=2)}")
            logging.info(f"Created {postcss_config_file}")
            # Update or create src/assets/main.css
            css_file = os.path.join(project_dir, "src", "assets", "main.css")
            tailwind_directives = """
@tailwind base;
@tailwind components;
@tailwind utilities;
"""
            css_dir = os.path.dirname(css_file)
            os.makedirs(css_dir, exist_ok=True)
            with open(css_file, "w") as f:
                f.write(tailwind_directives)
            logging.info(f"Created/Updated {css_file} with Tailwind directives")

        if use_prettier:
            logging.info("Installing Prettier")
            subprocess.run(
                [package_manager, "install", "--save-dev", "prettier"],
                cwd=project_dir,
                check=True,
            )

        if use_stylelint:
            logging.info("Installing Stylelint")
            subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "stylelint",
                    "stylelint-config-standard",
                ],
                cwd=project_dir,
                check=True,
            )
            stylelint_config = {
                "extends": "stylelint-config-standard",
                "rules": {"indentation": 2, "number-leading-zero": "always"},
            }
            stylelint_file = os.path.join(project_dir, ".stylelintrc.json")
            with open(stylelint_file, "w") as f:
                json.dump(stylelint_config, f, indent=2)
            logging.info(f"Created {stylelint_file}")

        # Apply custom ESLint rules
        if use_eslint and custom_eslint_rules:
            try:
                if not isinstance(custom_eslint_rules, dict):
                    raise ValueError("Custom ESLint rules must be a valid JSON object")
                eslint_file = os.path.join(project_dir, ".eslintrc.json")
                with open(eslint_file, "r") as f:
                    eslint_config_json = json.load(f)
                eslint_config_json["rules"].update(custom_eslint_rules.get("rules", {}))
                with open(eslint_file, "w") as f:
                    json.dump(eslint_config_json, f, indent=2)
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
