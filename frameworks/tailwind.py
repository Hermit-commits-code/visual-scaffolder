import os
import subprocess
import logging


def install_tailwind(project_dir):
    try:
        # Skip if already installed
        node_modules_path = os.path.join(project_dir, "node_modules", "tailwindcss")
        config_file = os.path.join(project_dir, "tailwind.config.js")

        if os.path.exists(node_modules_path) and os.path.exists(config_file):
            logging.info("Tailwind CSS already installed. Skipping installation.")
            return

        if not os.path.exists(os.path.join(project_dir, "package.json")):
            subprocess.run(["npm", "init", "-y"], cwd=project_dir, check=True)
            logging.info("Initialized npm in project")

        subprocess.run(
            ["npm", "install", "-D", "tailwindcss", "postcss", "autoprefixer"],
            cwd=project_dir,
            check=True,
        )
        subprocess.run(
            ["npx", "tailwindcss", "init", "-p"], cwd=project_dir, check=True
        )
        logging.info("Tailwind CSS setup completed successfully")

    except subprocess.CalledProcessError as e:
        logging.error(f"Tailwind installation failed: {e.stderr or e.stdout or str(e)}")
        raise RuntimeError("Tailwind installation failed. Check logs for details.")
