# Refined Local Dealership Contact Management System
## Updated Requirements Specification

**Updated**: September 2024
**Based on**: Clarified user requirements

---

## 🎯 **Key Requirement Updates**

### **1. Unified Search Page Architecture**

**Single Page Design**: All functionality integrated into one cohesive interface
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Local Dealership Contact Management - [Search Name]                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐ │
│  │ Search Params   │  │ Found Dealers    │  │ Contact Status & Ctrl   │ │
│  │ ┌─────────────┐ │  │ ☑️ Dealer A (50mi)│  │ State: 🟢 Contacting    │ │
│  │ │Make: Jeep ▼ │ │  │ ☑️ Dealer B (45mi)│  │ Current: Dealer A       │ │
│  │ │Zip: [90210] │ │  │ ☐ Dealer C (40mi)│  │ Progress: 2/5 contacted │ │
│  │ │Miles: [25▼] │ │  │ ✅ Dealer D (35mi)│  │                         │ │
│  │ │[Edit] [Save]│ │  │ ❌ Dealer E (30mi)│  │ [⏸️ Pause] [⏹️ Stop]     │ │
│  │ └─────────────┘ │  └──────────────────┘  └─────────────────────────┘ │
│  └─────────────────┘                                                    │
│                                                                         │
│  Customer Information (Editable)                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Name: [John] [Smith]  Email: [john@email.com]  Phone: [(555)123-4567]││
│  │ Message: [I'm interested in leasing a Jeep...]          [Edit][Save] ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

**Core Principle**: Everything related to a search appears on one page - no navigation between different views.

### **2. Editable Search Fields Behavior**

#### **Edit Mode Workflow**
```javascript
// Edit button clicked
function enterEditMode() {
  // 1. Immediately pause auto-contacting if active
  if (autoContactingState === 'contacting') {
    pauseAutoContacting()
    showMessage("Auto-contacting paused for editing")
  }

  // 2. Enable all form fields
  enableFormFields(['make', 'zipcode', 'distance', 'firstName', 'lastName', 'email', 'phone', 'message'])

  // 3. Show Save/Cancel buttons
  showEditControls()
}

// Save button clicked
function saveSearchChanges() {
  // 1. Validate new parameters
  const newParams = validateSearchParameters()

  // 2. Update dealership list if search parameters changed
  if (searchParametersChanged(newParams)) {
    updateDealershipList(newParams)
  }

  // 3. Update customer information for future contacts
  updateCustomerInfo(newParams.customerInfo)

  // 4. Exit edit mode (auto-contacting remains paused)
  exitEditMode()

  // 5. User must manually restart contacting
  showMessage("Changes saved. Click 'Start Contacting' to resume with updated information.")
}
```

#### **Field Update Impact**
```typescript
interface EditableFields {
  // Search Parameters (affects dealership discovery)
  make: string           // Changes: Redo search, add new dealers
  zipcode: string        // Changes: Redo search completely
  distance: number       // Changes: Expand/contract dealer list

  // Customer Information (affects future contacts only)
  firstName: string      // Changes: Update for uncontacted dealers
  lastName: string       // Changes: Update for uncontacted dealers
  email: string         // Changes: Update for uncontacted dealers
  phone: string         // Changes: Update for uncontacted dealers
  message: string       // Changes: Update for uncontacted dealers
}
```

### **3. Auto-Contacting States with Visual Indicators**

#### **Three Primary States**
```typescript
enum AutoContactingState {
  CONTACTING = 'contacting',  // Active - currently contacting dealerships
  PAUSED = 'paused',         // Paused - can be resumed
  DONE = 'done'              // Completed - all eligible dealers processed
}
```

#### **Visual State Indicators**
```html
<!-- State: CONTACTING -->
<div class="contact-status contacting">
  <div class="status-indicator">
    <span class="pulse-dot"></span>
    <span class="status-text">🟢 Contacting</span>
  </div>
  <div class="current-activity">
    <p>Currently contacting: <strong>Santa Monica Chrysler Jeep</strong></p>
    <div class="progress-bar">
      <div class="progress-fill" style="width: 40%"></div>
    </div>
    <p class="progress-text">2 of 5 dealerships contacted</p>
  </div>
  <div class="controls">
    <button class="btn-pause" onclick="pauseContacting()">⏸️ Pause</button>
    <button class="btn-stop" onclick="stopContacting()">⏹️ Stop</button>
  </div>
</div>

<!-- State: PAUSED -->
<div class="contact-status paused">
  <div class="status-indicator">
    <span class="pause-icon"></span>
    <span class="status-text">🟡 Paused</span>
  </div>
  <div class="paused-info">
    <p>Paused at: <strong>Santa Monica Chrysler Jeep</strong></p>
    <p>Progress: 2 of 5 dealerships contacted</p>
  </div>
  <div class="controls">
    <button class="btn-resume" onclick="resumeContacting()">▶️ Resume</button>
    <button class="btn-stop" onclick="stopContacting()">⏹️ Stop</button>
  </div>
</div>

<!-- State: DONE -->
<div class="contact-status done">
  <div class="status-indicator">
    <span class="check-icon"></span>
    <span class="status-text">✅ Done</span>
  </div>
  <div class="completion-summary">
    <p>All dealerships processed</p>
    <div class="results-summary">
      <span class="success-count">✅ 3 contacted</span>
      <span class="failed-count">❌ 1 failed</span>
      <span class="skipped-count">⏭️ 1 skipped</span>
    </div>
  </div>
  <div class="controls">
    <button class="btn-restart" onclick="smartRestart()">🔄 Restart Failed</button>
    <button class="btn-export" onclick="exportResults()">📊 Export Results</button>
  </div>
</div>
```

### **4. Contact Order: Furthest First Implementation**

#### **Distance-Based Sequencing Logic**
```javascript
class ContactSequencer {
  // Sort dealerships by distance (furthest first)
  getContactOrder(dealerships) {
    const eligibleDealers = dealerships.filter(dealer =>
      dealer.selected &&
      ['pending', 'failed'].includes(dealer.contactStatus)
    )

    // Sort by distance: furthest first
    return eligibleDealers.sort((a, b) => b.distanceMiles - a.distanceMiles)
  }

  // Visual indication of contact order
  updateContactOrderDisplay(dealerships) {
    const sequence = this.getContactOrder(dealerships)

    sequence.forEach((dealer, index) => {
      const dealerCard = document.getElementById(`dealer-${dealer.id}`)
      const orderBadge = dealerCard.querySelector('.contact-order')
      orderBadge.textContent = `#${index + 1}`
      orderBadge.title = `Will be contacted ${index + 1}${this.getOrdinalSuffix(index + 1)} (${dealer.distanceMiles} miles)`
    })
  }
}
```

#### **Contact Progress Visualization**
```html
<div class="contact-sequence-preview">
  <h3>Contact Order (Furthest First)</h3>
  <div class="sequence-list">
    <div class="sequence-item next">
      <span class="order-number">1</span>
      <span class="dealer-name">West Valley Jeep</span>
      <span class="distance">47.2 miles</span>
      <span class="status">⏳ Next</span>
    </div>
    <div class="sequence-item pending">
      <span class="order-number">2</span>
      <span class="dealer-name">Downtown Motors</span>
      <span class="distance">45.8 miles</span>
      <span class="status">⏳ Pending</span>
    </div>
    <div class="sequence-item completed">
      <span class="order-number">3</span>
      <span class="dealer-name">Metro Chrysler</span>
      <span class="distance">42.1 miles</span>
      <span class="status">✅ Contacted</span>
    </div>
  </div>
