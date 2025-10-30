# Simplified Local Dealership Contact Management System
## Technical Specification v2.0

**Approach**: Simplified Architecture
**Data Source**: Dealerships.csv with dynamic make field
**Storage**: LocalStorage only
**Dependencies**: None (fully offline-capable)

---

## 🎯 **Core Architecture Decisions**

### **1. Data Strategy: CSV + LocalStorage**
```javascript
// Single data source and storage method
class SimplifiedDataManager {
  constructor() {
    this.dealerships = []
    this.searches = []
    this.currentSearch = null
  }

  // One-time CSV import
  async importDealershipsCSV() {
    const csvData = await this.loadCSVFile('Dealerships.csv')
    this.dealerships = this.parseCSV(csvData)
    this.saveToLocalStorage('dealerships', this.dealerships)

    // Extract unique makes for dropdown
    this.availableMakes = this.getUniqueMakes()
  }

  getUniqueMakes() {
    const makes = [...new Set(this.dealerships.map(d => d.make))]
    return makes.sort() // ['Chrysler', 'Dodge', 'Jeep', 'Ram']
  }
}
```

### **2. State Model: Running ↔ Stopped**
```javascript
enum ContactState {
  STOPPED = 'stopped',  // Not running (default)
  RUNNING = 'running'   // Currently contacting dealerships
}

class SimpleContactManager {
  constructor() {
    this.state = 'stopped'
    this.currentDealerIndex = 0
  }

  start() {
    this.state = 'running'
    this.processNextDealer()
  }

  stop() {
    this.state = 'stopped'
    // Next start will resume from failures/pending
  }
}
```

### **3. Simplified Search Action**
```html
<!-- Simplified, safer user choice -->
<div class="search-actions">
  <button class="btn-primary" onclick="updateSearch()">
    🔍 Update Search
    <small>Find new dealerships, keep existing results</small>
  </button>
</div>
```

---

## 📊 **CSV Data Structure**

### **Dealerships.csv Format**
```csv
make,dealer_name,address,city,state,zip_code,phone,website,latitude,longitude
Jeep,Santa Monica Chrysler Jeep,3219 Santa Monica Blvd,Santa Monica,CA,90404,(310) 829-3200,https://www.santamonicachrysler.com,34.0345,-118.4845
Ram,Downtown Ram Center,123 Main St,Los Angeles,CA,90012,(213) 555-0123,https://www.downtownram.com,34.0522,-118.2437
Chrysler,Beverly Hills Chrysler,456 Wilshire Blvd,Beverly Hills,CA,90210,(310) 555-0456,https://www.bhchrysler.com,34.0736,-118.4004
Dodge,West Valley Dodge,789 Victory Blvd,Van Nuys,CA,91401,(818) 555-0789,https://www.wvdodge.com,34.1889,-118.4489
Ford,Future Ford Dealer,101 Ford Ave,Somewhere,CA,90000,(555) 123-4567,https://www.futureford.com,34.0000,-118.0000
```

### **CSV Parsing Implementation**
```javascript
class CSVDataParser {
  parseCSV(csvText) {
    const lines = csvText.split('\n')
    const headers = lines[0].split(',').map(h => h.trim())

    return lines.slice(1)
      .filter(line => line.trim()) // Skip empty lines
      .map((line, index) => {
        const values = this.parseCSVLine(line)
        const dealer = {}

        headers.forEach((header, i) => {
          dealer[header] = values[i] || ''
        })

        // Add tracking fields
        return {
          ...dealer,
          id: `dealer_${index}`,
          latitude: parseFloat(dealer.latitude),
          longitude: parseFloat(dealer.longitude),

          // Contact tracking fields
          contactStatus: 'pending',
          selected: true,
          lastContactedAt: null,
          contactSuccess: false,
          contactNotes: '',
          distanceMiles: 0 // Calculated during search
        }
      })
  }

  parseCSVLine(line) {
    // Handle CSV with quoted fields containing commas
    const result = []
    let current = ''
    let inQuotes = false

    for (let i = 0; i < line.length; i++) {
      const char = line[i]

      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }

    result.push(current.trim())
    return result
  }
}
```

---

## 🎨 **User Interface Design**

