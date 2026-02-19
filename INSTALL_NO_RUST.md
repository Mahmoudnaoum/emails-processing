# Installation Guide - No Rust Required

This guide helps you install the Email Relationship Analysis System without needing Rust.

## Quick Install (Recommended)

```bash
pip install -r requirements_no_rust.txt
```

This uses pure Python libraries that don't require any compilation.

## What's Included

- **psycopg2-cffi**: Pure Python PostgreSQL driver (no C compilation)
- **fastapi**: Modern web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **email-validator**: Email parsing

## Why This Works

The `requirements_no_rust.txt` file uses `psycopg2-cffi` instead of `psycopg2-binary`. This is a pure Python implementation that:
- Doesn't require Rust
- Doesn't require C compilation
- Works on all platforms
- Has the same API as psycopg2

## Alternative Options

If you have issues with the above, try:

**Option 1: Pre-compiled binary**
```bash
pip install -r requirements_retool_simple.txt
```

**Option 2: Try installing with wheel**
```bash
pip install --only-binary :all: psycopg2-binary
```

**Option 3: Install from conda (if you use conda)**
```bash
conda install -c conda-forge psycopg2
pip install fastapi uvicorn pydantic email-validator
```

## Verification

After installation, verify everything works:

```bash
python -c "import psycopg2cffi; print('✅ PostgreSQL driver installed')"
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import uvicorn; print('✅ Uvicorn installed')"
```

## Next Steps

1. Configure your database connection:
```bash
cp .env.example .env
# Edit .env with your Retool database credentials
```

2. Run the setup script:
```bash
python setup_retool.py
```

3. Test the system:
```bash
python test_retool_system.py
```

## Troubleshooting

### Error: "No module named 'psycopg2cffi'"

```bash
pip install psycopg2-cffi
```

### Error: "No module named 'cffi'"

```bash
pip install cffi pycparser
```

### Error: "Failed building wheel"

Try the pure Python version again:
```bash
pip uninstall psycopg2-binary psycopg2
pip install psycopg2-cffi
```

## Still Having Issues?

1. Make sure you're using Python 3.8 or later
2. Try upgrading pip: `python -m pip install --upgrade pip`
3. Use a virtual environment: `python -m venv .venv && .venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)
4. Check that all dependencies are installed: `pip list`

## Full Installation Command

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies (no Rust required)
pip install -r requirements_no_rust.txt

# Verify installation
python setup_retool.py
```
