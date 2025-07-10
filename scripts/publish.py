#!/usr/bin/env python3
"""
Automated publishing script
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run command and handle errors"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    return result


def main():
    """Main function"""
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🚀 Starting publishing process...")

    # 1. Check for uncommitted changes
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("⚠️  Uncommitted changes detected, please commit code first")
        sys.exit(1)

    # 2. Clean old build files
    print("🧹 Cleaning old build files...")
    run_command("rm -rf dist/ build/")

    # 3. Build package
    print("📦 Building package...")
    run_command("python -m build")

    # 4. Check package
    print("🔍 Checking package...")
    run_command("twine check dist/*")

    # 5. Ask whether to upload
    print("✅ Package build completed!")
    print("📋 Built files:")
    run_command("ls -la dist/")

    answer = input("\nUpload to PyPI? (y/N): ").lower()
    if answer != "y":
        print("❌ Upload cancelled")
        sys.exit(0)

    # 6. Upload to PyPI
    print("🚀 Uploading to PyPI...")
    run_command("twine upload dist/*")

    print("✅ Publishing completed!")
    print("\n📝 Next steps:")
    print("1. Test installation: uvx modelscope-mcp-server")
    print("2. Create git tag: git tag v0.1.0 && git push origin v0.1.0")


if __name__ == "__main__":
    main()
