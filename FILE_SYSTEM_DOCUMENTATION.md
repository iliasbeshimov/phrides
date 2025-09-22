# File System & Dependencies Documentation

## 📁 Complete File Structure

### Current Project Directory:
`/Users/iliasbeshimov/My Drive/Personal GDrive/Startup and Biz Projects/phrides.com car leasing help/Auto Contacting/`

```
Auto Contacting/
├── 📄 REQUIRED CORE FILES
│   ├── Dealerships - Jeep.csv                    # ⭐ PRIMARY DATA SOURCE
│   ├── enhanced_stealth_browser_config.py        # ⭐ BROWSER MANAGER (REQUIRED)
│   ├── final_retest_with_contact_urls.py         # ⭐ BEST PRODUCTION SCRIPT
│   └── contact_page_detector.py                  # ⭐ BACKUP PRODUCTION SCRIPT
│
├── 📄 WORKING SCRIPTS (TESTED & VALIDATED)
│   ├── gravity_forms_detector.py                 # Gravity Forms testing/debug
│   ├── debug_direct_contact_test.py              # Individual site testing
│   ├── complete_50_test.py                       # Original successful test
│   └── universal_form_analyzer.py                # Advanced form analysis
│
├── 📄 EXPERIMENTAL/HISTORICAL SCRIPTS
│   ├── retest_failed_dealerships.py              # Failed implementation (reference)
│   ├── resume_50_test.py                         # Failed resume attempt (reference)
│   ├── enhanced_contact_detector.py              # Development version
│   ├── smart_form_detector.py                    # Experimental features
│   ├── focused_20_dealer_test.py                 # Small batch testing
│   ├── robust_50_dealer_test.py                  # Alternative approach
│   ├── final_test_50_dealerships.py              # Earlier version
│   ├── final_validation_test_third_set.py        # Validation testing
│   ├── ultra_enhanced_detector.py                # Advanced features test
│   └── validation_test_20_new.py                 # Validation batch
│
├── 📄 DOCUMENTATION
│   ├── DEALERSHIP_CONTACT_AUTOMATION_DOCUMENTATION.md  # Complete technical docs
│   ├── QUICK_REFERENCE_GUIDE.md                       # Immediate action guide
│   ├── FILE_SYSTEM_DOCUMENTATION.md                   # This file
│   ├── CLAUDE.md                                      # Project instructions
│   ├── ARCHITECTURE.md                                # System design
│   ├── PROJECT_WORKFLOW.md                            # User workflow
│   ├── UI_COMPONENTS.md                               # Frontend specs
│   ├── TRACKING_SYSTEM.md                             # Status tracking
│   ├── API_ENDPOINTS.md                               # API specification
│   ├── LOGGING_SYSTEM.md                              # Logging system
│   └── DETECTION_RATE_ANALYSIS.md                     # Performance analysis
│
└── 📁 tests/                                          # TEST RESULTS DIRECTORY
    ├── final_retest_contact_urls_[timestamp]/         # Latest successful test
    ├── enhanced_detection_[timestamp]/                # Historical test results
    ├── complete_50_dealerships_[timestamp]/           # Original interrupted test
    ├── contact_page_navigation_[timestamp]/           # Navigation strategy test
    ├── validation_test_20_new_[timestamp]/            # Validation results
    └── universal_analysis_[timestamp]/                # Advanced analysis results
```

---

## 🔧 Critical Dependencies & Requirements

### 1. **REQUIRED FILES** (Cannot run without these)

#### `Dealerships - Jeep.csv` ⭐ **ESSENTIAL DATA SOURCE**
**Location**: Root directory
**Purpose**: Primary dealership database
**Format**: CSV with required columns
**Size**: 1000+ dealership records

**Required Columns:**
```csv
dealer_name,website,city,state,phone,latitude,longitude
```

**Sample Data:**
```csv
dealer_name,website,city,state,phone
Thomas Garage Inc,https://www.thomasautocenters.com,Thomas,WV,304-463-4193
Autonation Chrysler,https://www.autonationchryslerdodgejeepramsouthwest.com,Houston,TX,713-981-1943
```

