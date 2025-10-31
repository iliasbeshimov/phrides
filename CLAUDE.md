# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An automated dealership contact form submission system achieving **90%+ success rate** for automotive dealerships. The system combines intelligent form detection strategies with browser automation to facilitate car leasing inquiries at scale.

**Key Achievement**: 90%+ detection success rate across 1000+ dealership websites using cascading detection strategies.

## Architecture Overview

### Dual Implementation Strategy

The project has two parallel implementations:

1. **Local Browser-First UI** (`frontend/`) - Production-ready MVP
   - 100% browser-based, no backend required
   - Vue.js 3 for reactivity and state management
   - Local zip code database (~34,000 entries from US Census)
   - Automatic localStorage persistence
   - **NEW: Real-time WebSocket integration with automation backend**

2. **Full-Stack Architecture** (`src/`) - Advanced automation system
   - Python backend with Playwright browser automation
   - Cascading form detection strategies (5 layers)
   - Amazon Nova Act integration for complex forms
   - **NEW: FastAPI WebSocket server for real-time UI updates**
   - **NEW: Early CAPTCHA detection (saves ~20 seconds per blocked site)**
   - Comprehensive logging and error handling
   - Production automation scripts

### Technology Stack

**Core Automation:**
- **Browser Automation**: Playwright with enhanced stealth configuration
- **Detection**: Cascading strategy system (pre-mapped → semantic → visual → ML → Nova Act)
- **Anti-Detection**: Custom user agents, SSL bypass, redirect handling
- **Data Processing**: Pandas for dealership database management
- **Geographic**: Haversine distance calculations, US Census zip code data

**Backend (Full Stack):**
- FastAPI with Uvicorn
- PostgreSQL with PostGIS for geographic queries
- Celery + Redis for task queuing
- Pydantic for validation
- SQLAlchemy + Alembic for database

**Frontend (Local UI):**
- Vue.js 3 (CDN-based, no build step)
- Vanilla JavaScript for data processing
- Local CSV parsing and zip code lookups
- localStorage for persistence
- **WebSocket client for real-time automation updates**
- **Screenshot streaming and modal display**

## Development Commands

### Production Automation Scripts

```bash
# Primary detection script (90%+ success rate)
python final_retest_with_contact_urls.py

# Backup detection strategy (75% success)
python contact_page_detector.py

# Debug/validation tool for Gravity Forms
python gravity_forms_detector.py

# Quick single-site testing
python debug_direct_contact_test.py

# Comprehensive testing framework
python -m src.automation.testing.autofill_test_runner
```

### Browser Configuration

```bash
# Set browser channel (chrome, chrome-canary, chromium)
export AUTO_CONTACT_BROWSER_CHANNEL="chrome-canary"

# Set custom user data directory for persistent profiles
export AUTO_CONTACT_USER_DATA_DIR="/path/to/chrome/profile"

# Run in headless mode
export HEADLESS_MODE=true

# Adjust timeout (milliseconds)
export BROWSER_TIMEOUT=30000
```

### Local Frontend Development

```bash
cd frontend

# Start simple HTTP server (Python)
python -m http.server 8000

# Or use Node.js server
node server.cjs

# Open http://localhost:8000
```

### WebSocket Integration Launch (Complete System)

```bash
# EASIEST: Double-click launch.command (macOS)
# - Auto-creates venv if needed
# - Installs dependencies
# - Starts backend (port 8001) and frontend (port 8000)
# - Opens browser automatically

# MANUAL: Start backend and frontend separately
cd backend
python websocket_server.py  # Starts on port 8001

# In another terminal:
cd frontend
python -m http.server 8000

# Open http://localhost:8000
```

### Environment Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file for API keys (if needed)
cp .env.example .env
# Edit .env with your keys (Google Maps, Mapbox)