### **Unified Search Page Layout**
```html
<div class="dealership-management-app">
  <!-- Header -->
  <header class="app-header">
    <h1>🚗 Local Dealership Contact Manager</h1>
    <div class="search-info">
      <span class="search-name" v-if="currentSearch">{{currentSearch.name}}</span>
      <span class="search-stats" v-if="currentSearch">
        {{contactedCount}}/{{totalDealerships}} contacted
      </span>
    </div>
  </header>

  <!-- Main Content Grid -->
  <main class="main-grid">
    <!-- Left Panel: Search Parameters -->
    <section class="search-panel">
      <div class="panel-header">
        <h2>Search Parameters</h2>
        <button class="btn-edit" @click="toggleEditMode">
          {{editMode ? '💾 Save' : '✏️ Edit'}}
        </button>
      </div>

      <form class="search-form" @submit.prevent="handleSearchSubmit">
        <!-- Dynamic Make Dropdown -->
        <div class="form-group">
          <label>Vehicle Make</label>
          <select v-model="searchParams.make" :disabled="!editMode" required>
            <option value="">Select Make</option>
            <option v-for="make in availableMakes" :key="make" :value="make">
              {{make}} ({{getDealershipCount(make)}} dealers)
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Your Zipcode</label>
          <input type="text" v-model="searchParams.zipcode"
                 :disabled="!editMode" pattern="[0-9]{5}"
                 placeholder="90210" required>
        </div>

        <div class="form-group">
          <label>Search Distance</label>
          <select v-model="searchParams.distance" :disabled="!editMode" required>
            <option value="5">5 miles</option>
            <option value="10">10 miles</option>
            <option value="25">25 miles</option>
            <option value="50">50 miles</option>
            <option value="100">100 miles</option>
          </select>
        </div>

        <!-- Search Actions -->
        <div class="search-actions" v-if="editMode">
          <button type="button" class="btn-primary" @click="updateSearch">
            🔍 Update Search
            <small>Find new dealerships, keep existing results</small>
          </button>
        </div>
      </form>

      <!-- Customer Information -->
      <div class="customer-info">
        <h3>Customer Information</h3>
        <div class="form-grid">
          <input v-model="customerInfo.firstName" :disabled="!editMode"
                 placeholder="First Name" required>
          <input v-model="customerInfo.lastName" :disabled="!editMode"
                 placeholder="Last Name" required>
          <input v-model="customerInfo.email" :disabled="!editMode"
                 type="email" placeholder="Email" required>
          <input v-model="customerInfo.phone" :disabled="!editMode"
                 type="tel" placeholder="Phone" required>
        </div>

        <!-- Message Templates -->
        <div class="message-section">
          <label>Message Template</label>
          <select @change="applyMessageTemplate" v-if="editMode">
            <option value="">Choose template...</option>
            <option value="lease">Lease Inquiry</option>
            <option value="purchase">Purchase Inquiry</option>
            <option value="service">Service Inquiry</option>
            <option value="custom">Custom Message</option>
          </select>
          <textarea v-model="customerInfo.message" :disabled="!editMode"
                    rows="4" placeholder="Your message to dealerships..."></textarea>
        </div>
      </div>
    </section>

    <!-- Center Panel: Dealership List -->
    <section class="dealership-panel">
      <div class="panel-header">
        <h2>Found Dealerships</h2>
        <div class="list-controls">
          <!-- Bulk Selection -->
          <div class="bulk-controls">
            <button @click="selectAll">☑️ All</button>
            <button @click="selectNone">☐ None</button>
            <button @click="selectPending">⏳ Pending</button>
          </div>

          <!-- Sort Options -->
          <select v-model="sortBy" @change="sortDealerships">
            <option value="distance">Distance</option>
            <option value="name">Name</option>
            <option value="status">Status</option>
          </select>
        </div>
      </div>

      <!-- Dealership Cards -->
      <div class="dealership-list">
        <div v-for="(dealer, index) in sortedDealerships"
             :key="dealer.id"
             class="dealership-card"
             :class="dealer.contactStatus">

          <!-- Card Header -->
          <div class="card-header">
            <label class="checkbox-label">
              <input type="checkbox" v-model="dealer.selected">
              <span class="contact-order" v-if="dealer.selected">
                #{{getContactOrder(dealer)}}
              </span>
            </label>

            <div class="dealer-info">
              <h3>{{dealer.dealer_name}}</h3>
              <span class="distance-badge">{{dealer.distanceMiles}} miles</span>
            </div>

            <div class="status-indicator" :class="dealer.contactStatus">
              {{getStatusIcon(dealer.contactStatus)}}
            </div>
          </div>

          <!-- Card Body -->
          <div class="card-body">
            <p class="address">📍 {{dealer.address}}, {{dealer.city}}, {{dealer.state}}</p>
            <div class="contact-info">
              <span class="phone">📞 {{dealer.phone}}</span>
              <a :href="dealer.website" target="_blank" class="website">
                🌐 Visit Website
              </a>
            </div>
          </div>

          <!-- Card Actions -->
          <div class="card-actions">
            <button v-if="dealer.contactStatus === 'pending'"
                    class="btn-contact" @click="contactSingleDealer(dealer)">
              📞 Contact Now
            </button>
            <button v-if="dealer.contactStatus === 'failed'"
                    class="btn-retry" @click="retryContact(dealer)">
              🔄 Retry
            </button>
            <button class="btn-manual" @click="showManualOptions(dealer)">
              ✋ Manual
            </button>
            <button class="btn-skip" @click="skipDealer(dealer)">
              ⏭️ Skip
            </button>
          </div>

          <!-- Contact History (Expandable) -->
          <div class="contact-history" v-if="dealer.contactHistory && showHistory[dealer.id]">
            <div v-for="attempt in dealer.contactHistory" class="history-item">
              <span class="timestamp">{{formatTime(attempt.timestamp)}}</span>
              <span class="result" :class="attempt.success ? 'success' : 'failed'">
                {{attempt.success ? '✅ Success' : '❌ Failed'}}
              </span>
              <span class="details">{{attempt.details}}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Right Panel: Contact Status & Controls -->
    <section class="status-panel">
      <div class="panel-header">
        <h2>Contact Status</h2>
        <div class="status-badge" :class="contactState">
          {{getStatusDisplay()}}
        </div>
      </div>

      <!-- Contact Controls -->
      <div class="contact-controls">
        <button v-if="contactState === 'stopped'"
                class="btn-start" @click="startContacting"
                :disabled="!hasSelectedDealerships">
          ▶️ Start Contacting
          <small>{{selectedCount}} dealers (furthest first)</small>
        </button>

        <button v-if="contactState === 'running'"
                class="btn-stop" @click="stopContacting">
          ⏹️ Stop Contacting
        </button>

        <button v-if="hasFailedContacts && contactState === 'stopped'"
                class="btn-retry-failed" @click="retryFailedContacts">
          🔄 Retry Failed ({{failedCount}})
        </button>
      </div>

      <!-- Current Activity (when running) -->
      <div class="current-activity" v-if="contactState === 'running'">
        <h3>Currently Contacting</h3>
        <div class="current-dealer">
          <h4>{{currentDealer.dealer_name}}</h4>
          <p>{{currentDealer.address}}</p>
          <p class="distance">{{currentDealer.distanceMiles}} miles away</p>
        </div>

        <div class="progress-display">
          <div class="progress-bar">
            <div class="progress-fill" :style="{width: progressPercentage + '%'}"></div>
          </div>
          <p class="progress-text">
            {{contactedCount}} of {{selectedCount}} completed
          </p>
          <p class="time-estimate">
            Estimated time remaining: {{estimatedTimeRemaining}}
          </p>
        </div>
      </div>

      <!-- Results Summary -->
      <div class="results-summary">
        <h3>Contact Results</h3>
        <div class="stats-grid">
          <div class="stat-item success">
            <span class="count">{{successCount}}</span>
            <span class="label">Successful</span>
          </div>
          <div class="stat-item failed">
            <span class="count">{{failedCount}}</span>
            <span class="label">Failed</span>
          </div>
          <div class="stat-item pending">
            <span class="count">{{pendingCount}}</span>
            <span class="label">Pending</span>
          </div>
          <div class="stat-item rate">
            <span class="count">{{successRate}}%</span>
            <span class="label">Success Rate</span>
          </div>
        </div>
      </div>

      <!-- Export & Backup -->
      <div class="data-controls">
        <button class="btn-export" @click="exportResults">
          📊 Export Results
        </button>
        <button class="btn-backup" @click="createBackup">
          💾 Backup Data
        </button>
      </div>
    </section>
  </main>
</div>
```

