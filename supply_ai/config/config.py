import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.db_path = self.config_dir / "data" / "suppliers.db"
        self.inputs_dir = self.config_dir / "inputs"
        self.llm_config = {
            "model": "llama3:8b",
            "temperature": 0.2
        }

    def ensure_directories(self):
        """Ensure all required directories exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.inputs_dir.mkdir(exist_ok=True)

    def get_config(self):
        """Return configuration as dictionary"""
        return {
            "db_path": str(self.db_path),
            "inputs_dir": str(self.inputs_dir),
            "llm_config": self.llm_config
        }
