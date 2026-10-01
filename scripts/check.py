"""Fail-fast reproducible local checks; output files are generated, not hand-authored."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    Path("artifacts").mkdir(exist_ok=True)
    commands = [
        ["ruff", "check", "src", "tests", "scripts"],
        ["ruff", "format", "--check", "src", "tests", "scripts"],
        ["pytest", "-q", "--junitxml=artifacts/tests.xml"],
        ["build", "--no-isolation"],
    ]
    with Path("artifacts/checks.log").open("w", encoding="utf-8") as log:
        for command in commands:
            label = "Running: " + " ".join(command)
            print(label, flush=True)
            result = subprocess.run(
                [sys.executable, "-m", *command],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            log.write(label + "\n" + result.stdout)
            log.flush()
            print(result.stdout, end="", flush=True)
            result.check_returncode()


if __name__ == "__main__":
    main()
