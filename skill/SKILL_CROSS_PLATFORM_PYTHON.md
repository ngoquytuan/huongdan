# Skill: Cross-Platform Python Development (Windows & Ubuntu)

## Overview
Best practices and solutions for developing Python applications that run reliably on both Windows and Ubuntu, with focus on Streamlit applications and file system interactions.

**Created:** 2026-01-28
**Context:** FR-03.1 v7 - Vietnamese Document Processing System
**Primary Issue Solved:** Streamlit infinite loop on Ubuntu due to file watcher

---

## Critical Differences: Windows vs Ubuntu

### File System Monitoring

| Aspect | Windows | Ubuntu/Linux |
|--------|---------|--------------|
| **File Watcher** | Polling-based, less sensitive | inotify - aggressive, catches every operation |
| **Triggers on** | File modifications | File open, close, modify, create, move |
| **Bytecode Creation** | Less problematic | Triggers file watcher during imports |
| **Performance Impact** | Lower | Higher (more CPU-intensive) |

### Python Behavior

| Aspect | Windows | Ubuntu/Linux |
|--------|---------|--------------|
| **Bytecode Location** | `__pycache__/` | `__pycache__/` |
| **Creation Timing** | On import | On import (triggers inotify) |
| **Path Separators** | `\` or `/` (both work) | `/` only |
| **Line Endings** | CRLF (`\r\n`) | LF (`\n`) |
| **Case Sensitivity** | No | Yes |

---

## The Streamlit Infinite Loop Problem

### Symptom
```
2026-01-26 20:57:34,216 [INFO] APP START
2026-01-26 20:57:34,300 [INFO] APP START  ← 84ms later
2026-01-26 20:57:34,382 [INFO] APP START  ← 82ms later
2026-01-26 20:57:34,463 [INFO] APP START  ← 81ms later
...repeats forever...
```

### Root Cause
1. Streamlit uses file watcher to detect code changes and auto-reload
2. On Ubuntu, inotify monitors ALL file system operations
3. When Python imports modules, it creates `.pyc` files in `__pycache__/`
4. inotify detects these files → Streamlit reloads → imports again → creates more `.pyc` files → infinite loop
5. Logging to files also triggers inotify on every log write

### Why It Works on Windows
Windows file watcher is polling-based and less aggressive. It typically:
- Debounces file changes (waits before triggering)
- Ignores certain file patterns by default
- Has longer polling intervals

---

## Solution Pattern: `@st.cache_resource`

### The Fix

**❌ BROKEN (causes infinite loop on Ubuntu):**
```python
import logging
import os

LOG_DIR = '.logs'
LOG_FILE = os.path.join(LOG_DIR, 'app_debug.log')

# This runs on EVERY Streamlit rerun
if not logging.getLogger().hasHandlers():
    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    # ... setup handlers ...
    logging.basicConfig(handlers=[file_handler])

logger = logging.getLogger(__name__)
```

**Problem:** Even with the `if not hasHandlers()` check, the file system operations (makedirs, FileHandler creation) happen at module level on every rerun, triggering inotify.

---

**✅ FIXED (works on both Windows and Ubuntu):**
```python
import streamlit as st
import logging

# Use @st.cache_resource to run ONCE and cache the result
@st.cache_resource
def setup_logging():
    import os
    os.makedirs('.logs', exist_ok=True)

    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        root_logger.setLevel(logging.DEBUG)

        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        root_logger.addHandler(stream_handler)

        # File handler
        file_handler = logging.FileHandler('.logs/app_debug.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)

# Call once, result is cached
logger = setup_logging()
```

**Why this works:**
- `@st.cache_resource` runs the function ONCE on first execution
- Returns cached result on subsequent reruns
- No file operations after first run = no inotify triggers
- No infinite loop

---

## Streamlit Caching Decorators

### `@st.cache_resource` vs `@st.cache_data`

| Decorator | Use For | Example | Thread-Safe |
|-----------|---------|---------|-------------|
| `@st.cache_resource` | **Global resources** (singletons) | Database connections, loggers, ML models, API clients | No (same instance shared) |
| `@st.cache_data` | **Immutable data** (copies) | DataFrames, lists, dicts, API responses | Yes (returns copies) |

### When to Use `@st.cache_resource`

✅ **Use for:**
- Logging setup
- Database connection pools
- ML model loading
- File system monitors
- API client initialization
- Thread pools
- Cache managers

❌ **Don't use for:**
- User-specific data
- Session-dependent values
- Data that changes per user
- Mutable objects that need isolation

### Example: Database Connection
```python
@st.cache_resource
def get_database_connection():
    """Create database connection ONCE, reuse forever"""
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="user",
        password="pass"
    )
    return conn

