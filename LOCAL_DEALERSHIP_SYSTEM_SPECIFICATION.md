# Local Dealership Contact Management System
## Comprehensive Technical Specification

**Version**: 1.0
**Date**: September 2024
**Type**: Browser-based Single Page Application

---

## 🎯 **System Overview**

### **Objective**
Create a comprehensive browser-based dealership contact management system with robust local search capabilities, intelligent contact tracking, and persistent local storage - requiring no server infrastructure.

### **Core Philosophy**
- **Fully Client-Side**: No backend dependencies, runs entirely in browser
- **Local-First**: Data persists locally with optional cloud sync via Google Sheets
- **Contact-Optimized**: Designed specifically for automotive dealership lead generation
- **Intelligence-Driven**: Smart restart logic and contact state management

---

## 🏗️ **System Architecture**

### **Application Type**
**Single Page Application (SPA)** with integrated components:
```
┌─────────────────────────────────────────────────────────────┐
│  Local Dealership Contact Management System                 │
├─────────────────────────────────────────────────────────────┤
│  Search Parameters    │  Dealership List   │  Contact Status │
│  ┌─────────────────┐  │  ┌──────────────┐  │  ┌─────────────┐ │
│  │ Make: [Jeep  ▼] │  │  │ █ Dealer 1   │  │  │ ⚫ Active    │ │
│  │ Zip:  [90210  ] │  │  │ █ Dealer 2   │  │  │ ⏸️ Paused    │ │
│  │ Mile: [25    ▼] │  │  │ □ Dealer 3   │  │  │ ✅ Complete  │ │
│  │ [Expand Search] │  │  │ □ Dealer 4   │  │  │             │ │
│  └─────────────────┘  │  └──────────────┘  │  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Auto-Contact Controls                                       │
│  [▶️ Start from Furthest] [⏸️ Pause] [🔄 Smart Restart]       │
└─────────────────────────────────────────────────────────────┘
```

### **Technical Stack**
```javascript
// Core Technologies
Frontend: Vanilla JavaScript / React (lightweight)
Styling: TailwindCSS (minimal footprint)
Storage: IndexedDB (primary) + LocalStorage (fallback)
Data Source: Google Sheets API (public spreadsheet)
Maps: Google Maps API (distance calculation)
Automation: Browser Extension / WebDriver integration
```

---

## 🔍 **Search and Dealership Management**

### **Dynamic Search Capabilities**

#### **Search Parameters**
```typescript
interface SearchParameters {
  make: 'Jeep' | 'Ram' | 'Chrysler' | 'Dodge' | 'All'
  zipcode: string          // 5-digit US zipcode
  radiusMiles: number      // 5, 10, 25, 50, 100, 200
  customerInfo: {
    firstName: string
    lastName: string
    email: string
    phone: string
    zipcode: string
    message: string
  }
}
```

#### **Geographical Expansion**
```javascript
// Search expansion without data loss
function expandSearch(currentParams, newRadius) {
  const existingDealerships = getStoredDealerships(currentParams)
  const expandedResults = findDealerships({
    ...currentParams,
    radiusMiles: newRadius
  })

  // Merge with existing data, preserve contact status
  return mergeDealershipData(existingDealerships, expandedResults)
}
```

#### **Search Modification Rules**
- **Adding radius**: Preserves existing dealerships, adds new ones
- **Changing make**: Creates new search context but saves previous
- **Location change**: Creates entirely new search
- **Customer info update**: Updates all searches globally

### **Dealership Data Management**

#### **Google Spreadsheet Integration**
```javascript
// Data source configuration
const SPREADSHEET_CONFIG = {
  spreadsheetId: 'your_public_google_sheet_id',
  range: 'Dealerships!A:Z',
  apiKey: 'your_google_sheets_api_key',
  refreshInterval: 3600000 // 1 hour cache
}

// Fetch dealership data
async function fetchDealershipData() {
  const response = await fetch(
    `https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_CONFIG.spreadsheetId}/values/${SPREADSHEET_CONFIG.range}?key=${SPREADSHEET_CONFIG.apiKey}`
  )
  return response.json()
}
```

#### **Dealership Data Structure**
```typescript
interface Dealership {
  id: string
  dealerName: string
  address: string
  city: string
  state: string
  zipcode: string
  phone: string
  website: string
  latitude: number
  longitude: number
  make: string[]

  // Calculated fields
  distanceMiles: number
  contactStatus: ContactStatus
  lastContactedAt?: Date
  contactSuccess?: boolean
  contactNotes?: string
}

type ContactStatus = 'pending' | 'active' | 'paused' | 'completed' | 'failed' | 'skipped'
```