#### `enhanced_stealth_browser_config.py` ⭐ **ESSENTIAL BROWSER MANAGER**
**Location**: Root directory
**Purpose**: Browser automation and stealth configuration
**Dependencies**: Playwright, asyncio
**Status**: REQUIRED - No script can run without this

**Key Class:**
```python
class EnhancedStealthBrowserManager:
    async def create_enhanced_stealth_context(self, browser):
        # Anti-detection configuration
        # User agent management
        # Browser context setup
```

### 2. **PRODUCTION SCRIPTS** (Ready to use)

#### `final_retest_with_contact_urls.py` ⭐ **PRIMARY PRODUCTION SCRIPT**
**Success Rate**: 81.8% (9/11 sites)
**Strategy**: Direct contact URL navigation
**Use Case**: Most reliable detection for known contact URL patterns

**Dependencies:**
- `enhanced_stealth_browser_config.py`
- `Dealerships - Jeep.csv`
- Playwright
- pandas
- asyncio

**Command:**
```bash
python final_retest_with_contact_urls.py
```

#### `contact_page_detector.py` ⭐ **BACKUP PRODUCTION SCRIPT**
**Success Rate**: 75% (30/40 sites)
**Strategy**: Homepage → contact page navigation
**Use Case**: When contact URL patterns unknown

**Dependencies:**
- `enhanced_stealth_browser_config.py`
- `Dealerships - Jeep.csv`
- Playwright
- pandas
- asyncio

### 3. **DEBUG/UTILITY SCRIPTS**

#### `gravity_forms_detector.py`
**Purpose**: Test specific Gravity Forms sites
**Use Case**: Debugging Gravity Forms detection
**Success Rate**: 100% for known Gravity Forms sites

#### `debug_direct_contact_test.py`
**Purpose**: Quick validation of individual contact pages
**Use Case**: Testing specific dealership contact forms

---

## 🐍 Python Dependencies

### Required Python Packages
```txt
playwright>=1.40.0
pandas>=2.0.0
asyncio (built-in)
os (built-in)
datetime (built-in)
random (built-in)
```

### Installation Commands
```bash
# Install Playwright
pip install playwright
playwright install chromium

# Install pandas
pip install pandas

# Verify installation
python -c "import playwright; import pandas; print('Dependencies OK')"
```

---

## 📊 Data File Requirements

### Input Data: `Dealerships - Jeep.csv`

#### Minimum Required Fields
```csv
dealer_name,website
```

#### Recommended Fields (for full functionality)
```csv
dealer_name,website,city,state,phone,latitude,longitude,email
```

#### Data Quality Requirements
- **website**: Must start with `http://` or `https://`
- **dealer_name**: Non-empty string for identification
- **No duplicates**: Unique website URLs
- **Valid URLs**: Accessible website addresses

#### Sample Valid Record
```csv
Thomas Garage Inc,https://www.thomasautocenters.com,Thomas,WV,304-463-4193,37.9542,-81.2209,info@thomasautocenters.com
```

### Output Data Structure

#### Test Results CSV Format
```csv
dealer_name,website,status,contact_score,form_type,total_inputs,email_fields,name_fields,message_fields,screenshot_path
```

#### Screenshot Directory Structure
```
tests/[test_name]_[timestamp]/
├── screenshots/
│   ├── [dealer_name]_success.png
│   ├── [dealer_name]_failed.png
│   └── [dealer_name]_error.png
└── [test_name]_results.csv
```

---

## 🔄 File Dependencies Map

### Core Dependency Chain
```
final_retest_with_contact_urls.py
    ↓ imports
enhanced_stealth_browser_config.py
    ↓ requires
playwright (external package)
    ↓ reads
Dealerships - Jeep.csv
    ↓ outputs
tests/final_retest_contact_urls_[timestamp]/
    ├── final_retest_results.csv
    └── screenshots/*.png
```