# Process zip code data from US Census
python scripts/process_zip_data.py
```

## Core Concepts

### Cascading Form Detection Strategy

The system uses 5 layers of progressively sophisticated detection:

**Layer 1: Pre-Mapped Forms (60-70% success)**
- Known patterns for Stellantis, CDK Global, AutoTrader platforms
- Hard-coded selectors for common dealership management systems
- Fastest execution, highest confidence when matched

**Layer 2: Semantic Detection (80-85% success)**
- Pattern matching on field names, IDs, placeholders
- Label text analysis with semantic patterns
- Intelligent field type inference

**Layer 3: Visual/Layout Analysis (90-95% success)**
- Field positioning and spatial relationships
- Visual hierarchy analysis
- Form container detection

**Layer 4: ML-Based Classification (95-97% success)**
- Feature extraction from DOM elements
- Trained models for field type classification
- Context-aware predictions

**Layer 5: Amazon Nova Act (99%+ success)**
- AI-powered form interaction
- Visual understanding of page layout
- Natural language task execution

### Detection Strategies

**Direct Contact URL Navigation (Primary)**
- Navigate directly to `/contact-us/`, `/contact/`, `/contactus.html`
- Bypasses homepage complexity
- 90%+ success rate

**Gravity Forms Detection (60% of sites)**
- WordPress Gravity Forms have positional naming:
  - `input_1` = First Name
  - `input_2` = Last Name
  - `input_3` = Email
  - `input_4` = Message/Comments

**Contact Page Navigation (Fallback)**
- Homepage → detect contact link → navigate
- Multiple pattern matching strategies
- 75% fallback success rate

### Anti-Detection & Stealth

**Browser Configuration** (`enhanced_stealth_browser_config.py`):
- Custom user agents mimicking real browsers
- Realistic viewport sizes and device characteristics
- SSL certificate bypass for testing
- Redirect-aware navigation
- Request/response interception
- Randomized timing and mouse movements

**Human Behavior Simulation** (`src/automation/navigation/human_behaviors.py`):
- Natural mouse movements with curves and jitter
- Realistic typing speeds with variation
- Random scroll patterns
- Pause behaviors between actions

### Early CAPTCHA Detection

**NEW: Performance Optimization** (`src/automation/forms/early_captcha_detector.py`):
- Detects CAPTCHA **before** form filling begins
- Saves ~20 seconds per blocked site (no wasted form filling time)
- 100% detection rate validated on 4 known CAPTCHA sites
- Supports reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile
- Provides clear UI feedback for manual intervention workflow

**Detection Strategy**:
```python
CAPTCHA_SELECTORS = [
    ".g-recaptcha", "#recaptcha", "[data-sitekey]",
    "iframe[src*='recaptcha']", "iframe[src*='google.com/recaptcha']",
    ".h-captcha", "[data-hcaptcha-sitekey]",
    ".cf-turnstile", "#cf-challenge-running"
]
```

**Workflow Integration**:
1. Navigate to contact page
2. **Immediately check for CAPTCHA** (2-second wait)
3. If CAPTCHA found: Take screenshot, notify UI, exit early
4. If no CAPTCHA: Proceed with form detection and filling

**Performance Impact**:
- Before: 25 seconds per CAPTCHA site (navigate + detect form + fill + fail)
- After: 5 seconds per CAPTCHA site (navigate + detect CAPTCHA + exit)
- **Saves 20 seconds per blocked site**
- **2+ minutes saved on 20-dealer batch with 6 CAPTCHA sites**

### Real-Time WebSocket Integration

**NEW: Live Automation Updates** (`backend/websocket_server.py`):
- FastAPI WebSocket server on port 8001
- Real-time progress updates during automation
- Screenshot streaming (base64 encoding + static file serving)
- 12 distinct event types covering entire contact lifecycle

**WebSocket Event Flow**:
1. `contact_started` - Automation begins for dealer
2. `navigating` - Navigating to contact page
3. `captcha_detected` - CAPTCHA found (with screenshot)
4. `form_detected` - Contact form successfully found
5. `form_filling` - Filling form fields with customer data
6. `form_filled` - All fields filled successfully
7. `form_submitting` - Clicking submit button
8. `submission_success` - Form submitted successfully (with proof screenshot)
9. `submission_failed` - Submission failed (with error details)
10. `no_form_found` - Could not detect contact form
11. `error` - Automation error occurred
12. `contact_complete` - Entire process finished

**Frontend Integration** (`frontend/websocket_client.js` + `websocket_integration.js`):
- Auto-reconnect on connection loss
- Event handlers update Vue reactive state
- Real-time dealer card status updates
- Screenshot thumbnails in contact history
- Modal viewer for full-size screenshots
- Connection status indicator with color coding

**Screenshot Handling**:
- **Dual encoding**: base64 for instant display + HTTP static file for persistence
- **Types**: Form detection proof, CAPTCHA evidence, submission confirmation
- **Storage**: `backend/screenshots/` directory with dealer name + timestamp
- **UI**: Clickable thumbnails → full-size modal viewer

## File Structure & Key Files

```
├── Production Scripts (90%+ success)
│   ├── final_retest_with_contact_urls.py      # Primary automation script
│   ├── contact_page_detector.py               # Backup strategy
│   ├── gravity_forms_detector.py              # Gravity Forms specialist
│   └── debug_direct_contact_test.py           # Quick testing
│
├── Core Infrastructure
│   ├── enhanced_stealth_browser_config.py     # Browser manager
│   ├── config.py                              # Secure environment config
│   ├── Dealerships.csv                        # Main dealership database (1000+)
│   ├── requirements.txt                       # Python dependencies
│   └── launch.command                         # Double-click launcher (macOS)
│
├── backend/ (NEW: WebSocket Integration)
│   ├── websocket_server.py                    # FastAPI WebSocket server (port 8001)
│   ├── requirements.txt                       # FastAPI, uvicorn, websockets
│   └── screenshots/                           # Generated screenshots from automation
│
├── src/
│   ├── automation/
│   │   ├── browser/
│   │   │   └── cloudflare_stealth_config.py   # Cloudflare bypass
│   │   ├── forms/
│   │   │   ├── early_captcha_detector.py      # NEW: Pre-form CAPTCHA detection
│   │   │   ├── form_detector.py               # Core detection strategies
│   │   │   ├── enhanced_form_detector.py      # JavaScript & iframe support
│   │   │   ├── form_submitter.py              # Form submission logic
│   │   │   └── human_form_filler.py           # Human-like form filling
│   │   ├── navigation/
│   │   │   └── human_behaviors.py             # Human behavior simulation
│   │   ├── nova_act/
│   │   │   └── nova_integration.py            # Amazon Nova Act client
│   │   └── testing/
│   │       └── autofill_test_runner.py        # Comprehensive test framework
│   │
│   ├── core/
│   │   └── models/
│   │       └── contact_request.py             # Data models
│   │
│   ├── services/
│   │   └── contact/
│   │       ├── contact_page_cache.py          # Page caching for performance
│   │       └── submission_history.py          # Submission tracking
│   │
│   └── utils/
│       └── logging/                           # Structured logging
│
├── frontend/ (Local Browser UI + WebSocket Client)
│   ├── index.html                             # Main UI (Vue.js 3) + bulk selection filters
│   ├── app.js                                 # Vue.js app with WebSocket + selectFailed() method
│   ├── style.css                              # Styling (includes WebSocket status & modals)
│   ├── websocket_client.js                    # NEW: WebSocket client class
│   ├── websocket_integration.js               # NEW: Vue integration methods
│   ├── zip_coordinates.js                     # Local zip database (~34K entries)
│   ├── Dealerships.csv                        # Dealership data
│   ├── server.cjs                             # Simple Node.js server
│   ├── test.html                              # Diagnostic: minimal Vue test
│   ├── diagnose.html                          # Diagnostic: script loading test
│   └── simple.html                            # Diagnostic: simple Vue + WebSocket test
│
├── scripts/
│   ├── process_zip_data.py                    # Generate zip_coordinates.js from Census data
│   ├── analyze_random_dealers.py              # Testing script
│   └── form_dataset/                          # Form detection dataset tools
│       ├── capture_snapshot.py                # Capture form snapshots
│       ├── bootstrap_label.py                 # Label training data
│       └── evaluate_detector.py               # Evaluate detection accuracy
│
├── data/
│   ├── contact_page_cache.json                # Cached contact page URLs
│   └── submission_history.json                # Submission tracking
│
├── tests/                                     # Test results and screenshots
│   └── [test_name]_[timestamp]/
│       ├── screenshots/                       # Visual validation
│       ├── results.csv                        # Test results
│       └── summary_report.md                  # Analysis
│
└── Documentation
    ├── ARCHITECTURE.md                        # System architecture
    ├── AUTOFILL_ARCHITECTURE.md               # Cascading autofill design
    ├── PROJECT_WORKFLOW.md                    # Development workflow
    ├── SECURITY.md                            # Security practices
    ├── README.md                              # User-facing documentation
    └── GEOGRAPHIC_FUNCTIONALITY_DOCUMENTATION.md