---

## 📱 **User Interface and Workflow**

### **Single-Page Layout**

#### **Three-Panel Design**
```html
<div class="dealership-management-system">
  <!-- Left Panel: Search Controls -->
  <div class="search-panel">
    <h2>Search Parameters</h2>
    <form class="search-form">
      <select name="make">Jeep, Ram, Chrysler, Dodge</select>
      <input name="zipcode" placeholder="90210" pattern="[0-9]{5}">
      <select name="radius">5, 10, 25, 50, 100, 200 miles</select>
      <button type="button" onclick="expandSearch()">Expand Search</button>
    </form>

    <h3>Customer Information</h3>
    <form class="customer-form">
      <input name="firstName" placeholder="John">
      <input name="lastName" placeholder="Smith">
      <input name="email" placeholder="john@email.com">
      <input name="phone" placeholder="(555) 123-4567">
      <textarea name="message">I'm interested in leasing...</textarea>
    </form>
  </div>

  <!-- Center Panel: Dealership List -->
  <div class="dealership-panel">
    <h2>Dealerships (sorted by distance - furthest first)</h2>
    <div class="dealership-filters">
      <label><input type="checkbox" checked> Show Pending</label>
      <label><input type="checkbox" checked> Show Completed</label>
      <label><input type="checkbox"> Show Failed</label>
    </div>

    <div class="dealership-list">
      <!-- Dynamic dealership cards -->
    </div>
  </div>

  <!-- Right Panel: Contact Status & Controls -->
  <div class="status-panel">
    <h2>Contact Status</h2>
    <div class="status-overview">
      <div class="status-card active">
        <span class="status-indicator">⚫</span>
        <span>Active: 1</span>
      </div>
      <div class="status-card paused">
        <span class="status-indicator">⏸️</span>
        <span>Paused: 0</span>
      </div>
      <div class="status-card completed">
        <span class="status-indicator">✅</span>
        <span>Completed: 12</span>
      </div>
    </div>

    <div class="contact-controls">
      <button class="btn-primary" onclick="startContacting()">
        ▶️ Start from Furthest
      </button>
      <button class="btn-secondary" onclick="pauseContacting()">
        ⏸️ Pause Current
      </button>
      <button class="btn-tertiary" onclick="smartRestart()">
        🔄 Smart Restart
      </button>
    </div>

    <div class="current-activity">
      <h3>Current Contact</h3>
      <div class="activity-display">
        <!-- Live status of current contact attempt -->
      </div>
    </div>
  </div>
</div>
```

### **Dealership Card Design**
```html
<div class="dealership-card" data-status="pending" data-distance="45.2">
  <div class="card-header">
    <div class="selection-control">
      <input type="checkbox" checked id="dealer-123">
      <label for="dealer-123"></label>
    </div>
    <div class="dealer-info">
      <h3>Santa Monica Chrysler Jeep</h3>
      <span class="distance-badge">45.2 miles</span>
    </div>
    <div class="status-indicator pending">⏳</div>
  </div>

  <div class="card-body">
    <p class="address">3219 Santa Monica Blvd, Santa Monica, CA 90404</p>
    <p class="contact">📞 (310) 829-3200 • 🌐 santamonicachrysler.com</p>
  </div>

  <div class="card-actions">
    <button class="btn-sm" onclick="contactNow('123')">Contact Now</button>
    <button class="btn-sm" onclick="skipDealer('123')">Skip</button>
    <button class="btn-sm" onclick="viewDetails('123')">Details</button>
  </div>

  <div class="contact-history" style="display: none;">
    <!-- Previous contact attempts -->
  </div>
</div>
```

---

## 🔄 **Contact Management States**

### **State Definitions**

#### **Contact States**
```typescript
enum ContactStatus {
  PENDING = 'pending',      // Not yet contacted
  ACTIVE = 'active',        // Currently being contacted
  PAUSED = 'paused',        // Contact paused mid-process
  COMPLETED = 'completed',  // Successfully contacted
  FAILED = 'failed',        // Contact attempt failed
  SKIPPED = 'skipped'       // Manually skipped by user
}
```

