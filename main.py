import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import filedialog
import re
import os


class ProjectScaffolderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Scaffolder")
        self.project_path = os.path.expanduser("~/Desktop/repos")
        self.config = {
            "project_name": "",
            "project_path": self.project_path,
            "framework": "Vue.js",
        }
        self.current_step = 0

        # Main Frame
        self.main_frame = ttkb.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Notebook for Steps
        self.notebook = ttkb.Notebook(self.main_frame, bootstyle="primary")
        self.notebook.pack(fill="both", expand=True)

        # Step 1: Project Name
        self.name_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.name_frame, text="Project Name")
        ttkb.Label(self.name_frame, text="Project Name:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.project_name_entry = ttkb.Entry(self.name_frame)
        self.project_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_result_label = ttkb.Label(self.name_frame, text="")
        self.name_result_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Step 2: Output Directory
        self.dir_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.dir_frame, text="Output Directory")
        ttkb.Label(self.dir_frame, text="Output Directory:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.output_dir_label = ttkb.Label(self.dir_frame, text=self.project_path)
        self.output_dir_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.browse_button = ttkb.Button(
            self.dir_frame,
            text="Browse",
            command=self.browse_directory,
            bootstyle="secondary",
        )
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        self.dir_result_label = ttkb.Label(self.dir_frame, text="")
        self.dir_result_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Step 3: Framework Selection
        self.framework_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.framework_frame, text="Framework")
        ttkb.Label(self.framework_frame, text="Select Framework:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.framework_var = tk.StringVar(value="Vue.js")
        frameworks = [
            "Vue.js",
            "Angular",
            "React",
            "Next.js",
            "Svelte",
            "Astro",
            "Vanilla JS",
        ]
        self.framework_menu = ttkb.OptionMenu(
            self.framework_frame, self.framework_var, "Vue.js", *frameworks
        )
        self.framework_menu.grid(row=0, column=1, padx=5, pady=5)
        self.framework_result_label = ttkb.Label(self.framework_frame, text="")
        self.framework_result_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Navigation Buttons
        self.nav_frame = ttkb.Frame(self.main_frame)
        self.nav_frame.pack(fill="x", pady=10)
        self.prev_button = ttkb.Button(
            self.nav_frame,
            text="Previous",
            command=self.prev_step,
            bootstyle="secondary",
        )
        self.prev_button.pack(side="left", padx=5)
        self.next_button = ttkb.Button(
            self.nav_frame, text="Next", command=self.next_step, bootstyle="primary"
        )
        self.next_button.pack(side="left", padx=5)

        # Initialize UI
        self.notebook.select(0)
        self.prev_button.configure(state="disabled")

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.project_path)
        if directory:
            self.output_dir_label.config(text=directory)
            self.config["project_path"] = directory
            self.dir_result_label.config(
                text=f"Selected directory: {directory}", bootstyle="success"
            )
        else:
            self.dir_result_label.config(
                text="No directory selected", bootstyle="warning"
            )

    def validate_project_name(self):
        project_name = self.project_name_entry.get().strip()
        if not project_name:
            self.name_result_label.config(
                text="Error: Project name cannot be empty", bootstyle="danger"
            )
            return False
        if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
            self.name_result_label.config(
                text="Error: Use letters, numbers, hyphens, or underscores",
                bootstyle="danger",
            )
            return False
        self.config["project_name"] = project_name
        self.name_result_label.config(
            text=f"Success: Project name '{project_name}' is valid", bootstyle="success"
        )
        return True

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.notebook.select(self.current_step)
            self.next_button.configure(state="normal")
            if self.current_step == 0:
                self.prev_button.configure(state="disabled")

    def next_step(self):
        if self.current_step == 0:
            if not self.validate_project_name():
                return
        if self.current_step < 2:
            self.current_step += 1
            self.notebook.select(self.current_step)
            self.prev_button.configure(state="normal")
            if self.current_step == 2:
                self.next_button.configure(state="disabled")
                self.framework_result_label.config(
                    text=f"Selected framework: {self.framework_var.get()}",
                    bootstyle="success",
                )

    def update_framework(self, *args):
        self.config["framework"] = self.framework_var.get()
        self.framework_result_label.config(
            text=f"Selected framework: {self.config['framework']}", bootstyle="success"
        )


if __name__ == "__main__":
    root = ttkb.Window(themename="flatly")
    app = ProjectScaffolderApp(root)
    root.mainloop()
