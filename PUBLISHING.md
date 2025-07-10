# Publishing Guide

## Quick Publishing

Use the provided publishing script:

```bash
# Run the publishing script
python scripts/publish.py
```

## Manual Publishing Steps

### 1. Preparation

#### Install Build Tools

```bash
# Install necessary build tools
uv add --dev build twine

# Or use pip
pip install build twine
```

#### Create PyPI Account

1. Visit <https://pypi.org/> to register an account
2. Visit <https://pypi.org/manage/account/token/> to create an API Token
3. Save the API Token for later use

### 2. Publishing Steps

#### 1. Prepare for Release

```bash
# Make sure code is committed
git add .
git commit -m "Prepare for release version 0.1.0"
git push origin main

# Create tag
git tag v0.1.0
git push origin v0.1.0
```

#### 2. Build Package

```bash
# Clean previous builds
rm -rf dist/ build/

# Build package
python -m build

# Or use uv
uv build
```

#### 3. Check Package

```bash
# Check package integrity
twine check dist/*

# Verify package contents
tar -tzf dist/modelscope_mcp_server-0.1.0.tar.gz
```

#### 4. Upload to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Will prompt for username and password
# Username: __token__
# Password: Your API Token
```

#### 5. Verify Publication

```bash
# Wait a few minutes then test installation
uvx modelscope-mcp-server

# Or
pip install modelscope-mcp-server
```

## Automated Publishing (Optional)

### Using GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

Remember to add `PYPI_API_TOKEN` in your GitHub repository's Settings > Secrets.

## Version Management

### Update Version

1. Update version number in `pyproject.toml`
2. Commit changes
3. Create new tag
4. Repeat publishing steps

### Semantic Versioning

- `0.1.0` - Initial version
- `0.1.1` - Patch version (bug fixes)
- `0.2.0` - Minor version (new features)
- `1.0.0` - Major version (breaking changes)

## Verify Publication

After publishing, users can use your package through:

```bash
# Use uvx to run directly (recommended)
uvx modelscope-mcp-server

# Or install then run
pip install modelscope-mcp-server
modelscope-mcp-server
```

## Troubleshooting

### Common Issues

1. **Package name already exists**: Change package name in `pyproject.toml`
2. **Version number conflict**: Increment version number and republish
3. **Authentication failure**: Check if API Token is correct
4. **Build failure**: Ensure project structure is correct and dependencies are complete

### Useful Commands

```bash
# Test local installation
pip install -e .

# Check package information
python -m pip show modelscope-mcp-server

# Verify entry point
python -c "import modelscope_mcp_server; print(modelscope_mcp_server.__version__)"
```