#### **State Transitions**
```javascript
const stateTransitions = {
  pending: ['active', 'skipped'],
  active: ['paused', 'completed', 'failed'],
  paused: ['active', 'skipped'],
  completed: ['active'], // Allow re-contact if needed
  failed: ['active', 'skipped'],
  skipped: ['active']
}
```

### **Visual State Indicators**

#### **Status Colors and Icons**
```css
.status-indicator.pending { color: #6B7280; } /* Gray */
.status-indicator.active { color: #3B82F6; }  /* Blue */
.status-indicator.paused { color: #F59E0B; }  /* Orange */
.status-indicator.completed { color: #10B981; } /* Green */
.status-indicator.failed { color: #EF4444; }  /* Red */
.status-indicator.skipped { color: #8B5CF6; } /* Purple */
```

#### **Progress Visualization**
```html
<div class="contact-progress">
  <div class="progress-bar">
    <div class="progress-segment completed" style="width: 40%"></div>
    <div class="progress-segment active" style="width: 5%"></div>
    <div class="progress-segment pending" style="width: 55%"></div>
  </div>
  <div class="progress-stats">
    <span>8/20 contacted</span>
    <span>Success rate: 87.5%</span>
  </div>
</div>
```

### **Granular Contact Controls**

#### **Individual Dealership Controls**
```javascript
class DealershipContactManager {
  // Start contacting specific dealership
  async contactDealer(dealerId) {
    this.updateStatus(dealerId, 'active')
    try {
      const result = await this.automateContact(dealerId)
      this.updateStatus(dealerId, result.success ? 'completed' : 'failed')
      return result
    } catch (error) {
      this.updateStatus(dealerId, 'failed')
      throw error
    }
  }

  // Pause current contact
  pauseContact(dealerId) {
    this.updateStatus(dealerId, 'paused')
    this.stopAutomation(dealerId)
  }

  // Resume paused contact
  resumeContact(dealerId) {
    this.updateStatus(dealerId, 'active')
    this.continueAutomation(dealerId)
  }

  // Skip dealership entirely
  skipDealer(dealerId) {
    this.updateStatus(dealerId, 'skipped')
    this.moveToNext()
  }
}
```

### **Intelligent Restart Mechanism**

#### **Smart Restart Logic**
```javascript
function smartRestart() {
  const uncontactedDealers = dealerships.filter(dealer =>
    ['pending', 'failed'].includes(dealer.contactStatus)
  )

  if (uncontactedDealers.length === 0) {
    showMessage("All dealerships have been contacted!")
    return
  }

  // Sort by distance (furthest first)
  const sortedDealers = uncontactedDealers.sort((a, b) =>
    b.distanceMiles - a.distanceMiles
  )

  startContactSequence(sortedDealers)
}
```

#### **Contact Sequence Management**
```javascript
class ContactSequenceManager {
  constructor() {
    this.currentIndex = 0
    this.isRunning = false
    this.isPaused = false
  }

  // Start from furthest dealership
  startFromFurthest() {
    const pendingDealers = this.getPendingDealerships()
    const sortedByDistance = pendingDealers.sort((a, b) =>
      b.distanceMiles - a.distanceMiles
    )

    this.contactQueue = sortedByDistance
    this.currentIndex = 0
    this.isRunning = true
    this.processNext()
  }

  // Process next dealership in queue
  async processNext() {
    if (!this.isRunning || this.isPaused) return
    if (this.currentIndex >= this.contactQueue.length) {
      this.complete()
      return
    }

    const currentDealer = this.contactQueue[this.currentIndex]
    await this.contactDealer(currentDealer.id)
    this.currentIndex++

    // Add delay between contacts
    setTimeout(() => this.processNext(), 2000)
  }
}
```

---

## 💾 **Local Data Persistence**

### **Storage Architecture**

#### **IndexedDB Structure** (Primary Storage)
```javascript
const dbSchema = {
  name: 'DealershipContactDB',
  version: 1,
  stores: {
    dealerships: {
      keyPath: 'id',
      indexes: {
        make: 'make',
        zipcode: 'zipcode',
        contactStatus: 'contactStatus',
        distanceMiles: 'distanceMiles'
      }
    },
    searchHistory: {
      keyPath: 'id',
      autoIncrement: true,
      indexes: {
        timestamp: 'createdAt',
        zipcode: 'parameters.zipcode'
      }
    },
    contactAttempts: {
      keyPath: 'id',
      autoIncrement: true,
      indexes: {
        dealershipId: 'dealershipId',
        timestamp: 'attemptedAt',
        success: 'success'
      }
    },
    customerProfiles: {
      keyPath: 'id',
      indexes: {
        email: 'email'
      }
    }
  }
}
```