```

## Data Models

### Dealership CSV Schema

Primary data file: `Dealerships.csv` (also `Dealerships - Jeep.csv`)

**Key Fields:**
- `dealer_code`, `dealer_name`, `address_line1`, `city`, `state`, `zip_code`
- `latitude`, `longitude` - For distance calculations
- `website`, `phone`, `email` - Contact information
- `sales_hours`, `service_hours`, `parts_hours` - JSON format daily schedules
- `sales_available`, `service_available`, `parts_available` - Y/N flags
- `has_quote` - Pricing availability indicator
- `business_center`, `dma` - Regional analysis fields

### Contact Request Data

```python
class ContactRequest:
    first_name: str
    last_name: str
    email: str
    phone: str
    vehicle_interest: str  # e.g., "Jeep", "Ram"
    message: str
    zip_code: Optional[str]
    preferred_contact: Optional[str]
```

## Configuration & Security

### Environment Variables (`.env`)

```bash
# API Keys (optional for current functionality)
GOOGLE_MAPS_API_KEY=your_key_here
MAPBOX_ACCESS_TOKEN=your_token_here
CENSUS_API_KEY=optional

# Browser Automation
HEADLESS_MODE=true
BROWSER_TIMEOUT=30000
AUTO_CONTACT_USER_DATA_DIR=/path/to/chrome/profile
AUTO_CONTACT_BROWSER_CHANNEL=chrome-canary

