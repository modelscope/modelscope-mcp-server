#!/usr/bin/env python3
"""Version bumping script for ModelScope MCP Server."""

import argparse
import re
from pathlib import Path


def get_current_version():
    """Get current version from _version.py."""
    version_file = Path("src/modelscope_mcp_server/_version.py")
    content = version_file.read_text()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in _version.py")


def bump_version(version_type, pre_release=None):
    """Bump version based on type."""
    current = get_current_version()
    print(f"Current version: {current}")

    # Parse current version
    parts = current.split(".")
    major, minor, patch = (
        int(parts[0]),
        int(parts[1]),
        int(parts[2].split("a")[0].split("b")[0].split("rc")[0].split(".dev")[0]),
    )

    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    # Add pre-release suffix if specified
    if pre_release:
        if pre_release in ["alpha", "a"]:
            new_version += "a1"
        elif pre_release in ["beta", "b"]:
            new_version += "b1"
        elif pre_release in ["rc"]:
            new_version += "rc1"
        elif pre_release in ["dev"]:
            new_version += ".dev1"

    # Update _version.py
    version_file = Path("src/modelscope_mcp_server/_version.py")
    content = version_file.read_text()
    new_content = re.sub(
        r'__version__ = ["\'][^"\']+["\']', f'__version__ = "{new_version}"', content
    )
    version_file.write_text(new_content)

    print(f"New version: {new_version}")
    return new_version


def main():
    parser = argparse.ArgumentParser(description="Bump version")
    parser.add_argument(
        "type", choices=["major", "minor", "patch"], help="Version bump type"
    )
    parser.add_argument(
        "--pre",
        choices=["alpha", "a", "beta", "b", "rc", "dev"],
        help="Pre-release type",
    )

    args = parser.parse_args()
    new_version = bump_version(args.type, args.pre)

    print(f"Version bumped to {new_version}")
    print("Don't forget to:")
    print("1. Commit the changes")
    print("2. Create a git tag")
    print("3. Build and test the package")


if __name__ == "__main__":
    main()
