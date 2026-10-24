from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.generate_demo_db import build_database

if __name__ == "__main__":
    print(f"Created {build_database()}")