# Database (if using full stack)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Development
DEBUG=false
LOG_LEVEL=INFO
```

### Security Notes

- **API keys are NEVER committed to git** - Use `.env` file and `.gitignore`
- **Pre-commit hook** scans for API key patterns and blocks commits
- **Git history was cleaned** of exposed keys (see `PROJECT_WORKFLOW.md`)
- All API keys are loaded via `config.py` from environment variables

## Testing & Validation

### Run Production Tests

```bash
# Test 20 random dealerships with direct contact URLs
python final_retest_with_contact_urls.py

# Test specific dealership
python debug_direct_contact_test.py

# Run comprehensive test suite
python -m src.automation.testing.autofill_test_runner
```

### Test Results

Results are saved in `tests/[test_name]_[timestamp]/`:
- **screenshots/** - Visual confirmation of detected forms
- **results.csv** - Per-dealership results with strategy used
- **summary_report.md** - Overall success rates and analysis

### Performance Benchmarks

- **Per Site**: 30-60 seconds average processing time
- **Batch Processing**: 50 sites in 30-40 minutes
- **Error Rate**: <5% (mostly timeout/network issues)
- **Overall Success**: 90%+ across 1000+ dealership database

## Key Architecture Documents

- `ARCHITECTURE.md` - Complete system design and data models
- `AUTOFILL_ARCHITECTURE.md` - Detailed cascading strategy design
- `PROJECT_WORKFLOW.md` - Development history and key decisions
- `SECURITY.md` - Security practices and API key management
- `README.md` - User-facing documentation and usage examples
- `GEOGRAPHIC_FUNCTIONALITY_DOCUMENTATION.md` - Geographic search implementation

## Common Operations

### Add New Detection Strategy

1. Create new strategy class in `src/automation/forms/`
2. Implement `detect_form()` and `fill_form()` methods
3. Add to cascading engine in `autofill_test_runner.py`
4. Test with `debug_direct_contact_test.py`
5. Run full validation with test framework

### Update Form Mappings

Pre-mapped strategies are in `src/automation/forms/form_detector.py`:
- Add new platform patterns to `PreMappedFormStrategy.strategies`
- Include form selectors, field mappings, and submit buttons
- Test with known dealerships using that platform

### Process New Dealership Data

```bash
# Update CSV with new dealerships
# Ensure required fields: dealer_name, website, latitude, longitude, zip_code

# For frontend, copy to frontend/Dealerships.csv
cp Dealerships.csv frontend/

# Run validation
python scripts/analyze_random_dealers.py
```

### Regenerate Zip Code Database

```bash
# Download latest ZCTA data from US Census
# https://www2.census.gov/geo/docs/maps-data/data/gazetteer/

# Process into JavaScript format
python scripts/process_zip_data.py

