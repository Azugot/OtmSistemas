"""Wrapper para executar a interface Streamlit."""
from __future__ import annotations

import subprocess
import sys


def main() -> None:
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    subprocess.call(cmd)


if __name__ == "__main__":
    main()