#### **LocalStorage Fallback**
```javascript
class StorageManager {
  constructor() {
    this.preferredStorage = 'indexeddb'
    this.fallbackStorage = 'localstorage'
    this.init()
  }

  async init() {
    try {
      this.db = await this.openIndexedDB()
      this.storageType = 'indexeddb'
    } catch (error) {
      console.warn('IndexedDB not available, falling back to LocalStorage')
      this.storageType = 'localstorage'
    }
  }

  async save(store, data) {
    if (this.storageType === 'indexeddb') {
      return this.saveToIndexedDB(store, data)
    } else {
      return this.saveToLocalStorage(store, data)
    }
  }

  async load(store, query = {}) {
    if (this.storageType === 'indexeddb') {
      return this.loadFromIndexedDB(store, query)
    } else {
      return this.loadFromLocalStorage(store, query)
    }
  }
}
```

### **Data Synchronization**

#### **Google Sheets Integration**
```javascript
class DataSyncManager {
  constructor() {
    this.sheetsAPI = new GoogleSheetsAPI()
    this.localDB = new StorageManager()
    this.syncInterval = 3600000 // 1 hour
  }

  // Pull latest dealership data from Google Sheets
  async syncDealershipData() {
    try {
      const remoteData = await this.sheetsAPI.fetchDealerships()
      const localData = await this.localDB.load('dealerships')

      const mergedData = this.mergeDealershipData(localData, remoteData)
      await this.localDB.save('dealerships', mergedData)

      return { success: true, updated: mergedData.length }
    } catch (error) {
      console.error('Sync failed:', error)
      return { success: false, error: error.message }
    }
  }

  // Merge remote data with local contact status
  mergeDealershipData(localData, remoteData) {
    const localMap = new Map(localData.map(d => [d.id, d]))

    return remoteData.map(remoteDealership => {
      const localDealership = localMap.get(remoteDealership.id)

      return {
        ...remoteDealership,
        // Preserve local contact status and history
        contactStatus: localDealership?.contactStatus || 'pending',
        lastContactedAt: localDealership?.lastContactedAt,
        contactSuccess: localDealership?.contactSuccess,
        contactNotes: localDealership?.contactNotes
      }
    })
  }
}
```

### **Data Export and Backup**

#### **Export Capabilities**
```javascript
class DataExportManager {
  // Export search results to CSV
  exportToCSV(searchId) {
    const searchData = this.getSearchResults(searchId)
    const csvData = this.convertToCSV(searchData)
    this.downloadFile(`search-results-${searchId}.csv`, csvData)
  }

  // Export contact history
  exportContactHistory() {
    const contactHistory = this.getContactHistory()
    const jsonData = JSON.stringify(contactHistory, null, 2)
    this.downloadFile('contact-history.json', jsonData)
  }

  // Create backup of all data
  async createBackup() {
    const allData = {
      dealerships: await this.localDB.load('dealerships'),
      searchHistory: await this.localDB.load('searchHistory'),
      contactAttempts: await this.localDB.load('contactAttempts'),
      customerProfiles: await this.localDB.load('customerProfiles'),
      timestamp: new Date().toISOString(),
      version: '1.0'
    }

    const backupData = JSON.stringify(allData, null, 2)
    this.downloadFile(`dealership-backup-${Date.now()}.json`, backupData)
  }
}
```

---

## 🤖 **Contact Automation Integration**

### **Browser-Based Automation**

