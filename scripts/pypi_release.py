#!/usr/bin/env python3
"""Release script for ModelScope MCP Server."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, dry_run=False):
    """Run shell command."""
    print(f"Running: {cmd}")
    if dry_run and any(
        danger in cmd for danger in ["git tag", "git push", "uv publish"]
    ):
        print("  [DRY RUN] Command skipped")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        if not dry_run:
            sys.exit(1)
    return result


def get_current_version():
    """Get current version."""
    version_file = Path("src/modelscope_mcp_server/_version.py")
    content = version_file.read_text()
    import re

    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version")


def main():
    """Main release process."""
    parser = argparse.ArgumentParser(description="Release ModelScope MCP Server")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual changes will be made")

    print("🚀 Starting release process...")

    # 1. Get current version
    version = get_current_version()
    print(f"📦 Current version: {version}")

    # 2. Check git status
    result = run_command("git status --porcelain", check=False, dry_run=args.dry_run)
    if result.stdout.strip() and not args.dry_run:
        print("❌ Working directory not clean. Please commit changes first.")
        sys.exit(1)
    elif result.stdout.strip() and args.dry_run:
        print("⚠️  Working directory not clean (ignored in dry-run mode)")

    # 3. Clean old build files (from old script)
    print("🧹 Cleaning old build files...")
    run_command("rm -rf dist/ build/", check=False, dry_run=args.dry_run)

    # 4. Run tests and checks
    print("🧪 Running pre-commit checks...")
    run_command("uv run pre-commit run --all-files", dry_run=args.dry_run)

    # 5. Build package
    print("🔨 Building package...")
    run_command("uv build", dry_run=args.dry_run)

    # 6. Check package integrity (from old script)
    print("🔍 Checking package integrity...")
    result = run_command("uv run twine check dist/*", check=False, dry_run=args.dry_run)
    if result.returncode != 0:
        print("⚠️  Twine check failed or not available, skipping package check")

    # 7. Show built files (from old script)
    print("📋 Built files:")
    run_command("ls -la dist/", dry_run=args.dry_run)

    # 8. Ask for confirmation
    if args.dry_run:
        print(f"\n📤 [DRY RUN] Would release version {version}")
    else:
        response = input(f"\n📤 Ready to release version {version}? (y/N): ")
        if response.lower() != "y":
            print("Release cancelled.")
            sys.exit(0)

    # 9. Create git tag
    print(f"🏷️  Creating git tag v{version}...")
    run_command(f"git tag v{version}", dry_run=args.dry_run)

    # 10. Push tag
    print("📤 Pushing tag to origin...")
    run_command("git push origin --tags", dry_run=args.dry_run)

    # 11. Publish to PyPI
    print("📦 Publishing to PyPI...")
    run_command("uv publish --token $PYPI_TOKEN", dry_run=args.dry_run)

    print(f"✅ Successfully released version {version}!")
    print(f"🔗 Check: https://pypi.org/project/modelscope-mcp-server/{version}/")

    # 12. Post-release instructions (from old script)
    print("\n📝 Next steps:")
    print(f"1. Test installation: uv tool install modelscope-mcp-server=={version}")
    print(
        "2. Test import: python -c 'import modelscope_mcp_server; print(modelscope_mcp_server.__version__)'"
    )
    print("3. Update documentation if needed")
    print("4. Announce the release")


if __name__ == "__main__":
    main()