---

## 🔧 **Core Implementation**

### **Dynamic Make Dropdown**
```javascript
class MakeManager {
  constructor(dealerships) {
    this.dealerships = dealerships
    this.availableMakes = this.extractUniqueMakes()
  }

  extractUniqueMakes() {
    const makes = [...new Set(this.dealerships.map(d => d.make))]
    return makes.sort()
  }

  getDealershipCount(make) {
    return this.dealerships.filter(d => d.make === make).length
  }

  // When CSV is updated, refresh makes
  refreshMakes(newDealerships) {
    this.dealerships = newDealerships
    this.availableMakes = this.extractUniqueMakes()
    this.updateMakeDropdown()
  }

  updateMakeDropdown() {
    const dropdown = document.getElementById('make-select')
    dropdown.innerHTML = '<option value="">Select Make</option>'

    this.availableMakes.forEach(make => {
      const count = this.getDealershipCount(make)
      const option = document.createElement('option')
      option.value = make
      option.textContent = `${make} (${count} dealers)`
      dropdown.appendChild(option)
    })
  }
}
```

### **Simplified Search Action Implementation**
```javascript
class SimplifiedSearchManager {
  // Note: In the final Vue app, this logic is integrated into the `updateSearch` method.
  // The `customerInfo` and `searchParams` are component data properties.

  findDealershipsForParams(customerInfo, searchParams) {
    // Filter by make
    let filtered = this.dealerships.filter(d => d.make === searchParams.make);

    // Get user's location from the single zip code field in customerInfo
    const userCoords = this.geocodeZipcode(customerInfo.zipcode); 
    if (!userCoords) {
        console.error("Invalid Zipcode");
        return [];
    }

    // Calculate distances and filter by radius
    return filtered
      .map(dealer => {
        const distance = this.calculateDistance(
          userCoords.lat, userCoords.lng,
          dealer.latitude, dealer.longitude
        );
        return { ...dealer, distanceMiles: Math.round(distance * 10) / 10 };
      })
      .filter(dealer => dealer.distanceMiles <= searchParams.distance)
      .sort((a, b) => b.distanceMiles - a.distanceMiles); // Furthest first
  }
}
```