</div>
```

### **5. Dynamic Search Parameters - Additive Behavior**

#### **Search Parameter Change Logic**
```javascript
class DynamicSearchManager {
  // Handle search parameter updates
  async updateSearchParameters(newParams) {
    const currentParams = this.getCurrentSearchParams()
    const changes = this.detectChanges(currentParams, newParams)

    if (changes.zipcode) {
      // Complete location change - new search
      await this.performNewSearch(newParams)
    } else if (changes.distance) {
      // Distance expansion/contraction - additive
      await this.updateSearchRadius(newParams.distance)
    } else if (changes.make) {
      // Make change - filter existing + add new
      await this.updateMakeFilter(newParams.make)
    }

    // Always preserve existing dealership statuses
    this.preserveExistingStatuses()
  }

  // Expand search radius - additive only
  async expandSearchRadius(newRadius) {
    const currentDealers = this.getCurrentDealerships()
    const currentRadius = this.getCurrentRadius()

    if (newRadius <= currentRadius) {
      // No expansion needed, just filter current list
      this.filterByRadius(currentDealers, newRadius)
      return
    }

    // Find additional dealerships in expanded area
    const additionalDealers = await this.findDealershipsInRange(
      this.getUserLocation(),
      currentRadius + 1, // Start from just beyond current radius
      newRadius           // Up to new radius
    )

    // Add new dealerships with 'pending' status
    const newDealers = additionalDealers.map(dealer => ({
      ...dealer,
      contactStatus: 'pending',
      selected: true,
      addedAt: new Date()
    }))

    // Merge with existing (preserving all existing statuses)
    this.mergeDealerships(currentDealers, newDealers)
  }

