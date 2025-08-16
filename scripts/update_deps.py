#!/usr/bin/env python3
"""Dependency update script."""

import re
import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run command and display results."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def get_dependency_versions() -> dict[str, str]:
    """Get current dependency versions using uv tree."""
    try:
        result = subprocess.run(["uv", "tree", "--depth", "1"], check=True, capture_output=True, text=True)

        versions = {}
        for line in result.stdout.split("\n"):
            # Parse lines like "├── fastmcp v2.10.6" or "└── ruff v0.12.5 (group: dev)"
            match = re.search(r"[├└]── (\S+)\s+v(\S+)", line)
            if match:
                package_name, version = match.groups()
                versions[package_name] = version

        return versions
    except subprocess.CalledProcessError:
        print("⚠️  Could not get dependency versions")
        return {}


def compare_versions(before: dict[str, str], after: dict[str, str]) -> None:
    """Compare and display version changes."""
    updated_packages = []

    for package, new_version in after.items():
        old_version = before.get(package)
        if old_version and old_version != new_version:
            updated_packages.append((package, old_version, new_version))

    if updated_packages:
        print("\n📦 Updated dependencies:")
        for package, old_version, new_version in updated_packages:
            print(f"  • {package}: {old_version} → {new_version}")
    else:
        print("\n📦 No dependency versions were updated")


def main() -> None:
    """Run the dependency update script."""
    print("🚀 Starting dependency updates...")

    # Get versions before update
    print("\n📋 Getting current dependency versions...")
    versions_before = get_dependency_versions()

    # 1. Update Python dependencies
    if not run_command(["uv", "sync", "--upgrade"], "Updating Python dependencies"):
        sys.exit(1)

    # 2. Update pre-commit hooks
    if not run_command(["uv", "run", "pre-commit", "autoupdate"], "Updating pre-commit hooks"):
        sys.exit(1)

    # Get versions after update
    versions_after = get_dependency_versions()

    # Compare and show changes
    compare_versions(versions_before, versions_after)

    # 3. Show file changes
    print("\n📋 Reviewing file changes:")
    run_command(["git", "status", "--porcelain"], "Checking modified files")

    print("\n✅ Dependency updates completed!")
    print("💡 Recommendations:")
    print("  1. Run tests to ensure compatibility: uv run pytest")
    print("  2. Review changes: git diff")
    print("  3. Commit updates: git add . && git commit -m 'chore: update dependencies'")


if __name__ == "__main__":
    main()