#### **Contact Automation Engine**
```javascript
class ContactAutomationEngine {
  constructor() {
    this.currentContact = null
    this.automationStatus = 'idle'
    this.retryAttempts = 3
    this.delayBetweenContacts = 30000 // 30 seconds
  }

  // Main contact method
  async contactDealer(dealership, customerInfo) {
    this.currentContact = dealership
    this.automationStatus = 'active'

    try {
      // Step 1: Open dealership website
      const success = await this.openDealershipWebsite(dealership.website)
      if (!success) throw new Error('Could not open website')

      // Step 2: Find contact form
      const contactForm = await this.findContactForm()
      if (!contactForm) throw new Error('Contact form not found')

      // Step 3: Fill contact form
      await this.fillContactForm(contactForm, customerInfo)

      // Step 4: Submit form
      const submitResult = await this.submitContactForm()

      // Step 5: Verify submission
      const confirmed = await this.verifySubmission()

      return {
        success: confirmed,
        method: 'automated_form',
        timestamp: new Date(),
        details: submitResult
      }

    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: new Date()
      }
    } finally {
      this.automationStatus = 'idle'
      this.currentContact = null
    }
  }

  // Integration with existing automation scripts
  async useExistingAutomation(dealership, customerInfo) {
    // Call existing Python automation scripts via bridge
    const automationResult = await this.callPythonAutomation({
      dealer_website: dealership.website,
      customer_info: customerInfo,
      script: 'final_retest_with_contact_urls.py'
    })

    return automationResult
  }
}
```

#### **Form Detection and Filling**
```javascript
class FormAutomationHandler {
  // Detect Gravity Forms (most common)
  detectGravityForms() {
    const gravityForms = document.querySelectorAll('form[id*="gform"]')
    return gravityForms.length > 0 ? gravityForms[0] : null
  }

  // Detect standard contact forms
  detectStandardForms() {
    const selectors = [
      'form[id*="contact"]',
      'form[class*="contact"]',
      'form[action*="contact"]',
      '.contact-form form',
      '#contact-form'
    ]

    for (const selector of selectors) {
      const form = document.querySelector(selector)
      if (form) return form
    }
    return null
  }

  // Fill form with customer data
  async fillContactForm(form, customerInfo) {
    const fieldMappings = {
      firstName: ['input_1', 'first_name', 'fname', 'first'],
      lastName: ['input_2', 'last_name', 'lname', 'last'],
      email: ['input_3', 'email', 'email_address'],
      phone: ['input_4', 'phone', 'telephone', 'mobile'],
      message: ['input_5', 'message', 'comments', 'inquiry']
    }

    for (const [dataField, selectors] of Object.entries(fieldMappings)) {
      const value = customerInfo[dataField]
      if (!value) continue

      for (const selector of selectors) {
        const field = form.querySelector(`[name="${selector}"], #${selector}`)
        if (field) {
          field.value = value
          field.dispatchEvent(new Event('input', { bubbles: true }))
          break
        }
      }
    }
  }
}
```

---

## 📊 **Contact Sequencing and Logic**

### **Contact Order: Furthest First**

#### **Distance-Based Sequencing**
```javascript
class ContactSequencer {
  // Sort dealerships by distance (furthest first)
  sortByDistance(dealerships, order = 'furthest') {
    return dealerships.sort((a, b) => {
      if (order === 'furthest') {
        return b.distanceMiles - a.distanceMiles
      } else {
        return a.distanceMiles - b.distanceMiles
      }
    })
  }

  // Get contact sequence
  getContactSequence(searchParams) {
    const eligibleDealers = this.getEligibleDealerships(searchParams)
    const sortedDealers = this.sortByDistance(eligibleDealers, 'furthest')

    return {
      totalCount: sortedDealers.length,
      sequence: sortedDealers,
      estimatedDuration: sortedDealers.length * 45 // 45 seconds per contact
    }
  }

  // Filter eligible dealerships for contact
  getEligibleDealerships(searchParams) {
    return dealerships.filter(dealer => {
      // Must be selected by user
      if (!dealer.selected) return false

      // Must be in pending or failed state for restart
      if (!['pending', 'failed'].includes(dealer.contactStatus)) return false

      // Must match search criteria
      if (searchParams.make !== 'All' && !dealer.make.includes(searchParams.make)) {
        return false
      }

      return true
    })
  }
}
```

### **Intelligent Restart Logic**

#### **Skip Already Contacted**
```javascript
class IntelligentRestartManager {
  // Determine restart behavior
  analyzeRestartOptions(dealerships) {
    const statusCounts = dealerships.reduce((counts, dealer) => {
      counts[dealer.contactStatus] = (counts[dealer.contactStatus] || 0) + 1
      return counts
    }, {})

    return {
      total: dealerships.length,
      pending: statusCounts.pending || 0,
      completed: statusCounts.completed || 0,
      failed: statusCounts.failed || 0,
      skipped: statusCounts.skipped || 0,
      canRestart: (statusCounts.pending + statusCounts.failed) > 0
    }
  }