  // Preserve existing dealership contact statuses
  preserveExistingStatuses() {
    // Never change status of dealerships that have been:
    // - contacted (successful)
    // - failed
    // - manually skipped
    // - manually marked as contacted

    const protectedStatuses = ['contacted', 'failed', 'skipped', 'manual']

    this.dealerships.forEach(dealer => {
      if (protectedStatuses.includes(dealer.contactStatus)) {
        dealer.protected = true // Mark as unchangeable
      }
    })
  }
}
```

#### **Example: Distance Expansion Workflow**
```
Initial Search: Jeep dealers within 25 miles of 90210
Results: 3 dealerships found
│
├─ User expands to 50 miles
│
├─ System finds 4 additional dealerships (26-50 miles)
│
└─ Final Result: 7 dealerships total
   ├─ Original 3: Keep existing contact statuses
   └─ New 4: Added with 'pending' status
```

---

## 🔧 **Implementation Details**

### **Unified Page Architecture**

#### **Single Page Component Structure**
```typescript
interface UnifiedSearchPage {
  // Page state
  searchId: string
  searchName: string
  isEditMode: boolean
  autoContactingState: AutoContactingState

  // Data
  searchParameters: SearchParameters
  customerInfo: CustomerInfo
  dealerships: Dealership[]
  contactProgress: ContactProgress

  // Component sections
  searchParamsSection: SearchParametersComponent
  dealershipListSection: DealershipListComponent
  contactStatusSection: ContactStatusComponent
  customerInfoSection: CustomerInfoComponent
}
```

#### **State Management**
```javascript
class UnifiedPageStateManager {
  constructor() {
    this.state = {
      editMode: false,
      autoContactingState: 'done',
      currentContactIndex: -1,
      searchParameters: {},
      customerInfo: {},
      dealerships: [],
      unsavedChanges: false
    }
  }

  // Enter edit mode
  enterEditMode() {
    if (this.state.autoContactingState === 'contacting') {
      this.pauseAutoContacting()
    }

    this.setState({
      editMode: true,
      autoContactingState: 'paused'
    })

    this.enableFormEditing()
  }

  // Save changes and exit edit mode
  async saveChanges(newData) {
    // Detect what changed
    const changes = this.detectChanges(this.state, newData)

    // Update search parameters if needed
    if (changes.searchParameters) {
      await this.updateSearchResults(newData.searchParameters)
    }

    // Update customer info
    if (changes.customerInfo) {
      this.updateCustomerInfo(newData.customerInfo)
    }

    // Exit edit mode
    this.setState({
      editMode: false,
      unsavedChanges: false,
      ...newData
    })

    // Auto-contacting remains paused - requires manual restart
    this.showMessage("Changes saved. Auto-contacting remains paused.")
  }
}
```

### **Local Data Persistence Strategy**

#### **IndexedDB Schema for Refined Requirements**
```javascript
const databaseSchema = {
  name: 'DealershipContactDB',
  version: 2, // Updated for new requirements
  stores: {
    searches: {
      keyPath: 'id',
      indexes: {
        name: 'searchName',
        createdAt: 'createdAt',
        lastModified: 'lastModified'
      },
      structure: {
        id: 'string',
        searchName: 'string',
        searchParameters: 'object',
        customerInfo: 'object',
        dealerships: 'object[]',
        autoContactingState: 'string',
        currentContactIndex: 'number',
        createdAt: 'date',
        lastModified: 'date'
      }
    },

    contactHistory: {
      keyPath: 'id',
      autoIncrement: true,
      indexes: {
        searchId: 'searchId',
        dealershipId: 'dealershipId',
        timestamp: 'contactedAt'
      }
    },

    userPreferences: {
      keyPath: 'key',
      structure: {
        key: 'string',
        value: 'any',
        updatedAt: 'date'
      }
    }
  }
}
```

#### **Google Sheets Integration for Dealership Data**
```javascript
class GoogleSheetsDataSource {
  constructor() {
    this.sheetId = 'your_google_sheet_id'
    this.apiKey = 'your_api_key'
    this.cache = new Map()
    this.cacheExpiry = 3600000 // 1 hour
  }