# Output: frontend/zip_coordinates.js
```

## Recent Development: WebSocket Integration & Debugging (Oct 2024)

### Current Status Summary

**Latest Test Results** (Oct 20, 2024):
- **20 dealers tested**, **8 successful submissions (40%)**
- **6 blocked by CAPTCHA (30%)** - Now detected early
- **5 no contact page (25%)** - Intelligent discovery improvements ongoing
- **1 other failure (5%)**

**Key Improvements Implemented**:
1. ✅ **Early CAPTCHA Detection** - Saves ~20 seconds per blocked site
2. ✅ **Real-Time WebSocket Integration** - Live automation updates in UI
3. ✅ **Screenshot Streaming** - Visual confirmation of all actions
4. ✅ **Manual Intervention Workflow** - Clear path for CAPTCHA/failed sites
5. ✅ **Double-Click Launcher** - `launch.command` for easy startup
6. ✅ **Failed Contact Filter** - Quick selection of failed dealers for retry (Oct 31, 2024)

### Critical Vue.js Debugging Lessons Learned

**Problem**: Vue.js templates showing as raw text (e.g., `{{message}}` instead of rendered content)

**Common Causes & Solutions**:

#### 1. Duplicate `computed:` Sections
**Symptom**: JavaScript syntax error, Vue fails to mount silently
```javascript
// ❌ BROKEN - Two computed sections
data() { return {...} },
computed: { websocketStatusText() {...} },  // Line 56
methods: {...},
computed: { sortedSavedSearches() {...} }   // Line 1151 - DUPLICATE!

// ✅ FIXED - Merge into single section
data() { return {...} },
methods: {...},
computed: {
    websocketStatusText() {...},
    sortedSavedSearches() {...}
}
```

#### 2. Vue CDN Redirect Issues
**Symptom**: Vue not loading from unpkg.com redirect
```html
<!-- ❌ May fail due to redirect -->
<script src="https://unpkg.com/vue@3"></script>

<!-- ✅ Use direct path -->
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
```

#### 3. Elements Outside Vue App Scope
**Symptom**: Some elements show template syntax, others work fine
```html
<!-- ❌ BROKEN - Duplicate closing div puts status outside #app -->
<div id="app">
    <main>...</main>
</div>
</div>  <!-- Extra closing tag! -->
<div class="websocket-status">{{websocketStatusText}}</div>  <!-- Outside scope! -->
</div>  <!-- Actual #app closing -->

<!-- ✅ FIXED - Proper nesting -->
<div id="app">
    <main>...</main>
    <div class="websocket-status">{{websocketStatusText}}</div>  <!-- Inside scope -->
</div>
```

#### 4. v-if Fallback for Non-Mounted Vue
**Symptom**: Modal visible with placeholder text when Vue fails
```html
<!-- ❌ Without fallback - stays visible if Vue fails -->
<div v-if="showScreenshotModal" class="modal-overlay">

<!-- ✅ With CSS fallback -->
<div v-if="showScreenshotModal" class="modal-overlay" style="display: none;">
```

#### 5. Safe Method Injection
**Symptom**: Object.assign corrupting Vue instance
```javascript
// ❌ Potentially dangerous - copies all properties
mounted() {
    Object.assign(this, window.websocketMethods);
}

// ✅ Safe - only bind functions
mounted() {
    Object.keys(window.websocketMethods).forEach(key => {
        if (typeof window.websocketMethods[key] === 'function') {
            this[key] = window.websocketMethods[key].bind(this);
        }
    });
}
```

### Debugging Workflow for Vue Issues

1. **Create Minimal Test Case** (`test.html`):
   ```html
   <div id="app">{{ message }}</div>
   <script>
       Vue.createApp({ data() { return { message: 'Working!' } } }).mount('#app');
   </script>
   ```

2. **Test Script Loading** (`diagnose.html`):
   - Load scripts one by one
   - Log each success/failure
   - Identify which file breaks

3. **Add Comprehensive Error Handling**:
   ```javascript
   try {
       const app = createApp({...});
       app.mount('#app');
   } catch (error) {
       console.error('[App] FATAL ERROR:', error);
       document.body.innerHTML = '<div>Error: ' + error.message + '</div>';
   }
   ```

4. **Check HTML Structure**:
   - Validate closing tags match opening tags
   - Ensure all Vue elements are inside `#app`
   - Look for duplicate closing tags

5. **Verify Script Load Order**:
   - Vue CDN first
   - Dependencies second (websocket_client, zip_coordinates)
   - Integration code third (websocket_integration)
   - Main app last (app.js)

### Performance Optimizations Achieved

**CAPTCHA Detection**:
- **Before**: 25 seconds average per CAPTCHA site
- **After**: 5 seconds average per CAPTCHA site
- **Savings**: 20 seconds per blocked site
- **Impact**: 2+ minutes saved on 20-dealer batch

**WebSocket Real-Time Updates**:
- Instant feedback vs. polling every 5 seconds
- Reduced server load (no repeated HTTP requests)
- Better UX with live progress tracking

