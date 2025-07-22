import os
import subprocess
import logging
import platform
import urllib.request


class DependencyManager:
    def __init__(self, log_file):
        self.log_file = log_file
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def check_internet(self):
        try:
            urllib.request.urlopen("https://deb.nodesource.com", timeout=5)
            logging.info("Internet connection verified")
            return True, ""
        except Exception as e:
            logging.error(f"No internet connection: {str(e)}")
            return False, f"No internet connection. Please check your network: {str(e)}"

    def check_sudo(self):
        try:
            subprocess.run(
                ["sudo", "-n", "true"], capture_output=True, text=True, check=True
            )
            logging.info("Sudo access verified (non-interactive)")
            return True, ""
        except subprocess.CalledProcessError:
            logging.error("Sudo requires password or is not available")
            return (
                False,
                "Sudo requires password. Run: sudo apt update && sudo apt install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs",
            )
        except FileNotFoundError:
            logging.error("Sudo not installed")
            return (
                False,
                "Sudo is not installed. Run: sudo apt update && sudo apt install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs",
            )

    def check_node(self):
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=True
            )
            node_version = result.stdout.strip()
            logging.info(f"Node.js found: {node_version}")
            major_version = int(node_version.split(".")[0].lstrip("v"))
            if 8 <= major_version <= 22:
                return True, ""
            else:
                logging.warning(
                    f"Node.js version {node_version} is not supported (required: 8-22)"
                )
                return (
                    False,
                    f"Node.js version {node_version} is not supported. Run: sudo apt update && sudo apt install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs",
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.info("Node.js not installed or not found in PATH")
            return (
                False,
                "Node.js is not installed. Run: sudo apt update && sudo apt install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs",
            )

    def check_vue_cli(self):
        try:
            result = subprocess.run(
                ["vue", "--version"], capture_output=True, text=True, check=True
            )
            vue_version = result.stdout.strip()
            logging.info(f"Vue CLI found: {vue_version}")
            return True, ""
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.info("Vue CLI not installed or not found in PATH")
            return False, "Vue CLI is not installed. Run: npm install -g @vue/cli"

    def check_angular_cli(self):
        try:
            result = subprocess.run(
                ["ng", "--version"], capture_output=True, text=True, check=True
            )
            angular_version = result.stdout.strip()
            logging.info(f"Angular CLI found: {angular_version}")
            return True, ""
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.info("Angular CLI not installed or not found in PATH")
            return (
                False,
                "Angular CLI is not installed. Run: npm install -g @angular/cli",
            )

    def install_node(self):
        internet_success, internet_error = self.check_internet()
        if not internet_success:
            return False, internet_error

        sudo_success, sudo_error = self.check_sudo()
        if not sudo_success:
            return False, sudo_error

        try:
            logging.info("Downloading Node.js 18.19.0 setup script")
            script_path = "/tmp/nodesource_setup.sh"
            subprocess.run(
                [
                    "curl",
                    "-fsSL",
                    "https://deb.nodesource.com/setup_18.x",
                    "-o",
                    script_path,
                ],
                check=True,
            )
            logging.info("Running Node.js setup script")
            subprocess.run(["sudo", "bash", script_path], check=True)
            logging.info("Installing Node.js")
            subprocess.run(["sudo", "apt", "install", "-y", "nodejs"], check=True)
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=True
            )
            logging.info(f"Node.js installed: {result.stdout.strip()}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error = f"Failed to install Node.js: {e.stderr or e.stdout or 'Command failed without output'}"
            logging.error(error)
            return False, error
        except Exception as e:
            error = f"Unexpected error installing Node.js: {str(e)}"
            logging.error(error)
            return False, error
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
                logging.info(f"Cleaned up {script_path}")

    def install_vue_cli(self):
        try:
            logging.info("Installing Vue CLI globally")
            subprocess.run(
                ["npm", "install", "-g", "@vue/cli"],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                ["vue", "--version"], capture_output=True, text=True, check=True
            )
            logging.info(f"Vue CLI installed: {result.stdout.strip()}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error = f"Failed to install Vue CLI: {e.stderr or e.stdout or 'Command failed without output'}"
            logging.error(error)
            return False, error
        except Exception as e:
            error = f"Unexpected error installing Vue CLI: {str(e)}"
            logging.error(error)
            return False, error

    def install_angular_cli(self):
        try:
            logging.info("Installing Angular CLI globally")
            subprocess.run(
                ["npm", "install", "-g", "@angular/cli"],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                ["ng", "--version"], capture_output=True, text=True, check=True
            )
            logging.info(f"Angular CLI installed: {result.stdout.strip()}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error = f"Failed to install Angular CLI: {e.stderr or e.stdout or 'Command failed without output'}"
            logging.error(error)
            return False, error
        except Exception as e:
            error = f"Unexpected error installing Angular CLI: {str(e)}"
            logging.error(error)
            return False, error

    def ensure_dependencies(self):
        node_success, node_error = self.check_node()
        if not node_success:
            logging.info("Attempting to install Node.js")
            node_success, node_error = self.install_node()
            if not node_success:
                return False, node_error

        vue_success, vue_error = self.check_vue_cli()
        if not vue_success:
            logging.info("Attempting to install Vue CLI")
            vue_success, vue_error = self.install_vue_cli()
            if not vue_success:
                return False, vue_error

        return True, ""

    def ensure_angular_dependencies(self):
        node_success, node_error = self.check_node()
        if not node_success:
            logging.info("Attempting to install Node.js")
            node_success, node_error = self.install_node()
            if not node_success:
                return False, node_error

        angular_success, angular_error = self.check_angular_cli()
        if not angular_success:
            logging.info("Attempting to install Angular CLI")
            angular_success, angular_error = self.install_angular_cli()
            if not angular_success:
                return False, angular_error

        return True, ""