### **Contact Order: Furthest First**
```javascript
class ContactOrderManager {
  getContactOrder(dealerships) {
    const selectedDealerships = dealerships.filter(d =>
      d.selected && ['pending', 'failed'].includes(d.contactStatus)
    )

    // Sort by distance: furthest first
    return selectedDealerships.sort((a, b) => b.distanceMiles - a.distanceMiles)
  }

  getContactOrderNumber(dealer, allDealerships) {
    const orderedList = this.getContactOrder(allDealerships)
    const index = orderedList.findIndex(d => d.id === dealer.id)
    return index >= 0 ? index + 1 : null
  }

  updateContactOrderDisplay(dealerships) {
    const orderedList = this.getContactOrder(dealerships)

    // Update UI to show contact order
    orderedList.forEach((dealer, index) => {
      const element = document.querySelector(`[data-dealer-id="${dealer.id}"] .contact-order`)
      if (element) {
        element.textContent = `#${index + 1}`
        element.title = `Will be contacted ${this.getOrdinalSuffix(index + 1)} (${dealer.distanceMiles} miles)`
      }
    })
  }

  getOrdinalSuffix(num) {
    const suffixes = ['th', 'st', 'nd', 'rd']
    const value = num % 100
    return suffixes[(value - 20) % 10] || suffixes[value] || suffixes[0]
  }
}
```

---

## 💾 **Simplified Data Persistence**

### **LocalStorage-Only Architecture**
```javascript
class SimplifiedStorageManager {
  constructor() {
    this.storageKeys = {
      dealerships: 'ddm_dealerships',
      searches: 'ddm_searches',
      currentSearch: 'ddm_current_search',
      userPreferences: 'ddm_preferences',
      backups: 'ddm_backups'
    }
  }

  // Save data to localStorage
  save(key, data) {
    try {
      const serialized = JSON.stringify(data)
      localStorage.setItem(this.storageKeys[key], serialized)
      return true
    } catch (error) {
      console.error('Storage save failed:', error)
      this.handleStorageError(error)
      return false
    }
  }

  // Load data from localStorage
  load(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(this.storageKeys[key])
      return item ? JSON.parse(item) : defaultValue
    } catch (error) {
      console.error('Storage load failed:', error)
      return defaultValue
    }
  }

  // Auto-backup every hour
  startAutoBackup() {
    setInterval(() => {
      this.createBackup()
    }, 3600000) // 1 hour

    // Also backup before page unload
    window.addEventListener('beforeunload', () => {
      this.createBackup()
    })
  }

  createBackup() {
    const backup = {
      version: '2.0',
      timestamp: new Date().toISOString(),
      data: {
        dealerships: this.load('dealerships'),
        searches: this.load('searches'),
        currentSearch: this.load('currentSearch'),
        userPreferences: this.load('userPreferences')
      }
    }

    // Keep only last 5 backups
    const backups = this.load('backups', [])
    backups.push(backup)
    if (backups.length > 5) {
      backups.shift()
    }

    this.save('backups', backups)
  }

  restoreFromBackup(backupIndex = 0) {
    const backups = this.load('backups', [])
    if (backups.length === 0) {
      throw new Error('No backups available')
    }

    const backup = backups[backupIndex]
    if (!backup) {
      throw new Error('Backup not found')
    }

    // Restore all data
    Object.entries(backup.data).forEach(([key, value]) => {
      if (value !== null) {
        this.save(key, value)
      }
    })

    return backup.timestamp
  }
}
```

---

## 🚀 **Enhanced Features (Low Complexity)**

### **Message Templates**
```javascript
const messageTemplates = {
  lease: "Hi, I'm interested in leasing a {make}. Could you please send me information about current lease deals and availability? My zipcode is {zipcode}. Thanks!",

  purchase: "Hello, I'm looking to purchase a {make}. What inventory do you currently have available? I'm located in {zipcode}.",

  service: "Hi, I need service for my {make}. What are your current availability and rates? I'm in the {zipcode} area.",

  custom: ""
}

