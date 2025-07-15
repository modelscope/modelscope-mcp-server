#!/usr/bin/env python3
"""Docker Hub release script for ModelScope MCP Server."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, dry_run=False):
    """Run shell command."""
    print(f"Running: {cmd}")
    if dry_run and any(
        danger in cmd
        for danger in [
            "docker buildx build",
            "docker push",
            "docker tag",
            "docker build",
            "docker manifest",
        ]
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
    """Get current version from _version.py."""
    version_file = Path("src/modelscope_mcp_server/_version.py")
    if not version_file.exists():
        print("Error: _version.py not found")
        sys.exit(1)

    content = version_file.read_text()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in _version.py")


def check_docker_buildx():
    """Check if Docker buildx is available."""
    result = run_command("docker buildx version", check=False)
    return result.returncode == 0


def check_docker_manifest():
    """Check if Docker manifest is available."""
    result = run_command("docker manifest --help", check=False)
    return result.returncode == 0


def get_proxy_build_args():
    """Get proxy build arguments from environment."""
    proxy_args = []

    # Check for common proxy environment variables
    proxy_vars = [
        ("HTTP_PROXY", "http_proxy"),
        ("HTTPS_PROXY", "https_proxy"),
        ("NO_PROXY", "no_proxy"),
        ("ALL_PROXY", "all_proxy"),
    ]

    for upper_var, lower_var in proxy_vars:
        # Check uppercase first, then lowercase
        value = os.getenv(upper_var) or os.getenv(lower_var)
        if value:
            proxy_args.extend(
                [
                    "--build-arg",
                    f"{upper_var}={value}",
                    "--build-arg",
                    f"{lower_var}={value}",
                ]
            )

    return proxy_args


def setup_buildx_builder(builder_name="multiarch", dry_run=False):
    """Setup Docker buildx builder for multi-architecture builds."""
    print(f"🔧 Setting up buildx builder: {builder_name}")

    # Check if builder exists
    result = run_command(
        f"docker buildx ls | grep {builder_name}", check=False, dry_run=dry_run
    )
    if result.returncode != 0:
        # Create new builder with proxy support
        driver_opts = ""
        if os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"):
            print("📡 Detected proxy settings, configuring builder...")
            # For buildx, we need to configure the builder to use proxy
            driver_opts = "--driver-opt network=host"

        create_cmd = f"docker buildx create --name {builder_name} --platform linux/amd64,linux/arm64 {driver_opts}"
        run_command(create_cmd, dry_run=dry_run)

    # Use the builder
    run_command(f"docker buildx use {builder_name}", dry_run=dry_run)

    # Bootstrap the builder
    run_command("docker buildx inspect --bootstrap", dry_run=dry_run)


def build_and_push_image_buildx(
    image_name, version, platforms="linux/amd64,linux/arm64", dry_run=False
):
    """Build and push multi-architecture Docker image using buildx."""
    print(f"🐳 Building and pushing Docker image (buildx): {image_name}:{version}")

    # Get proxy build arguments
    proxy_args = get_proxy_build_args()
    if proxy_args:
        print(
            f"📡 Using proxy settings: {len(proxy_args) // 2} proxy variables detected"
        )

    # Build command components
    build_cmd_parts = [
        "docker buildx build",
        f"--platform {platforms}",
        f"--tag {image_name}:{version}",
        f"--tag {image_name}:latest",
    ]

    # Add proxy build args
    if proxy_args:
        build_cmd_parts.extend(proxy_args)

    # Add final arguments
    build_cmd_parts.extend(["--push", "."])

    build_cmd = " ".join(build_cmd_parts)
    run_command(build_cmd, dry_run=dry_run)


def build_and_push_image_traditional(image_name, version, dry_run=False):
    """Build and push Docker image using traditional docker build."""
    print(f"🐳 Building and pushing Docker image (traditional): {image_name}:{version}")
    print("⚠️  Note: Traditional build only supports current platform architecture")

    # Get proxy build arguments
    proxy_args = get_proxy_build_args()
    if proxy_args:
        print(
            f"📡 Using proxy settings: {len(proxy_args) // 2} proxy variables detected"
        )

    # Build command components
    build_cmd_parts = [
        "docker build",
        f"-t {image_name}:{version}",
        f"-t {image_name}:latest",
    ]

    # Add proxy build args
    if proxy_args:
        build_cmd_parts.extend(proxy_args)

    # Add final argument
    build_cmd_parts.append(".")

    build_cmd = " ".join(build_cmd_parts)
    run_command(build_cmd, dry_run=dry_run)

    # Push version tag
    push_cmd_version = f"docker push {image_name}:{version}"
    run_command(push_cmd_version, dry_run=dry_run)

    # Push latest tag
    push_cmd_latest = f"docker push {image_name}:latest"
    run_command(push_cmd_latest, dry_run=dry_run)


def build_and_push_multiarch_traditional(
    image_name, version, platforms="linux/amd64,linux/arm64", dry_run=False
):
    """Build and push multi-architecture Docker image using traditional docker build + manifest."""
    print(
        f"🐳 Building multi-architecture Docker image (traditional + manifest): {image_name}:{version}"
    )
    print(
        "📋 This will create platform-specific tags and combine them using docker manifest"
    )

    # Parse platforms
    platform_list = [p.strip() for p in platforms.split(",")]

    # Get proxy build arguments
    proxy_args = get_proxy_build_args()
    if proxy_args:
        print(
            f"📡 Using proxy settings: {len(proxy_args) // 2} proxy variables detected"
        )

    # Check if manifest command is available
    if not check_docker_manifest():
        print(
            "❌ Docker manifest command not available. Please enable experimental features."
        )
        print("💡 Run: echo '{\"experimental\": true}' > ~/.docker/config.json")
        sys.exit(1)

    # Build images for each platform
    platform_tags = []
    for platform in platform_list:
        # Convert platform to tag suffix (e.g., linux/amd64 -> amd64)
        arch = platform.split("/")[-1]
        platform_tag = f"{image_name}:{version}-{arch}"
        platform_tags.append(platform_tag)

        print(f"🏗️  Building for platform: {platform}")

        # Build command components
        build_cmd_parts = [
            "docker build",
            f"--platform {platform}",
            f"-t {platform_tag}",
        ]

        # Add proxy build args
        if proxy_args:
            build_cmd_parts.extend(proxy_args)

        # Add final argument
        build_cmd_parts.append(".")

        build_cmd = " ".join(build_cmd_parts)
        run_command(build_cmd, dry_run=dry_run)

        # Push platform-specific tag
        push_cmd = f"docker push {platform_tag}"
        run_command(push_cmd, dry_run=dry_run)

    # Create and push manifest for version tag
    print(f"📋 Creating manifest for {image_name}:{version}")

    # Remove existing manifest if it exists
    rm_manifest_cmd = f"docker manifest rm {image_name}:{version}"
    run_command(rm_manifest_cmd, check=False, dry_run=dry_run)

    manifest_cmd = (
        f"docker manifest create {image_name}:{version} {' '.join(platform_tags)}"
    )
    run_command(manifest_cmd, dry_run=dry_run)

    # Push manifest
    manifest_push_cmd = f"docker manifest push {image_name}:{version}"
    run_command(manifest_push_cmd, dry_run=dry_run)

    # Create and push manifest for latest tag
    print(f"📋 Creating manifest for {image_name}:latest")

    # Remove existing manifest if it exists
    rm_manifest_latest_cmd = f"docker manifest rm {image_name}:latest"
    run_command(rm_manifest_latest_cmd, check=False, dry_run=dry_run)

    manifest_latest_cmd = (
        f"docker manifest create {image_name}:latest {' '.join(platform_tags)}"
    )
    run_command(manifest_latest_cmd, dry_run=dry_run)

    # Push latest manifest
    manifest_latest_push_cmd = f"docker manifest push {image_name}:latest"
    run_command(manifest_latest_push_cmd, dry_run=dry_run)

    print(
        "✅ Multi-architecture image created successfully using traditional build + manifest"
    )


def verify_image_pushed(image_name, version, dry_run=False):
    """Verify that the image was successfully pushed."""
    if dry_run:
        print(f"🔍 [DRY RUN] Would verify image: {image_name}:{version}")
        return

    print(f"🔍 Verifying image: {image_name}:{version}")

    # Try to pull the image to verify it exists
    result = run_command(f"docker pull {image_name}:{version}", check=False)
    if result.returncode != 0:
        print(f"Warning: Could not verify image {image_name}:{version}")
        return False

    # Check manifest for multiple architectures
    result = run_command(f"docker manifest inspect {image_name}:{version}", check=False)
    if result.returncode == 0:
        try:
            manifest = json.loads(result.stdout)
            if "manifests" in manifest:
                architectures = [
                    m["platform"]["architecture"] for m in manifest["manifests"]
                ]
                print(f"✅ Image supports architectures: {', '.join(architectures)}")
                return True
        except json.JSONDecodeError:
            pass

    print("✅ Image verification completed")
    return True


def print_proxy_status():
    """Print current proxy configuration."""
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "ALL_PROXY"]

    found_proxy = False
    for var in proxy_vars:
        value = os.getenv(var) or os.getenv(var.lower())
        if value:
            if not found_proxy:
                print("📡 Proxy configuration detected:")
                found_proxy = True
            print(f"  {var}: {value}")

    if not found_proxy:
        print("⚠️  No proxy configuration detected")
        print(
            "💡 If you need proxy support, set HTTP_PROXY/HTTPS_PROXY environment variables"
        )


def main():
    """Main Docker release process."""
    parser = argparse.ArgumentParser(
        description="Release ModelScope MCP Server to Docker Hub"
    )
    parser.add_argument(
        "--image-name",
        default="spadrian/modelscope-mcp-server",
        help="Docker image name (default: spadrian/modelscope-mcp-server)",
    )
    parser.add_argument(
        "--platforms",
        default="linux/amd64,linux/arm64",
        help="Target platforms (default: linux/amd64,linux/arm64)",
    )
    parser.add_argument(
        "--builder-name",
        default="multiarch",
        help="Buildx builder name (default: multiarch)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip image verification after push",
    )
    parser.add_argument(
        "--force-traditional",
        action="store_true",
        help="Force use of traditional docker build instead of buildx",
    )
    parser.add_argument(
        "--traditional-multiarch",
        action="store_true",
        help="Use traditional docker build with manifest for multi-architecture support",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual changes will be made")

    print("🚀 Starting Docker Hub release process...")

    # 1. Get current version
    try:
        version = get_current_version()
        print(f"📦 Current version: {version}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 2. Print proxy status
    print_proxy_status()

    # 3. Determine build method
    use_buildx = False
    use_traditional_multiarch = args.traditional_multiarch

    if args.force_traditional:
        print("🔧 Forced traditional build (single platform)")
    elif use_traditional_multiarch:
        print("🔧 Using traditional build with manifest for multi-architecture")
        # Check if manifest is available
        if not check_docker_manifest():
            print("❌ Docker manifest command not available")
            print(
                "💡 Enable experimental features: echo '{\"experimental\": true}' > ~/.docker/config.json"
            )
            sys.exit(1)
    else:
        # Check Docker buildx availability
        use_buildx = check_docker_buildx()
        if use_buildx:
            print("✅ Docker buildx is available - using multi-architecture build")
        else:
            print(
                "⚠️  Docker buildx is not available - falling back to traditional build"
            )

    # 4. Check if user is logged in to Docker Hub
    if not args.dry_run:
        result = run_command("docker info | grep Username", check=False)
        if result.returncode != 0:
            print("❌ Please login to Docker Hub first: docker login")
            sys.exit(1)

    # 5. Setup buildx builder (if using buildx)
    if use_buildx:
        setup_buildx_builder(args.builder_name, args.dry_run)

    # 6. Build and push image
    if use_buildx:
        build_and_push_image_buildx(
            args.image_name, version, args.platforms, args.dry_run
        )
    elif use_traditional_multiarch:
        build_and_push_multiarch_traditional(
            args.image_name, version, args.platforms, args.dry_run
        )
    else:
        build_and_push_image_traditional(args.image_name, version, args.dry_run)

    # 7. Verify image was pushed
    if not args.skip_verification:
        verify_image_pushed(args.image_name, version, args.dry_run)

    print(f"✅ Successfully released Docker image: {args.image_name}:{version}")

    # Fix URL generation - remove the incorrect replacement
    if "/" in args.image_name:
        hub_url = f"https://hub.docker.com/r/{args.image_name}"
    else:
        hub_url = f"https://hub.docker.com/r/{args.image_name}"

    print(f"🔗 Image URL: {hub_url}")

    # 8. Post-release instructions
    print("\n📝 Next steps:")
    print(f"1. Test the image: docker run --rm {args.image_name}:{version} --help")
    if use_buildx or use_traditional_multiarch:
        print(
            f"2. Test multi-arch: docker run --platform linux/arm64 --rm {args.image_name}:{version} --help"
        )
    print("3. Update README.md with new Docker Hub instructions")
    print("4. Create GitHub release if needed")


if __name__ == "__main__":
    main()