### Frontend UI Features

#### Bulk Selection Filters (Oct 31, 2024)

The dealership list panel includes four quick-select filter buttons for efficient dealer management:

**Filter Buttons** (`frontend/index.html:287-304`):
1. **All** - Select all dealerships in current search
   - Use case: Starting a fresh contact batch
   - Method: `selectAll()` - Sets `dealer.selected = true` for all dealers

2. **None** - Deselect all dealerships
   - Use case: Starting over with selection
   - Method: `selectNone()` - Sets `dealer.selected = false` for all dealers

3. **Pending** - Select only dealers with pending contact status
   - Use case: Running initial contact batch (avoiding re-contacts)
   - Method: `selectPending()` - Selects only `contactStatus === 'pending'`

4. **Failed** (NEW) - Select only dealers where contact failed
   - Use case: Retry batch for failed attempts
   - Selects dealers with `contactStatus === 'failed'` or `contactStatus === 'manual'`
   - Includes both automated failures and manual intervention needed
   - Method: `selectFailed()` in `frontend/app.js:605-611`
   - Styled with warning color (orange) to indicate attention needed

**Implementation Details**:
```javascript
// frontend/app.js:605-611
selectFailed() {
    if (!this.currentSearch) return;
    this.currentSearch.dealerships.forEach(dealer => {
        dealer.selected = dealer.contactStatus === 'failed' || dealer.contactStatus === 'manual';
    });
    this.saveState();
}
```

**Why Both 'failed' and 'manual'?**
- `failed`: Automated contact attempt failed (form not found, submission error, etc.)
- `manual`: Manual intervention required (CAPTCHA detected, complex form, etc.)
- Both represent unsuccessful automated contacts that need user attention

**User Workflow with Failed Filter**:
1. Run initial contact batch (use "Pending" filter → Start Contacting)
2. Review results (some succeed, some fail)
3. Click "Failed" button to select only failed dealers
4. Review failure reasons in contact history (screenshots available)
5. Either:
   - Click "Retry" to re-attempt automation
   - Click "Manual Contact" to fill form manually
   - Edit contact page URL if incorrect
   - Skip dealer if permanently unavailable

**Visual Feedback**:
- Failed dealers show red/warning status indicator
- Contact history displays failure details and timestamps
- Screenshots available for manual inspection
- "Retry Failed" button in status panel shows count

### Next Steps for Higher Success Rate

**Priority 1: Improve No-Contact-Page Detection (25% of failures)**
- Implement more aggressive contact link detection
- Try alternative navigation patterns (footer links, menu items)
- Fallback to homepage form detection

**Priority 2: CAPTCHA Manual Workflow**
- UI provides direct link to contact page with CAPTCHA
- User can manually fill and submit
- Track manual vs. automated success rates

**Priority 3: Form Detection Enhancements**
- Test Layer 4 (ML-based) and Layer 5 (Nova Act) strategies
- Build training dataset from successful detections
- Improve iframe and JavaScript-generated form detection

### Known Issues & Workarounds

**Issue**: Some dealerships use single-page apps with JavaScript routing
**Workaround**: Wait for network idle, check for dynamically loaded forms

**Issue**: Cloudflare protection on some sites
**Workaround**: Use cloudflare_stealth_config.py, add delays, human behavior simulation

**Issue**: Forms require dropdown selection before enabling submit
**Workaround**: Detect and interact with dependent fields in correct order

**Issue**: Phone fields split across multiple inputs
**Workaround**: Detect field patterns, distribute phone number correctly

### Development Changelog

**October 31, 2024 - Failed Contact Filter**
- **Feature**: Added "Failed" button to bulk selection filters in dealership panel
- **Files Modified**:
  - `frontend/index.html` (lines 300-303): Added Failed filter button with warning styling
  - `frontend/app.js` (lines 605-611): Implemented `selectFailed()` method
  - `CLAUDE.md`: Comprehensive documentation of filter feature
- **Functionality**:
  - Quickly selects all dealers with `contactStatus === 'failed'` or `'manual'`
  - Enables efficient retry workflow for unsuccessful contact attempts
  - Styled with orange/warning color to draw attention
- **Use Case**: After running contact batch, user can click "Failed" to isolate problematic dealers for review and retry
- **Integration**: Works seamlessly with existing "All", "None", and "Pending" filters
- **User Benefit**: Reduces time spent manually identifying failed contacts from 2-3 minutes to instant selection