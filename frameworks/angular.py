import os
import subprocess
import logging
import json
import shutil
from dependencies import DependencyManager
from utils.scaffold_tracker import write_scaffold_metadata
from utils.git_manager import init_git_repo


def create_angular_project(
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
    use_routing,
    package_manager,
    use_stylelint,
    env_vars,
    use_tests=False,
):
    # Validate package_manager
    valid_package_managers = ["npm", "yarn", "pnpm", "cnpm", "bun"]
    if package_manager not in valid_package_managers:
        logging.warning(
            f"Invalid package_manager '{package_manager}', defaulting to 'npm'"
        )
        package_manager = "npm"

    # Log input parameters for debugging
    logging.info(
        f"Input parameters: project_path={project_path}, project_name={project_name}, "
        f"use_typescript={use_typescript}, use_eslint={use_eslint}, "
        f"eslint_config={eslint_config}, use_tailwind={use_tailwind}, "
        f"use_prettier={use_prettier}, use_routing={use_routing}, "
        f"package_manager={package_manager}, use_stylelint={use_stylelint}, "
        f"use_tests={use_tests}"
    )

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
                shutil.rmtree(project_dir, ignore_errors=False)
                logging.info(f"Successfully removed {project_dir}")
            except Exception as e:
                logging.error(
                    f"Failed to remove existing directory {project_dir}: {str(e)}"
                )
                return False, f"Failed to remove existing directory: {str(e)}"
        os.makedirs(project_dir, exist_ok=True)
        logging.info(f"Created project directory: {project_dir}")

        # Construct ng new command
        cmd = [
            "ng",
            "new",
            project_name,
            "--style=css",
            f"--routing={str(use_routing).lower()}",
            "--skip-git",
            "--force",
            f"--package-manager={package_manager}",
        ]
        if not use_typescript:
            cmd.append("--skip-typescript")
        logging.info(f"Running command: {' '.join(cmd)} in {project_path}")
        result = subprocess.run(
            cmd, cwd=project_path, check=True, capture_output=True, text=True
        )
        logging.info(f"Angular project created: {result.stdout}")

        # Log project directory contents for debugging
        dir_contents = os.listdir(project_dir)
        logging.info(f"Project directory contents: {dir_contents}")
        src_dir = os.path.join(project_dir, "src")
        if os.path.exists(src_dir):
            src_contents = os.listdir(src_dir)
            logging.info(f"src directory contents: {src_contents}")
        else:
            logging.error("src directory not found")
            return False, "Angular project creation failed: src directory not found"

        # Initialize Git repository
        init_git_repo(project_dir)

        # Write scaffold metadata
        config = {
            "project_name": project_name,
            "framework": "angular",
            "use_typescript": use_typescript,
            "use_eslint": use_eslint,
            "eslint_config": eslint_config,
            "custom_eslint_rules": custom_eslint_rules,
            "use_tailwind": use_tailwind,
            "use_prettier": use_prettier,
            "prettier_config": prettier_config,
            "use_router": use_routing,
            "package_manager": package_manager,
            "use_stylelint": use_stylelint,
            "env_vars": env_vars,
            "use_tests": use_tests,
        }
        write_scaffold_metadata(project_dir, config)

        # Update package.json to add lint script
        package_json_path = os.path.join(project_dir, "package.json")
        with open(package_json_path, "r") as f:
            package_json = json.load(f)
        package_json["scripts"] = package_json.get("scripts", {})
        package_json["scripts"]["lint"] = "ng lint --fix"
        with open(package_json_path, "w") as f:
            json.dump(package_json, f, indent=2)
        logging.info(f"Updated {package_json_path} with lint script")

        if use_eslint:
            logging.info(f"Installing ESLint with config {eslint_config}")
            result = subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "@angular-eslint/schematics",
                    f"eslint-config-{eslint_config}",
                    "eslint",
                ],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"ESLint installation: {result.stdout}")
            # Run ng lint setup
            result = subprocess.run(
                ["ng", "lint", "--fix"],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"ESLint setup: {result.stdout}")
            # Create .eslintrc.json
            eslint_config_json = {
                "env": {"browser": True, "es2021": True},
                "extends": [
                    "plugin:@angular-eslint/recommended",
                    f"eslint-config-{eslint_config}",
                ],
                "parser": "@typescript-eslint/parser",
                "parserOptions": {"ecmaVersion": 12, "sourceType": "module"},
                "plugins": ["@typescript-eslint", "@angular-eslint"],
                "rules": custom_eslint_rules.get("rules", {}),
            }
            eslint_file = os.path.join(project_dir, ".eslintrc.json")
            with open(eslint_file, "w") as f:
                json.dump(eslint_config_json, f, indent=2)
            logging.info(f"Created {eslint_file} with ESLint configuration")
            # Run eslint --fix
            try:
                result = subprocess.run(
                    ["npx", "eslint", "src/**/*.{ts,js}", "--fix"],
                    cwd=project_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logging.info(f"ESLint auto-fix completed: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logging.warning(
                    f"ESLint auto-fix failed: {e.stderr or e.stdout or 'No additional error details'}"
                )

        if use_tailwind:
            logging.info("Installing Tailwind CSS with PostCSS plugins")
            result = subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "tailwindcss",
                    "@tailwindcss/postcss",
                    "postcss",
                    "autoprefixer",
                    "postcss-import",
                ],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"Tailwind/PostCSS installation: {result.stdout}")
            # Create tailwind.config.js
            tailwind_config = {
                "content": ["./src/**/*.{html,ts}"],
                "theme": {"extend": {}},
                "plugins": [],
            }
            tailwind_config_file = os.path.join(project_dir, "tailwind.config.js")
            with open(tailwind_config_file, "w") as f:
                f.write(f"module.exports = {json.dumps(tailwind_config, indent=2)}")
            logging.info(f"Created {tailwind_config_file}")
            # Create postcss.config.js
            postcss_config = {
                "plugins": {
                    "postcss-import": {},
                    "@tailwindcss/postcss": {},
                    "autoprefixer": {},
                }
            }
            postcss_config_file = os.path.join(project_dir, "postcss.config.js")
            with open(postcss_config_file, "w") as f:
                f.write(f"module.exports = {json.dumps(postcss_config, indent=2)}")
            logging.info(f"Created {postcss_config_file}")
            # Update src/styles.css
            css_file = os.path.join(project_dir, "src", "styles.css")
            tailwind_directives = """
@tailwind base;
@tailwind components;
@tailwind utilities;
"""
            with open(css_file, "w") as f:
                f.write(tailwind_directives)
            logging.info(f"Updated {css_file} with Tailwind directives")

        if use_prettier:
            logging.info("Installing Prettier")
            result = subprocess.run(
                [package_manager, "install", "--save-dev", "prettier"],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"Prettier installation: {result.stdout}")
            # Apply Prettier config
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

        if use_stylelint:
            logging.info("Installing Stylelint")
            result = subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "stylelint",
                    "stylelint-config-standard",
                ],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"Stylelint installation: {result.stdout}")
            stylelint_config = {
                "extends": "stylelint-config-standard",
                "rules": {"indentation": 2, "number-leading-zero": "always"},
            }
            stylelint_file = os.path.join(project_dir, ".stylelintrc.json")
            with open(stylelint_file, "w") as f:
                json.dump(stylelint_config, f, indent=2)
            logging.info(f"Created {stylelint_file}")

        if use_tests:
            logging.info("Installing Jest for testing")
            result = subprocess.run(
                [
                    package_manager,
                    "install",
                    "--save-dev",
                    "jest",
                    "@angular-builders/jest",
                    "@types/jest",
                ],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"Jest installation: {result.stdout}")
            # Update angular.json for Jest
            angular_json_path = os.path.join(project_dir, "angular.json")
            with open(angular_json_path, "r") as f:
                angular_json = json.load(f)
            projects = angular_json.get("projects", {})
            project_key = next(iter(projects))
            projects[project_key]["architect"]["test"] = {
                "builder": "@angular-builders/jest:run",
                "options": {"configPath": "jest.config.js"},
            }
            with open(angular_json_path, "w") as f:
                json.dump(angular_json, f, indent=2)
            logging.info(f"Updated {angular_json_path} with Jest configuration")
            # Create jest.config.js
            jest_config = {
                "preset": "jest-preset-angular",
                "setupFilesAfterEnv": ["<rootDir>/src/setup-jest.ts"],
                "testPathIgnorePatterns": ["/node_modules/"],
                "globals": {"ts-jest": {"tsconfig": "<rootDir>/tsconfig.spec.json"}},
            }
            jest_config_file = os.path.join(project_dir, "jest.config.js")
            with open(jest_config_file, "w") as f:
                f.write(f"module.exports = {json.dumps(jest_config, indent=2)}")
            logging.info(f"Created {jest_config_file}")
            # Create src/setup-jest.ts
            setup_jest_file = os.path.join(project_dir, "src", "setup-jest.ts")
            with open(setup_jest_file, "w") as f:
                f.write("import 'jest-preset-angular/setup-jest';\n")
            logging.info(f"Created {setup_jest_file}")
            # Install jest-preset-angular
            result = subprocess.run(
                [package_manager, "install", "--save-dev", "jest-preset-angular"],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(f"Jest preset installation: {result.stdout}")

        # Apply environment variables
        if env_vars:
            env_file = os.path.join(project_dir, ".env")
            with open(env_file, "w") as f:
                f.write(env_vars)
            logging.info(f"Applied environment variables to {env_file}")

        return True, ""
    except subprocess.CalledProcessError as e:
        error = f"Angular project creation failed: {e.stderr or e.stdout or 'No additional error details'}"
        logging.error(error)
        return False, error
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        logging.error(error)
        return False, error
