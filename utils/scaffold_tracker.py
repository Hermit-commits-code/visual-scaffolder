import os
import json
import logging
from datetime import datetime


def write_scaffold_metadata(project_dir, config):
    try:
        # Add timestamp
        config["created_at"] = datetime.now().isoformat()

        # Optional: Add tool version
        config["scaffolder_version"] = "1.0.0"

        metadata_path = os.path.join(project_dir, ".scaffold.json")
        with open(metadata_path, "w") as f:
            json.dump(config, f, indent=4)

        logging.info(f"Scaffold metadata written to {metadata_path}")

    except Exception as e:
        logging.error(f"Failed to write .scaffold.json: {str(e)}")
