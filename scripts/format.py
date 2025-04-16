"""Code formatting utilities.

This script provides utilities to format code using Black and isort.
"""

import subprocess
import sys
from pathlib import Path


def format_code():
    """Format code with Black and isort."""
    root_dir = Path(__file__).parent.parent.absolute()
    src_dir = root_dir / "src"
    tests_dir = root_dir / "tests"
    
    print("Running Black...")
    subprocess.run(
        ["black", str(src_dir), str(tests_dir)], 
        check=True
    )
    
    print("Running isort...")
    subprocess.run(
        ["isort", str(src_dir), str(tests_dir)], 
        check=True
    )
    
    print("✅ Code formatting completed successfully!")


def lint_code():
    """Lint code with flake8 and mypy."""
    root_dir = Path(__file__).parent.parent.absolute()
    src_dir = root_dir / "src"
    tests_dir = root_dir / "tests"
    
    print("Running flake8...")
    flake8_result = subprocess.run(
        ["flake8", str(src_dir), str(tests_dir)], 
        capture_output=True,
        text=True
    )
    
    print("Running mypy...")
    mypy_result = subprocess.run(
        ["mypy", "--ignore-missing-imports", str(src_dir)], 
        capture_output=True,
        text=True
    )
    
    # Report results
    has_errors = False
    
    if flake8_result.returncode != 0:
        has_errors = True
        print("\nflake8 errors:")
        print(flake8_result.stdout)
    
    if mypy_result.returncode != 0:
        has_errors = True
        print("\nmypy errors:")
        print(mypy_result.stdout)
    
    if has_errors:
        print("❌ Linting found issues that need to be fixed.")
        sys.exit(1)
    else:
        print("✅ Linting completed successfully!")


if __name__ == "__main__":
    # If run directly, this will format and lint the code
    format_code()
    lint_code()
