#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime

class ModelVersionManager:
    def __init__(self, version_folder="model_versions2"):
        self.version_folder = version_folder
        self.current_version = {"major": 1, "minor": 0, "batch": 0}

        os.makedirs(self.version_folder, exist_ok=True)

    def save_version(self, changes, evaluation_metrics):
        """Save a new version with changes and evaluation metrics into a new text file."""
        if changes == "algorithm":
            self.current_version["major"] += 1
            self.current_version["minor"] = 0
            self.current_version["batch"] = 0
        elif changes == "encoding":
            self.current_version["minor"] += 1
            self.current_version["batch"] = 0
        else: 
            self.current_version["batch"] += 1

        version_string = f"{self.current_version['major']}.{self.current_version['minor']}.{self.current_version['batch']}"

        timestamp = datetime.now().isoformat()
        content = (
            f"Version: {version_string}\n"
            f"Timestamp: {timestamp}\n"
            f"Changes: {changes}\n"
            f"Evaluation Metrics:\n"
        )
        for metric, value in evaluation_metrics.items():
            content += f"  - {metric}: {value}\n"

        filename = os.path.join(self.version_folder, f"version_{version_string}.txt")
        with open(filename, "w") as file:
            file.write(content)

        print(f"Version {version_string} saved to {filename}")

    def reset_version(self):
        """Reset the version to 1.0.0."""
        self.current_version = {"major": 1, "minor": 0, "batch": 0}
        print("Version reset to 1.0.0")

    def get_version_folder(self):
        """Return the folder where versions are stored."""
        return self.version_folder
