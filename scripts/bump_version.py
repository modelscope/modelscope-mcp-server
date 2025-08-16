#!/usr/bin/env python3
"""Version bumping script for ModelScope MCP Server releases.

Usage:
    python scripts/bump_version.py patch           # 1.2.3 -> 1.2.4
    python scripts/bump_version.py minor           # 1.2.3 -> 1.3.0
    python scripts/bump_version.py major           # 1.2.3 -> 2.0.0
    python scripts/bump_version.py set {version}   # PEP 440 format, e.g. 1.2.3a1, 1.2.3.dev1
"""

import re
import subprocess
import sys
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
VERSION_FILE = SRC_DIR / "modelscope_mcp_server" / "_version.py"
FILES_TO_COMMIT = "src/modelscope_mcp_server/_version.py"

# PEP 440 version pattern
PEP440_PATTERN = r"^(\d+)\.(\d+)\.(\d+)((a|b|rc)\d+|\.dev\d+|\.post\d+)?$"

BUMP_TYPES = ["major", "minor", "patch"]


def get_current_version() -> str:
    """Extract current version by importing the version module."""
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    try:
        from modelscope_mcp_server._version import __version__

        return __version__
    except ImportError as e:
        raise ValueError(f"Could not import version module: {e}") from e
    finally:
        if str(SRC_DIR) in sys.path:
            sys.path.remove(str(SRC_DIR))


def parse_version(version_string: str) -> tuple[int, int, int]:
    """Parse version string, extracting major.minor.patch from PEP 440 format."""
    # Extract base version (major.minor.patch) from PEP 440 format
    # Examples: 1.2.3 -> (1,2,3), 1.2.3a1 -> (1,2,3), 1.2.3.dev1 -> (1,2,3)
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version_string)
    if not match:
        raise ValueError(f"Invalid version format: {version_string}")

    try:
        major, minor, patch = map(int, match.groups())
        return major, minor, patch
    except ValueError as e:
        raise ValueError(f"Invalid version format: {version_string}") from e


def validate_version_format(version_string: str) -> None:
    """Validate that the version string follows PEP 440 format."""
    if not re.match(PEP440_PATTERN, version_string):
        raise ValueError(f"Invalid version format (should follow PEP 440): {version_string}")


def bump_version(current_version: str, bump_type: str) -> str:
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


def update_version(new_version: str) -> None:
    """Update version in _version.py and sync dependencies."""
    content = VERSION_FILE.read_text()
    new_content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    VERSION_FILE.write_text(new_content)

    # Run uv sync to update lock file
    try:
        subprocess.run(["uv", "sync"], check=True, cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to run 'uv sync': {e}")


def handle_version_change(action_description: str, new_version: str) -> str:
    """Handle version changes with common logic."""
    current = get_current_version()
    print(f"{action_description} from {current} to {new_version}")
    update_version(new_version)
    print("✓ Updated _version.py")
    return new_version


def print_next_steps(version: str) -> None:
    """Print the next steps after version update."""
    print("\nNext steps:")
    print(f"1. Commit the change: git add {FILES_TO_COMMIT} && git commit -m 'chore: bump version to {version}'")
    print(f"2. Create and push tag: git tag v{version} && git push origin v{version}")
    print("3. The GitHub Action will automatically create a release and publish to PyPI and Container Registry")


def main() -> None:
    """Handle version bumping operations."""
    if len(sys.argv) not in [2, 3]:
        print(__doc__)
        sys.exit(1)

    try:
        if len(sys.argv) == 2:
            # Traditional bump: python bump_version.py major/minor/patch
            bump_type = sys.argv[1]
            if bump_type not in BUMP_TYPES:
                print(__doc__)
                sys.exit(1)

            current = get_current_version()
            new = bump_version(current, bump_type)
            final_version = handle_version_change("Bumping version", new)

        elif len(sys.argv) == 3:
            # Manual set: python bump_version.py set 1.2.3a1
            if sys.argv[1] != "set":
                print(__doc__)
                sys.exit(1)

            new = sys.argv[2]
            validate_version_format(new)
            final_version = handle_version_change("Setting version", new)

        print_next_steps(final_version)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