  // Smart restart: only contact uncontacted dealerships
  performSmartRestart() {
    const analysis = this.analyzeRestartOptions(this.dealerships)

    if (!analysis.canRestart) {
      this.showMessage('No dealerships available for contact. All have been completed or skipped.')
      return false
    }

    const uncontactedDealers = this.dealerships.filter(dealer =>
      ['pending', 'failed'].includes(dealer.contactStatus) && dealer.selected
    )

    if (uncontactedDealers.length === 0) {
      this.showMessage('No uncontacted dealerships selected.')
      return false
    }

    // Show confirmation dialog
    const message = `Smart restart will contact ${uncontactedDealers.length} dealerships (${analysis.pending} pending, ${analysis.failed} failed). Continue?`

    if (confirm(message)) {
      this.startContactSequence(uncontactedDealers)
      return true
    }

    return false
  }

  // Handle partial completion scenarios
  resumeFromLastPosition() {
    const lastActive = this.dealerships.find(dealer =>
      dealer.contactStatus === 'active'
    )

    if (lastActive) {
      // Resume from paused state
      this.resumeContact(lastActive.id)
    } else {
      // Find next pending dealership
      const nextPending = this.getNextPendingDealer()
      if (nextPending) {
        this.startContact(nextPending.id)
      }
    }
  }
}
```

---

## 🔧 **Technical Implementation Details**

### **Browser Compatibility**
```javascript
// Feature detection and polyfills
class BrowserCompatibilityManager {
  constructor() {
    this.checkFeatureSupport()
    this.loadPolyfills()
  }

  checkFeatureSupport() {
    this.features = {
      indexedDB: 'indexedDB' in window,
      localStorage: 'localStorage' in window,
      fetch: 'fetch' in window,
      webWorkers: 'Worker' in window,
      notifications: 'Notification' in window
    }
  }

  loadPolyfills() {
    if (!this.features.fetch) {
      // Load fetch polyfill
      this.loadScript('https://polyfill.io/v3/polyfill.min.js?features=fetch')
    }
  }

  isSupported() {
    return this.features.localStorage && (this.features.indexedDB || true)
  }
}
```

### **Performance Optimization**

#### **Efficient Data Loading**
```javascript
class PerformanceOptimizer {
  // Lazy load dealership data
  async loadDealershipsInBatches(batchSize = 50) {
    const totalDealerships = await this.getTotalDealershipCount()
    const batches = Math.ceil(totalDealerships / batchSize)

    for (let i = 0; i < batches; i++) {
      const startIndex = i * batchSize
      const batch = await this.loadDealershipBatch(startIndex, batchSize)
      this.renderDealershipBatch(batch)

      // Allow UI to update between batches
      await new Promise(resolve => setTimeout(resolve, 10))
    }
  }

  // Virtualized scrolling for large lists
  implementVirtualScrolling() {
    const containerHeight = 600
    const itemHeight = 120
    const visibleItems = Math.ceil(containerHeight / itemHeight)
    const bufferSize = 5

    return {
      startIndex: Math.max(0, this.scrollTop - bufferSize),
      endIndex: Math.min(this.totalItems, this.scrollTop + visibleItems + bufferSize)
    }
  }

  // Debounced search
  debouncedSearch = this.debounce((searchTerm) => {
    this.performSearch(searchTerm)
  }, 300)
}
```

### **Error Handling and Recovery**

#### **Robust Error Management**
```javascript
class ErrorHandlingManager {
  constructor() {
    this.errorQueue = []
    this.retryQueue = []
    this.maxRetries = 3
  }

  // Handle contact automation errors
  handleContactError(dealershipId, error) {
    const errorRecord = {
      dealershipId,
      error: error.message,
      timestamp: new Date(),
      retryCount: 0
    }

    this.errorQueue.push(errorRecord)
    this.logError(errorRecord)

    // Determine if error is recoverable
    if (this.isRecoverableError(error)) {
      this.queueForRetry(errorRecord)
    } else {
      this.markAsFailed(dealershipId, error.message)
    }
  }

  // Recoverable error types
  isRecoverableError(error) {
    const recoverableErrors = [
      'network timeout',
      'temporary connection issue',
      'form not loaded yet',
      'element not found'
    ]

    return recoverableErrors.some(pattern =>
      error.message.toLowerCase().includes(pattern)
    )
  }