  async fetchDealershipData() {
    // Check cache first
    const cached = this.cache.get('dealerships')
    if (cached && (Date.now() - cached.timestamp) < this.cacheExpiry) {
      return cached.data
    }

    // Fetch from Google Sheets
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${this.sheetId}/values/Dealerships!A:Z?key=${this.apiKey}`

    try {
      const response = await fetch(url)
      const data = await response.json()

      const dealerships = this.parseSheetData(data.values)

      // Cache the results
      this.cache.set('dealerships', {
        data: dealerships,
        timestamp: Date.now()
      })

      return dealerships
    } catch (error) {
      console.error('Failed to fetch dealership data:', error)
      // Return cached data if available, even if expired
      return cached?.data || []
    }
  }

  parseSheetData(rows) {
    const [headers, ...dataRows] = rows

    return dataRows.map(row => {
      const dealer = {}
      headers.forEach((header, index) => {
        dealer[header.toLowerCase().replace(/\s+/g, '_')] = row[index] || ''
      })

      // Ensure required fields
      return {
        id: dealer.id || `dealer_${Date.now()}_${Math.random()}`,
        dealer_name: dealer.dealer_name,
        address: dealer.address,
        city: dealer.city,
        state: dealer.state,
        zipcode: dealer.zipcode,
        phone: dealer.phone,
        website: dealer.website,
        latitude: parseFloat(dealer.latitude),
        longitude: parseFloat(dealer.longitude),
        make: dealer.make ? dealer.make.split(',').map(m => m.trim()) : [],

        // Add default contact tracking fields
        contactStatus: 'pending',
        selected: true,
        lastContactedAt: null,
        contactSuccess: false,
        contactNotes: ''
      }
    })
  }
}
```

---

## 📱 **Updated UI Components**

### **Editable Search Parameters Section**
```html
<div class="search-parameters-section">
  <div class="section-header">
    <h2>Search Parameters</h2>
    <button class="btn-edit" onclick="enterEditMode()" v-if="!editMode">✏️ Edit</button>
    <div class="edit-controls" v-if="editMode">
      <button class="btn-save" onclick="saveChanges()">💾 Save</button>
      <button class="btn-cancel" onclick="cancelEdit()">❌ Cancel</button>
    </div>
  </div>

  <div class="parameters-grid">
    <div class="parameter-field">
      <label>Vehicle Make</label>
      <select name="make" :disabled="!editMode" v-model="searchParams.make">
        <option value="Jeep">Jeep</option>
        <option value="Ram">Ram</option>
        <option value="Chrysler">Chrysler</option>
        <option value="Dodge">Dodge</option>
      </select>
    </div>

    <div class="parameter-field">
      <label>Zipcode</label>
      <input type="text" name="zipcode" :disabled="!editMode"
             v-model="searchParams.zipcode" pattern="[0-9]{5}">
    </div>

    <div class="parameter-field">
      <label>Distance (miles)</label>
      <select name="distance" :disabled="!editMode" v-model="searchParams.distance">
        <option value="5">5 miles</option>
        <option value="10">10 miles</option>
        <option value="25">25 miles</option>
        <option value="50">50 miles</option>
        <option value="100">100 miles</option>
      </select>
    </div>
  </div>

  <!-- Show parameter change preview -->
  <div class="parameter-changes" v-if="editMode && hasChanges">
    <h4>⚠️ Changes Preview</h4>
    <ul>
      <li v-if="changedParams.distance">
        Distance change: {{currentParams.distance}} → {{changedParams.distance}} miles
        <span class="change-impact">Will find {{estimatedNewDealers}} additional dealerships</span>
      </li>
      <li v-if="changedParams.make">
        Make change: {{currentParams.make}} → {{changedParams.make}}
        <span class="change-impact">Will filter existing + add new dealerships</span>
      </li>
    </ul>
  </div>
</div>
```

### **Enhanced Contact Status Section**
```html
<div class="contact-status-section">
  <div class="section-header">
    <h2>Contact Status</h2>
    <div class="status-badge" :class="autoContactingState">
      {{getStatusDisplay()}}
    </div>
  </div>

  <!-- Active Contacting State -->
  <div class="status-display contacting" v-if="autoContactingState === 'contacting'">
    <div class="current-activity">
      <div class="activity-header">
        <span class="pulse-indicator"></span>
        <span class="activity-text">Currently contacting</span>
      </div>
      <div class="current-dealer">
        <h3>{{currentDealer.dealerName}}</h3>
        <p>{{currentDealer.address}} ({{currentDealer.distanceMiles}} miles)</p>
      </div>
      <div class="progress-display">
        <div class="progress-bar">
          <div class="progress-fill" :style="{width: progressPercentage + '%'}"></div>
        </div>
        <div class="progress-text">
          {{contactedCount}} of {{totalDealerships}} dealerships contacted
        </div>
      </div>
    </div>

    <div class="contacting-controls">
      <button class="btn-pause" onclick="pauseContacting()">
        ⏸️ Pause
      </button>
      <button class="btn-stop" onclick="stopContacting()">
        ⏹️ Stop
      </button>
    </div>
  </div>

  <!-- Paused State -->
  <div class="status-display paused" v-if="autoContactingState === 'paused'">
    <div class="pause-info">
      <p class="pause-reason">{{pauseReason}}</p>
      <p class="pause-position">
        Paused at: <strong>{{pausedDealer.dealerName}}</strong>
      </p>
      <p class="pause-progress">
        Progress: {{contactedCount}} of {{totalDealerships}} contacted
      </p>
    </div>

    <div class="paused-controls">
      <button class="btn-resume" onclick="resumeContacting()">
        ▶️ Resume
      </button>
      <button class="btn-stop" onclick="stopContacting()">
        ⏹️ Stop
      </button>
    </div>
  </div>

  <!-- Done State -->
  <div class="status-display done" v-if="autoContactingState === 'done'">
    <div class="completion-summary">
      <h3>✅ All dealerships processed</h3>
      <div class="results-breakdown">
        <div class="result-item success">
          <span class="count">{{results.contacted}}</span>
          <span class="label">Successfully contacted</span>
        </div>
        <div class="result-item failed">
          <span class="count">{{results.failed}}</span>
          <span class="label">Failed to contact</span>
        </div>
        <div class="result-item skipped">
          <span class="count">{{results.skipped}}</span>
          <span class="label">Skipped</span>
        </div>
      </div>
    </div>

    <div class="done-controls">
      <button class="btn-restart" onclick="smartRestart()" v-if="results.failed > 0">
        🔄 Retry Failed ({{results.failed}})
      </button>
      <button class="btn-export" onclick="exportResults()">
        📊 Export Results
      </button>
      <button class="btn-new-search" onclick="createNewSearch()">
        ➕ New Search
      </button>
    </div>
  </div>
</div>
```

---

## 🔄 **Key Workflow Updates**

### **Edit → Save → Manual Restart Workflow**
```
1. User clicks "Edit" → Auto-contacting pauses immediately
2. User modifies fields → System shows preview of changes
3. User clicks "Save" → Changes applied, new dealerships added if needed
4. Auto-contacting remains paused → User must manually restart
5. Manual restart → Only contacts uncontacted dealerships with new data
```

### **Dynamic Search Behavior**
```
Scenario: User expands distance from 25 to 50 miles

Before:
- 3 dealerships found (25 miles)
- 2 contacted, 1 pending

After expansion:
- 3 original dealerships (statuses preserved)
- 4 new dealerships added (pending status)
- Total: 7 dealerships (2 contacted, 5 pending)

Next contact session will:
- Skip the 2 already contacted
- Contact the 5 pending (using updated customer info)
- Start with furthest of the 5 pending
```

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Update specification with clarified requirements", "status": "completed", "activeForm": "Updating specification with clarified requirements"}, {"content": "Design unified search page with editable fields", "status": "completed", "activeForm": "Designing unified search page with editable fields"}, {"content": "Specify auto-contacting state management and visual indicators", "status": "completed", "activeForm": "Specifying auto-contacting state management"}, {"content": "Define dynamic search parameter behavior", "status": "completed", "activeForm": "Defining dynamic search parameter behavior"}]