import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import re
import logging
from scaffolder import ProjectScaffolder
import json


class ProjectScaffolderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Scaffolder")
        self.style = ttk.Style("darkly")
        self.project_name = tk.StringVar()
        self.project_path = tk.StringVar()
        self.framework = tk.StringVar(value="Vue.js")
        self.use_typescript = tk.BooleanVar()
        self.use_tailwind = tk.BooleanVar()
        self.use_eslint = tk.BooleanVar()
        self.use_prettier = tk.BooleanVar()
        self.eslint_config = tk.StringVar(value="prettier")
        self.custom_eslint_rules = tk.StringVar(
            value='{"rules": {"semi": ["error", "always"], "quotes": ["error", "single"]}}'
        )
        self.prettier_config = tk.StringVar(
            value='{"printWidth": 80, "singleQuote": true, "trailingComma": "es5"}'
        )
        self.current_step = 1
        log_file = os.path.join(
            self.project_path.get() or os.getcwd(), "logs", "scaffold.log"
        )
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.setup_ui()

    def setup_ui(self):
        self.clear_frame()
        if self.current_step == 1:
            self.setup_step1()
        elif self.current_step == 2:
            self.setup_step2()
        elif self.current_step == 3:
            self.setup_step3()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_step1(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(frame, text="Enter Project Name:").grid(
            row=0, column=0, pady=5, sticky=tk.W
        )
        ttk.Entry(frame, textvariable=self.project_name).grid(
            row=1, column=0, pady=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(frame, text="Next", command=self.validate_step1).grid(
            row=2, column=0, pady=10
        )
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=3, column=0, pady=5)

    def validate_step1(self):
        project_name = self.project_name.get().strip()
        logging.info(f"Validating project name: {project_name}")
        if not project_name:
            logging.error("Project name is empty")
            self.status_label.configure(
                text="Error: Project name cannot be empty", bootstyle="danger"
            )
            return
        if not re.match(r"^[a-zA-Z0-9-]{1,50}$", project_name):
            logging.error(
                f"Invalid project name: {project_name}. Must be alphanumeric with hyphens, 1-50 characters"
            )
            self.status_label.configure(
                text="Error: Project name must be alphanumeric with hyphens, 1-50 characters",
                bootstyle="danger",
            )
            return
        self.status_label.configure(
            text="Success: Project name is valid", bootstyle="success"
        )
        logging.info("Project name validated successfully")
        self.current_step = 2
        self.setup_ui()

    def setup_step2(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(frame, text="Select Project Path:").grid(
            row=0, column=0, pady=5, sticky=tk.W
        )
        ttk.Entry(frame, textvariable=self.project_path).grid(
            row=1, column=0, pady=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(frame, text="Browse", command=self.browse_path).grid(
            row=1, column=1, pady=5, padx=5
        )
        ttk.Button(frame, text="Back", command=lambda: self.goto_step(1)).grid(
            row=2, column=0, pady=10, sticky=tk.W
        )
        ttk.Button(frame, text="Next", command=self.validate_step2).grid(
            row=2, column=1, pady=10, sticky=tk.E
        )
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

    def browse_path(self):
        path = tk.filedialog.askdirectory()
        if path:
            self.project_path.set(path)

    def validate_step2(self):
        project_path = self.project_path.get().strip()
        logging.info(f"Validating project path: {project_path}")
        if not os.path.isdir(project_path):
            logging.error(f"Invalid project path: {project_path}")
            self.status_label.configure(
                text="Error: Invalid project path", bootstyle="danger"
            )
            return
        self.status_label.configure(
            text="Success: Project path is valid", bootstyle="success"
        )
        logging.info("Project path validated successfully")
        self.current_step = 3
        self.setup_ui()

    def setup_step3(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(frame, text="Select Framework:").grid(
            row=0, column=0, pady=5, sticky=tk.W
        )
        frameworks = ["Vue.js", "Angular", "React"]
        ttk.OptionMenu(frame, self.framework, "Vue.js", *frameworks).grid(
            row=1, column=0, pady=5, sticky=tk.W
        )
        ttk.Checkbutton(
            frame, text="Use TypeScript", variable=self.use_typescript
        ).grid(row=2, column=0, pady=5, sticky=tk.W)
        ttk.Checkbutton(
            frame, text="Use Tailwind CSS", variable=self.use_tailwind
        ).grid(row=3, column=0, pady=5, sticky=tk.W)
        ttk.Checkbutton(frame, text="Use ESLint", variable=self.use_eslint).grid(
            row=4, column=0, pady=5, sticky=tk.W
        )
        ttk.Label(frame, text="ESLint Config (e.g., prettier, standard):").grid(
            row=5, column=0, pady=5, sticky=tk.W
        )
        ttk.Entry(frame, textvariable=self.eslint_config).grid(
            row=6, column=0, pady=5, sticky=(tk.W, tk.E)
        )
        ttk.Label(frame, text="Custom ESLint Rules (JSON):").grid(
            row=7, column=0, pady=5, sticky=tk.W
        )
        ttk.Entry(frame, textvariable=self.custom_eslint_rules).grid(
            row=8, column=0, pady=5, sticky=(tk.W, tk.E)
        )
        ttk.Label(frame, text="Custom Prettier Config (JSON):").grid(
            row=9, column=0, pady=5, sticky=tk.W
        )
        ttk.Entry(frame, textvariable=self.prettier_config).grid(
            row=10, column=0, pady=5, sticky=(tk.W, tk.E)
        )
        ttk.Checkbutton(frame, text="Use Prettier", variable=self.use_prettier).grid(
            row=11, column=0, pady=5, sticky=tk.W
        )
        ttk.Button(frame, text="Back", command=lambda: self.goto_step(2)).grid(
            row=12, column=0, pady=10, sticky=tk.W
        )
        ttk.Button(frame, text="Create", command=self.create_project).grid(
            row=12, column=1, pady=10, sticky=tk.E
        )
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=13, column=0, columnspan=2, pady=5)

    def goto_step(self, step):
        self.current_step = step
        self.setup_ui()

    def create_project(self):
        project_path = self.project_path.get().strip()
        project_name = self.project_name.get().strip()
        logging.info(f"Creating project: {project_name} at {project_path}")
        try:
            custom_eslint_rules = (
                json.loads(self.custom_eslint_rules.get())
                if self.use_eslint.get()
                else {}
            )
            prettier_config = (
                json.loads(self.prettier_config.get())
                if self.use_prettier.get()
                else {}
            )
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in ESLint or Prettier config: {str(e)}")
            self.status_label.configure(
                text=f"Error: Invalid JSON in ESLint or Prettier config: {str(e)}",
                bootstyle="danger",
            )
            return

        config = {
            "project_name": project_name,
            "project_path": project_path,
            "framework": self.framework.get(),
            "use_typescript": self.use_typescript.get(),
            "use_tailwind": self.use_tailwind.get(),
            "use_eslint": self.use_eslint.get(),
            "eslint_config": self.eslint_config.get(),
            "custom_eslint_rules": custom_eslint_rules,
            "use_prettier": self.use_prettier.get(),
            "prettier_config": prettier_config,
        }
        scaffolder = ProjectScaffolder(project_path)
        success, error = scaffolder.create_project(config)
        if success:
            self.status_label.configure(
                text=f"Project '{project_name}' created successfully",
                bootstyle="success",
            )
            logging.info(f"Project '{project_name}' created successfully")
        else:
            self.status_label.configure(text=f"Error: {error}", bootstyle="danger")
            logging.error(f"Project creation failed: {error}")


if __name__ == "__main__":
    root = ttk.Window()
    app = ProjectScaffolderApp(root)
    root.mainloop()