function applyMessageTemplate(templateKey, customerInfo, searchParams) {
  let template = messageTemplates[templateKey]
  if (!template) return

  // Replace placeholders
  template = template
    .replace('{make}', searchParams.make)
    .replace('{zipcode}', customerInfo.zipcode || searchParams.zipcode)
    .replace('{firstName}', customerInfo.firstName)
    .replace('{lastName}', customerInfo.lastName)

  document.getElementById('message-textarea').value = template
}
```

### **Contact Fallback Options**
```html
<!-- When automation fails -->
<div class="contact-fallback-modal" v-if="showFallback">
  <div class="modal-content">
    <h3>❌ Automation Failed: {{failedDealer.dealer_name}}</h3>
    <p class="error-message">{{failureReason}}</p>

    <div class="fallback-options">
      <h4>Manual Contact Options:</h4>

      <button class="fallback-btn" @click="copyContactInfo">
        📋 Copy Contact Info
        <small>Copy dealer info to clipboard</small>
      </button>

      <button class="fallback-btn" @click="openWebsite">
        🌐 Open Website
        <small>Open dealer website in new tab</small>
      </button>

      <button class="fallback-btn" @click="dialPhone">
        📞 Call Dealer
        <small>{{failedDealer.phone}}</small>
      </button>

      <button class="fallback-btn" @click="markAsManuallyContacted">
        ✅ Mark as Contacted
        <small>I'll contact them manually</small>
      </button>

      <button class="fallback-btn" @click="skipDealer">
        ⏭️ Skip This Dealer
        <small>Move to next dealership</small>
      </button>
    </div>
  </div>
</div>
```

### **Simple Export Features**
```javascript
class ExportManager {
  exportSearchResults(search) {
    const exportData = {
      searchInfo: {
        name: search.name,
        parameters: search.parameters,
        createdAt: search.createdAt,
        lastModified: search.lastModified
      },
      customerInfo: search.customerInfo,
      dealerships: search.dealerships.map(d => ({
        dealer_name: d.dealer_name,
        address: d.address,
        city: d.city,
        state: d.state,
        phone: d.phone,
        website: d.website,
        distance_miles: d.distanceMiles,
        contact_status: d.contactStatus,
        last_contacted: d.lastContactedAt,
        contact_success: d.contactSuccess,
        notes: d.contactNotes
      })),
      summary: this.generateSummary(search)
    }

    this.downloadJSON(exportData, `search-results-${search.name}-${Date.now()}.json`)
  }

  exportToCSV(search) {
    const headers = [
      'Dealer Name', 'Address', 'City', 'State', 'Phone', 'Website',
      'Distance (miles)', 'Contact Status', 'Last Contacted', 'Success', 'Notes'
    ]

    const rows = search.dealerships.map(d => [
      d.dealer_name, d.address, d.city, d.state, d.phone, d.website,
      d.distanceMiles, d.contactStatus, d.lastContactedAt || '',
      d.contactSuccess ? 'Yes' : 'No', d.contactNotes || ''
    ])

    const csvContent = [headers, ...rows]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n')

    this.downloadCSV(csvContent, `dealerships-${search.name}-${Date.now()}.csv`)
  }
}
```

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create simplified technical specification", "status": "completed", "activeForm": "Creating simplified technical specification"}, {"content": "Explain explicit actions enhancement in detail", "status": "completed", "activeForm": "Explaining explicit actions enhancement"}, {"content": "Design dynamic make dropdown from CSV", "status": "completed", "activeForm": "Designing dynamic make dropdown from CSV"}, {"content": "Update data flow for simplified approach", "status": "completed", "activeForm": "Updating data flow for simplified approach"}]