### Import Dependencies
```python
# All production scripts require these imports
import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
```

---

## 🚀 Quick Setup Guide

### Minimal Setup (To run immediately)
1. **Ensure these files exist:**
   ```
   ✅ Dealerships - Jeep.csv
   ✅ enhanced_stealth_browser_config.py
   ✅ final_retest_with_contact_urls.py
   ```

2. **Install dependencies:**
   ```bash
   pip install playwright pandas
   playwright install chromium
   ```

3. **Run:**
   ```bash
   python final_retest_with_contact_urls.py
   ```

### Full Setup (All capabilities)
1. **Copy all files from current directory**
2. **Maintain directory structure**
3. **Install all Python dependencies**
4. **Verify data file format**

---

## 📁 Critical File Locations

### Must Be in Same Directory
- `enhanced_stealth_browser_config.py`
- `Dealerships - Jeep.csv`
- Production scripts (`.py` files)

### Auto-Created Directories
- `tests/` - Created automatically for results
- `tests/[test_name]_[timestamp]/` - Created per test run
- `tests/[test_name]_[timestamp]/screenshots/` - Created for images

---

## 🔒 File Security & Backup

### Critical Files to Backup
1. **`Dealerships - Jeep.csv`** - Primary data source
2. **`enhanced_stealth_browser_config.py`** - Core functionality
3. **`final_retest_with_contact_urls.py`** - Best production script
4. **`DEALERSHIP_CONTACT_AUTOMATION_DOCUMENTATION.md`** - Complete knowledge

### Files Safe to Delete
- `tests/` directory contents (can be regenerated)
- Experimental scripts (keep for reference but not critical)
- Screenshots (can be regenerated)

---

## 🔧 Environment Setup

### Directory Permissions
```bash
# Ensure write permissions for test output
chmod 755 .
chmod 644 *.py
chmod 644 *.csv
chmod 755 tests/  # If exists
```

### Python Environment
```bash
# Check Python version (3.7+ required)
python --version

# Check working directory
pwd
# Should be: .../Auto Contacting

# Verify file presence
ls -la enhanced_stealth_browser_config.py
ls -la "Dealerships - Jeep.csv"
ls -la final_retest_with_contact_urls.py
```

---

## 🎯 File Usage Priority

### Primary Production Files (Use These)
1. **`final_retest_with_contact_urls.py`** - Best performance
2. **`contact_page_detector.py`** - Fallback option
3. **`enhanced_stealth_browser_config.py`** - Required support
4. **`Dealerships - Jeep.csv`** - Required data

### Debug/Analysis Files (When Needed)
1. **`gravity_forms_detector.py`** - Gravity Forms testing
2. **`debug_direct_contact_test.py`** - Individual site testing
3. **`universal_form_analyzer.py`** - Advanced analysis

### Reference Files (Keep but don't run)
1. **`complete_50_test.py`** - Historical success reference
2. **`retest_failed_dealerships.py`** - Example of what not to do
3. **Documentation files** - Reference and continuation

---

## 📋 Pre-Run Checklist

### Before Running Any Script
- [ ] `enhanced_stetml_browser_config.py` exists
- [ ] `Dealerships - Jeep.csv` exists and has valid data
- [ ] Python dependencies installed (`playwright`, `pandas`)
- [ ] Chromium browser installed (`playwright install chromium`)
- [ ] Working directory is correct (`Auto Contacting/`)
- [ ] Write permissions for `tests/` directory

### Troubleshooting File Issues
```bash
# Check if core files exist
ls -la enhanced_stealth_browser_config.py
ls -la "Dealerships - Jeep.csv"

# Check CSV format
head -n 3 "Dealerships - Jeep.csv"

# Test Python imports
python -c "from enhanced_stealth_browser_config import EnhancedStealthBrowserManager; print('Import OK')"
```

---

**Last Updated**: September 21, 2024
**Purpose**: Complete file system reference for project continuation
**Critical**: This documentation ensures no files are missing when resuming work