# All users share the same connection
db = get_database_connection()
```

---

## Configuration: .streamlit/config.toml

### Essential Settings for Ubuntu

```toml
[server]
# CRITICAL: Disable file watcher on Ubuntu
fileWatcherType = "none"

# Optional: Allow manual rerun
runOnSave = true

[browser]
# Disable analytics
gatherUsageStats = false

[runner]
# Enable fast reruns for better performance
fastReruns = true

# Optional: Disable magic commands if not needed
magicEnabled = false
```

### File Watcher Types

| Type | Behavior | Use Case |
|------|----------|----------|
| `"none"` | No file watching | Production, Ubuntu deployments |
| `"auto"` | Automatic detection | Development (risky on Ubuntu) |
| `"poll"` | Polling-based | Development on slow filesystems |
| `"watchdog"` | Watchdog library | Development on macOS/Windows |

**Recommendation:** Always use `"none"` for production deployments, especially on Ubuntu.

---

## Environment Variables

### Prevent Bytecode Generation

**Add to shell startup (`~/.bashrc` or `~/.profile`):**
```bash
# Prevent Python bytecode generation
export PYTHONDONTWRITEBYTECODE=1

# Unbuffered output for better logging
export PYTHONUNBUFFERED=1
```

**Or in launch script:**
```bash
#!/bin/bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
streamlit run app.py --server.fileWatcherType none
```

### Why This Helps

| Variable | Effect | Benefit |
|----------|--------|---------|
| `PYTHONDONTWRITEBYTECODE=1` | Prevents `.pyc` file creation | No `__pycache__/` triggers |
| `PYTHONUNBUFFERED=1` | No buffering on stdout/stderr | Real-time logs |

---

## Best Practices

### 1. Code Structure

**✅ DO:**
```python
import streamlit as st

# Page config MUST be first Streamlit command
st.set_page_config(page_title="App", layout="wide")

# Then other imports
import logging
import pandas as pd

# Setup resources with caching
@st.cache_resource
def setup_logging():
    # ... logging setup ...
    return logger

logger = setup_logging()

# Main app code
def main():
    st.title("My App")
    # ... app logic ...

if __name__ == "__main__":
    main()
```

**❌ DON'T:**
```python
import streamlit as st
import logging

# Creating file handlers at module level
file_handler = logging.FileHandler('app.log')  # BAD: runs every rerun
logging.basicConfig(handlers=[file_handler])

# Page config after other Streamlit commands
st.title("My App")  # BAD: st.title before set_page_config
st.set_page_config(page_title="App")  # ERROR!
```

### 2. File Operations

**✅ DO:**
```python
@st.cache_resource
def initialize_directories():
    """Create directories once"""
    import os
    os.makedirs('.logs', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    return True

# Call once
initialize_directories()
```

**❌ DON'T:**
```python
import os

# Runs on every rerun
os.makedirs('.logs', exist_ok=True)  # BAD: triggers inotify
os.makedirs('output', exist_ok=True)
```

### 3. Logging Best Practices

**✅ DO:**
```python
@st.cache_resource
def setup_logging():
    import logging
    import os

    os.makedirs('.logs', exist_ok=True)

    logger = logging.getLogger(__name__)

    # Check if already configured
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # File handler with rotation (prevents huge log files)
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            '.logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        )
        logger.addHandler(handler)

    return logger

logger = setup_logging()
```

**❌ DON'T:**
```python
import logging

# No caching, runs every time
logging.basicConfig(
    filename='app.log',  # BAD: opens file on every rerun
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)
```

### 4. Database Connections

**✅ DO:**
```python
@st.cache_resource
def get_db_connection():
    """Create connection pool once"""
    import psycopg2.pool

    pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host="localhost",
        database="mydb"
    )
    return pool

