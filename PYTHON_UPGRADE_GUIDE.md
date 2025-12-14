# Python 3.9+ Upgrade Guide

## Current Status
Your virtual environment is using **Python 3.8**, which is incompatible with the latest `yfinance` package.

## Steps to Upgrade

### 1. Download Python 3.9+

Visit: https://www.python.org/downloads/

**Recommended:** Python 3.11 or 3.12 (Latest stable)

**Important:** During installation:
- ✅ Check "Add Python to PATH"
- ✅ Check "Install for all users" (optional)

### 2. Verify Installation

After installing, open a **NEW** terminal/PowerShell:

```bash
python --version
# Should show: Python 3.11.x or 3.12.x
```

If it still shows 3.8, try:
```bash
python3 --version
# or
py --version
```

### 3. Delete Old Virtual Environment

```bash
cd C:\Users\katuk\OneDrive\Desktop\projects\agentic
Remove-Item -Recurse -Force .venv
```

### 4. Create New Virtual Environment (Python 3.9+)

```bash
# Using the new Python version
python -m venv .venv

# Or if python still points to 3.8:
python3.11 -m venv .venv
# or
py -3.11 -m venv .venv
```

### 5. Activate Virtual Environment

```bash
.\.venv\Scripts\Activate.ps1
```

### 6. Verify Virtual Environment Python Version

```bash
python --version
# Should now show 3.9+ inside the venv
```

### 7. Install Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

This will install yfinance and all other dependencies with Python 3.9+ compatibility.

### 8. Test the System

```bash
# Go back to project root
cd ..

# Run the real-time analysis with actual Yahoo Finance data
python analyze_stock_realtime.py --symbol RELIANCE
```

---

## Quick Commands (Copy & Paste)

### For PowerShell:
```powershell
# Step 1: Remove old venv
Remove-Item -Recurse -Force .venv

# Step 2: Create new venv with Python 3.11+
python -m venv .venv

# Step 3: Activate
.\.venv\Scripts\Activate.ps1

# Step 4: Install dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Step 5: Test
python analyze_stock_realtime.py --symbol RELIANCE
```

---

## Troubleshooting

### Issue: "python still shows 3.8"
**Solution:** Use specific version:
```bash
py -3.11 -m venv .venv
# or
python3.11 -m venv .venv
```

### Issue: "Multiple Python versions installed"
**Solution:** Use `py` launcher:
```bash
py --list  # Shows all installed versions
py -3.11 -m venv .venv  # Use specific version
```

### Issue: "Cannot activate venv"
**Solution:** Run PowerShell as Administrator:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## After Upgrade Benefits

✅ **Real Yahoo Finance Data** - Live market prices  
✅ **No Mock Data** - Actual stock information  
✅ **Latest Features** - Access to newest yfinance features  
✅ **Better Performance** - Python 3.9+ optimizations  

---

## Alternative: Use Docker (Advanced)

If you prefer not to change your system Python:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "analyze_stock_realtime.py"]
```

---

**Need help with the upgrade? Let me know which step you're on!**