  // Automatic retry mechanism
  async retryFailedContacts() {
    while (this.retryQueue.length > 0) {
      const errorRecord = this.retryQueue.shift()

      if (errorRecord.retryCount >= this.maxRetries) {
        this.markAsFailed(errorRecord.dealershipId, 'Max retries exceeded')
        continue
      }

      try {
        errorRecord.retryCount++
        await this.attemptContact(errorRecord.dealershipId)
      } catch (error) {
        errorRecord.error = error.message
        this.retryQueue.push(errorRecord)
      }

      // Wait between retries
      await new Promise(resolve => setTimeout(resolve, 5000))
    }
  }
}
```

---

## 🚀 **Extensibility and Future Features**

### **Plugin Architecture**
```javascript
// Extensible contact methods
class ContactMethodRegistry {
  constructor() {
    this.methods = new Map()
    this.registerDefaultMethods()
  }

  registerDefaultMethods() {
    this.register('gravity_forms', new GravityFormsHandler())
    this.register('standard_forms', new StandardFormsHandler())
    this.register('email_fallback', new EmailFallbackHandler())
    this.register('manual_entry', new ManualEntryHandler())
  }

  register(name, handler) {
    this.methods.set(name, handler)
  }

  async executeContactMethod(methodName, dealership, customerInfo) {
    const handler = this.methods.get(methodName)
    if (!handler) throw new Error(`Contact method '${methodName}' not found`)

    return await handler.contact(dealership, customerInfo)
  }
}
```

### **Configuration Management**
```javascript
// User preferences and settings
class ConfigurationManager {
  constructor() {
    this.defaultConfig = {
      contactDelay: 30000,
      retryAttempts: 3,
      contactOrder: 'furthest',
      autoAdvance: true,
      notifications: true,
      theme: 'light',
      mapProvider: 'google'
    }

    this.loadUserConfig()
  }

  async loadUserConfig() {
    const stored = await this.storage.load('user_config')
    this.config = { ...this.defaultConfig, ...stored }
  }

  updateConfig(key, value) {
    this.config[key] = value
    this.storage.save('user_config', this.config)
    this.notifyConfigChange(key, value)
  }
}
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Core Infrastructure (Week 1)**
- [ ] Set up SPA framework (React/Vanilla JS)
- [ ] Implement IndexedDB storage layer
- [ ] Create Google Sheets integration
- [ ] Build basic three-panel layout
- [ ] Implement dealership data loading

### **Phase 2: Search and Management (Week 2)**
- [ ] Build search parameter controls
- [ ] Implement geographic distance calculation
- [ ] Create dealership filtering and sorting
- [ ] Add dealership selection controls
- [ ] Implement search expansion logic

### **Phase 3: Contact Management (Week 3)**
- [ ] Build contact status tracking
- [ ] Implement state management system
- [ ] Create contact sequence logic
- [ ] Add manual override capabilities
- [ ] Build intelligent restart mechanism

### **Phase 4: Automation Integration (Week 4)**
- [ ] Integrate form detection algorithms
- [ ] Implement contact automation engine
- [ ] Add error handling and retry logic
- [ ] Create progress tracking UI
- [ ] Build contact verification system

### **Phase 5: Polish and Deployment (Week 5)**
- [ ] Optimize performance
- [ ] Add data export capabilities
- [ ] Implement user configuration
- [ ] Create help documentation
- [ ] Deploy and test in production environment

---

## 🎯 **Success Criteria**

### **Functional Requirements**
- ✅ Single-page application with integrated workflow
- ✅ Local data persistence (no server required)
- ✅ Google Sheets integration for dealership data
- ✅ Contact sequencing (furthest first)
- ✅ Intelligent restart (skip contacted dealerships)
- ✅ Real-time contact status tracking

### **Performance Requirements**
- **Load Time**: <3 seconds for initial application load
- **Data Sync**: <10 seconds for Google Sheets sync
- **Contact Processing**: <60 seconds per dealership
- **UI Responsiveness**: <100ms for all user interactions

### **Usability Requirements**
- **Learning Curve**: New users productive within 10 minutes
- **Error Recovery**: Clear error messages and recovery options
- **Data Safety**: Automatic backup and recovery mechanisms
- **Browser Support**: Works in Chrome, Firefox, Safari, Edge

---

**📊 SPECIFICATION COMPLETE - READY FOR IMPLEMENTATION**

This specification provides a comprehensive blueprint for building a fully browser-based dealership contact management system that meets all your requirements while maintaining the flexibility for future enhancements.