db_pool = get_db_connection()

def query_database(sql):
    """Use pooled connection"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)
```

**❌ DON'T:**
```python
import psycopg2

# Creates new connection on every rerun
conn = psycopg2.connect(host="localhost", database="mydb")  # BAD: resource leak

def query_database(sql):
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()
```

---

## Launch Scripts

### Ubuntu/Linux Script

**File:** `run_app.sh`
```bash
#!/bin/bash
# Cross-platform Streamlit launcher for Ubuntu

cd "$(dirname "$0")"

echo "Starting Streamlit App..."

# Disable bytecode generation
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run with file watcher disabled
streamlit run app.py \
    --server.fileWatcherType none \
    --server.port 8501 \
    --server.headless true

echo "App stopped."
```

**Make executable:**
```bash
chmod +x run_app.sh
./run_app.sh
```

### Windows Script

**File:** `run_app.bat`
```batch
@echo off
cd /d "%~dp0"

echo Starting Streamlit App...

:: Set environment variables
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUNBUFFERED=1

:: Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Run Streamlit
python -m streamlit run app.py --server.port 8501

echo App stopped.
pause
```

**Run:**
```cmd
run_app.bat
```

---

## Debugging Infinite Loops

### Detection

**Symptoms:**
- App constantly shows "Rerunning..." in browser
- High CPU usage from Python/Streamlit process
- Log file grows rapidly (multiple entries per second)
- Cannot interact with UI
- Browser becomes unresponsive

**Quick Check:**
```bash
# Monitor log file
tail -f .logs/app_debug.log

# If you see rapid entries (< 100ms apart), you have a loop
# Good: Entries every few seconds (on user interaction)
# Bad: Entries every 50-100ms (infinite loop)
```

### Diagnosis Steps

1. **Check file watcher events (Ubuntu only):**
```bash
# Install inotify tools
sudo apt-get install inotify-tools

# Monitor file changes
inotifywait -m -r --format '%w%f %e' . | grep -v __pycache__
```

2. **Check Streamlit processes:**
```bash
# List all Streamlit processes
ps aux | grep streamlit

# Should see only ONE process
# Multiple processes = previous runs didn't stop
```

3. **Check for __pycache__ creation:**
```bash
# Watch for new bytecode files
watch -n 1 'find . -name "*.pyc" -mmin -1 | wc -l'

# If count keeps increasing, bytecode is being regenerated
```

4. **Check config:**
```bash
streamlit config show | grep fileWatcherType
# Should output: fileWatcherType = "none"
```

### Solutions (in order of preference)

1. **Add `@st.cache_resource` to resource initialization** ⭐ PRIMARY FIX
2. **Set `fileWatcherType = "none"` in `.streamlit/config.toml`**
3. **Export `PYTHONDONTWRITEBYTECODE=1`**
4. **Pre-compile all Python files:** `python -m compileall -q .`
5. **Kill existing processes:** `pkill -9 streamlit`

---

## Testing Cross-Platform

### Test Checklist

**Before deployment:**

- [ ] Test on Windows (development machine)
- [ ] Test on Ubuntu (production environment)
- [ ] Upload file test (most common trigger)
- [ ] Process document test (full workflow)
- [ ] Check logs for infinite loops
- [ ] Monitor CPU usage (should be low when idle)
- [ ] Test with/without virtual environment
- [ ] Test after server restart
- [ ] Test with multiple browser tabs
- [ ] Test with different file types

### Automated Test Script

**File:** `test_platform.py`
```python
#!/usr/bin/env python3
"""Test cross-platform compatibility"""

import os
import sys
import subprocess
import time

def test_streamlit_starts():
    """Test if Streamlit can start without errors"""
    print("Testing Streamlit startup...")

    # Set environment
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    # Start Streamlit
    proc = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run', 'app.py',
         '--server.fileWatcherType', 'none',
         '--server.port', '8502',
         '--server.headless', 'true'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for startup
    time.sleep(5)

    # Check if still running
    if proc.poll() is None:
        print("✅ Streamlit started successfully")
        proc.terminate()
        return True
    else:
        stdout, stderr = proc.communicate()
        print(f"❌ Streamlit failed to start")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return False

def test_no_pycache():
    """Test that __pycache__ isn't created during runtime"""
    print("Testing bytecode generation...")

    # Clean first
    os.system('find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null')

    # Import a module
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    subprocess.run(
        [sys.executable, '-c', 'import app'],
        env=env,
        capture_output=True
    )

    # Check for __pycache__
    result = subprocess.run(
        ['find', '.', '-type', 'd', '-name', '__pycache__'],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print(f"❌ Found __pycache__: {result.stdout}")
        return False
    else:
        print("✅ No __pycache__ created")
        return True

if __name__ == '__main__':
    print(f"Testing on {sys.platform}")
    print("=" * 50)

    results = []
    results.append(test_streamlit_starts())
    results.append(test_no_pycache())

    print("=" * 50)
    if all(results):
        print("✅ All tests passed")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
```

**Run:**
```bash
python test_platform.py
```

---

## Common Pitfalls

### 1. Page Config After Other Commands

**❌ ERROR:**
```python
import streamlit as st

st.title("My App")  # First Streamlit command
st.set_page_config(page_title="App")  # ERROR: Must be first!
```

**✅ CORRECT:**
```python
import streamlit as st

st.set_page_config(page_title="App")  # MUST be first
st.title("My App")
```

### 2. File Operations at Module Level

**❌ BAD:**
```python
import os

# Runs every rerun
os.makedirs('output', exist_ok=True)
```

**✅ GOOD:**
```python
@st.cache_resource
def ensure_directories():
    import os
    os.makedirs('output', exist_ok=True)
    return True

ensure_directories()
```

### 3. Forgetting to Activate Virtual Environment

**❌ BAD:**
```bash
# Running without venv
streamlit run app.py  # May use system Python
```

**✅ GOOD:**
```bash
source .venv/bin/activate  # or venv/Scripts/activate on Windows
streamlit run app.py
```

### 4. Hard-coding Path Separators

**❌ BAD:**
```python
log_path = '.logs\\app.log'  # Windows only
```

**✅ GOOD:**
```python
import os
log_path = os.path.join('.logs', 'app.log')  # Cross-platform
```

---

## Quick Reference Card

### When You See Infinite Loop on Ubuntu:

1. **Stop the app:** `Ctrl+C` or `pkill -9 streamlit`
2. **Check:** Is logging/resource setup using `@st.cache_resource`?
3. **Check:** Is `.streamlit/config.toml` set to `fileWatcherType = "none"`?
4. **Check:** Are you setting `PYTHONDONTWRITEBYTECODE=1`?
5. **Clean:** `find . -name "*.pyc" -delete`
6. **Restart:** `./run_app.sh`

### Pattern to Remember:

```python
# ANY resource that touches the file system
# should be wrapped in @st.cache_resource

@st.cache_resource
def initialize_something():
    # File operations
    # Database connections
    # Logging setup
    # API clients
    # etc.
    return resource

resource = initialize_something()  # Cached, runs once
```

---

## Related Resources

- [Streamlit Caching Docs](https://docs.streamlit.io/library/advanced-features/caching)
- [Python bytecode compilation](https://docs.python.org/3/library/py_compile.html)
- [Linux inotify](https://man7.org/linux/man-pages/man7/inotify.7.html)

---

**Version:** 1.0
**Last Updated:** 2026-01-28
**Tested On:** Windows 11, Ubuntu 20.04+
**Python Version:** 3.10+
**Streamlit Version:** 1.18.0+
