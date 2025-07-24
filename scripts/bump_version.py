#!/usr/bin/env python3
"""
Version bumping script for ModelScope MCP Server releases.

Usage:
    python scripts/bump_version.py patch  # 1.2.3 -> 1.2.4
    python scripts/bump_version.py minor  # 1.2.3 -> 1.3.0
    python scripts/bump_version.py major  # 1.2.3 -> 2.0.0
"""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Extract current version by importing the version module."""
    # Add the src directory to Python path
    src_path = Path(__file__).parent.parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    try:
        # Import the version module
        from modelscope_mcp_server._version import __version__

        return __version__
    except ImportError as e:
        raise ValueError(f"Could not import version module: {e}")
    finally:
        # Clean up the sys.path
        if str(src_path) in sys.path:
            sys.path.remove(str(src_path))


def parse_version(version_string):
    """Parse version string, handling legacy alpha suffix."""
    # Handle legacy alpha suffix by treating it as the base version
    if version_string.endswith(".alpha"):
        base_version = version_string[:-6]  # Remove '.alpha'
        try:
            major, minor, patch = map(int, base_version.split("."))
            return major, minor, patch
        except ValueError:
            raise ValueError(f"Invalid version format: {version_string}")

    # Regular version without any suffix
    try:
        major, minor, patch = map(int, version_string.split("."))
        return major, minor, patch
    except ValueError:
        raise ValueError(f"Invalid version format: {version_string}")


def bump_version(current_version, bump_type):
    """Bump version based on type (major, minor, patch)."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version(new_version):
    """Update version in _version.py."""
    version_path = (
        Path(__file__).parent.parent / "src" / "modelscope_mcp_server" / "_version.py"
    )
    content = version_path.read_text()

    # Update version
    new_content = re.sub(
        r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content
    )

    version_path.write_text(new_content)

    # Run uv sync to update lock file
    try:
        subprocess.run(["uv", "sync"], check=True, cwd=Path(__file__).parent.parent)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to run 'uv sync': {e}")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print(__doc__)
        sys.exit(1)

    bump_type = sys.argv[1]

    try:
        current = get_current_version()
        new = bump_version(current, bump_type)

        print(f"Bumping version from {current} to {new}")
        update_version(new)
        print("✓ Updated _version.py")

        files_to_commit = "src/modelscope_mcp_server/_version.py"

        print("\nNext steps:")
        print(
            f"1. Commit the change: git add {files_to_commit} && git commit -m 'chore: bump version to {new}'"
        )
        print(f"2. Create and push tag: git tag v{new} && git push origin v{new}")
        print(
            "3. The GitHub Action will automatically create a release and publish to PyPI and Container Registry"
        )

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
