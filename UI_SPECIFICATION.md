# Lease Deal Search UI Specification

**System Overview**: Complete web-based interface for automotive dealership contact automation with geographic discovery and progress tracking.

## 🎯 **Core User Flow**

### Primary Journey
```
Search Management → Create New Search → Dealership Discovery → Contact Automation → Progress Tracking
```

### Business Value
- **For Customers**: Find and contact multiple dealerships efficiently
- **For Business**: Scalable lead generation with high success rates
- **Technical**: 90%+ automation success rate with manual override capabilities

---

## 📱 **1. Search Management Dashboard**

### **Page Layout**
```
┌─────────────────────────────────────────────────────────────┐
│  🚗 Lease Deal Search System                    [+ New Search] │
├─────────────────────────────────────────────────────────────┤
│  📊 Active Searches (3)                     🔍 [Search Box]  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🏷️ "Beverly Hills Jeep Search"        📅 2 days ago   │   │
│  │ 📍 90210, 25 miles • Jeep • 5 dealerships           │   │
│  │ ⚡ Status: 3 contacted, 2 pending    [View] [Resume] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🏷️ "NYC Ram Dealers"                  📅 1 week ago   │   │
│  │ 📍 10001, 15 miles • Ram • 8 dealerships            │   │
│  │ ✅ Status: Complete (8/8)            [View] [Export] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  📚 Archived Searches (12)                    [Show All]    │
└─────────────────────────────────────────────────────────────┘
```

### **Search Card Components**
- **Status Indicators**: Active, Complete, Paused, Error
- **Progress Metrics**: "3/5 contacted", "Success rate: 80%"
- **Quick Actions**: View, Resume, Export, Archive, Delete
- **Sorting**: Date created, Last activity, Success rate, Name

### **Filters & Search**
- **Status Filter**: All, Active, Complete, Paused
- **Make Filter**: All, Jeep, Ram, Chrysler, Dodge
- **Date Range**: Last 7 days, Last 30 days, Custom
- **Text Search**: Search by name, zipcode, or make

---

## 🔧 **2. Create New Search Form**

### **Form Layout (Step-by-Step)**

#### **Step 1: Search Details**
```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Create New Search                           Step 1 of 3  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Search Name *                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Beverly Hills Jeep Search                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Vehicle Make *                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Jeep                                              ▼    │ │
│  └────────────────────────────────────────────────────────┘ │
│  Options: Jeep (1,791), Ram (1,341), Chrysler (987), Dodge  │
│                                                              │
│  Customer Location *                                         │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐│
│  │ 90210           │  │ Within 25 miles              ▼     ││
│  └─────────────────┘  └─────────────────────────────────────┘│
│  📍 Beverly Hills, CA                                        │
│                                                              │
│                               [Cancel]        [Next Step →] │
└─────────────────────────────────────────────────────────────┘
```

#### **Step 2: Customer Information**
```
┌─────────────────────────────────────────────────────────────┐
│  👤 Customer Information                        Step 2 of 3  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐│
│  │ First Name *        │  │ Last Name *                     ││
│  │ John                │  │ Smith                           ││
│  └─────────────────────┘  └─────────────────────────────────┘│
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐│
│  │ Phone *             │  │ Email *                         ││
│  │ (555) 123-4567      │  │ john.smith@email.com            ││
│  └─────────────────────┘  └─────────────────────────────────┘│
│                                                              │
│  Customer Zipcode                                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 90210                                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  💡 Uses search location if blank                            │
│                                                              │
│  Inquiry Message                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Hi, I'm interested in leasing a Jeep. Could you        │ │
│  │ please send me information about current deals and     │ │
│  │ availability? Thanks!                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│                        [← Back]        [Next: Find Dealers] │
└─────────────────────────────────────────────────────────────┘
```

#### **Step 3: Dealership Discovery**
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Found 5 Jeep Dealerships                   Step 3 of 3  │
├─────────────────────────────────────────────────────────────┤
│  📍 Within 25 miles of Beverly Hills, CA (90210)            │
│                                                              │
│  ☑️ Select All (5)  │  ⚡ Auto-Contact: ☑️ Enabled          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ☑️  🏪 Santa Monica Chrysler Jeep           📏 5.0 mi  │ │
│  │     📍 3219 Santa Monica Blvd, Santa Monica, CA       │ │
│  │     📞 310-829-3200  🌐 santamonicachrysler.com       │ │
│  │     ✅ Contact form detected                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ☑️  🏪 Galpin Jeep                          📏 12.3 mi │ │
│  │     📍 15555 Roscoe Blvd, North Hills, CA             │ │
│  │     📞 818-778-1200  🌐 galpinjeep.com                │ │
│  │     ✅ Contact form detected                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ☐   🏪 West Covina Jeep                    📏 23.7 mi │ │
│  │     📍 1600 W Covina Pkwy, West Covina, CA            │ │
│  │     📞 626-967-4100  🌐 westcovinajeep.com            │ │
│  │     ⚠️ Contact form needs verification                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│                        [← Back]     [Create Search & Start] │
└─────────────────────────────────────────────────────────────┘
```

### **Extensible Field Architecture**
- **Core Fields**: Always present (name, make, customer info)
- **Custom Fields**: Add/remove based on business needs
- **Field Types**: Text, email, phone, dropdown, textarea, checkbox
- **Validation**: Real-time with clear error messages
- **Auto-save**: Draft preservation for incomplete forms

---

## 📋 **3. Dealership Management Interface**

### **Main Dealership View**
```
┌─────────────────────────────────────────────────────────────┐
│  🏪 Beverly Hills Jeep Search                    🔄 Refresh  │
├─────────────────────────────────────────────────────────────┤
│  👤 John Smith • john.smith@email.com • (555) 123-4567      │
│  📍 90210, 25 miles • Jeep • Created 2 hours ago            │
│                                                              │
│  📊 Progress: 2/5 contacted • Success Rate: 100%            │
│  ━━━━━━━━━━░░░░░                                              │
│                                                              │
│  🎛️ Automation Controls                                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Status: ⏸️ Paused        [▶️ Resume] [⏹️ Stop] [🔄 Restart]││
│  │ Contact Order: ☑️ Closest First  ☐ Random Order         ││
│  │ Delay Between: ⚡ 30-60 seconds   🐌 2-5 minutes         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  🗂️ Dealership List                      Sort: Distance ▼   │
└─────────────────────────────────────────────────────────────┘
```

### **Individual Dealership Cards**
```
┌─────────────────────────────────────────────────────────────┐
│ ✅ CONTACTED  🏪 Santa Monica Chrysler Jeep    📏 5.0 miles │
├─────────────────────────────────────────────────────────────┤
│ 📍 3219 Santa Monica Blvd, Santa Monica, CA 90404          │
│ 📞 310-829-3200 • 🌐 santamonicachrysler.com               │
│                                                             │
│ ⏰ Contacted: Today 3:47 PM                                 │
│ ✅ Form submitted successfully                               │
│ 📧 Confirmation email received                              │
│                                                             │
│ [📸 Screenshot] [📋 Details] [🔄 Retry] [❌ Remove]         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🔄 CONTACTING  🏪 Galpin Jeep                📏 12.3 miles │
├─────────────────────────────────────────────────────────────┤
│ 📍 15555 Roscoe Blvd, North Hills, CA 91343                │
│ 📞 818-778-1200 • 🌐 galpinjeep.com                        │
│                                                             │
│ ⏰ Started: Now • Step 2/4: Filling contact form            │
│ 🤖 Browser automation in progress...                        │
│ ━━━━━━░░░░                                                   │
│                                                             │
│ [📸 Live View] [⏸️ Pause] [⏹️ Stop]                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ⏳ PENDING    🏪 West Covina Jeep            📏 23.7 miles │
├─────────────────────────────────────────────────────────────┤
│ 📍 1600 W Covina Pkwy, West Covina, CA 91722               │
│ 📞 626-967-4100 • 🌐 westcovinajeep.com                    │
│                                                             │
│ ⚡ Toggle: ☑️ Include in automation                          │
│ ⚠️ Form detection: Needs manual verification                │
│ 🔧 Override: [Manual Contact Info]                          │
│                                                             │
│ [🎯 Contact Now] [⚙️ Configure] [📋 Details]                │
└─────────────────────────────────────────────────────────────┘
```

### **Status Indicators**
- **✅ Contacted**: Green - Form submitted successfully
- **🔄 Contacting**: Blue - Automation in progress
- **⏳ Pending**: Gray - Waiting in queue
- **❌ Failed**: Red - Contact attempt failed
- **⏸️ Paused**: Orange - Manually paused
- **⚠️ Manual**: Yellow - Requires manual intervention

---

## 🤖 **4. Contact Automation System**

### **Automation Controls**
```
┌─────────────────────────────────────────────────────────────┐
│  🤖 Automation Engine                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Current Status: 🔄 Running                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Progress: 2/5 complete                                  ││
│  │ ━━━━━━━━░░░░░░                                           ││
│  │ Est. completion: 8 minutes                              ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ⚙️ Settings                                                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Contact Order: ☑️ Closest first ☐ Random ☐ Alphabetical││
│  │ Delay Between: ⚡ 30-60 sec 🐌 2-5 min ⏱️ Custom        ││
│  │ Retry Failed:  ☑️ Auto-retry once ☐ Manual only        ││
│  │ Screenshots:   ☑️ Save all ☐ Errors only ☐ None       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  🎛️ Controls                                                 │
│  [▶️ Start] [⏸️ Pause] [⏹️ Stop] [🔄 Restart All]            │
│                                                              │
│  📊 Live Stats                                               │
│  ✅ Success: 2 (67%)  ❌ Failed: 1 (33%)  ⏳ Pending: 2     │
└─────────────────────────────────────────────────────────────┘
```

### **Real-time Progress Display**
```
┌─────────────────────────────────────────────────────────────┐
│  📺 Live Automation View                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔄 Currently Processing: Galpin Jeep (12.3 miles)          │
│                                                              │
│  Step Progress:                                              │
│  ✅ 1. Opening website (galpinjeep.com)                     │
│  ✅ 2. Navigating to contact page                           │
│  🔄 3. Detecting contact form (Gravity Forms found)         │
│  ⏳ 4. Filling customer information                         │
│  ⏳ 5. Submitting form                                       │
│  ⏳ 6. Capturing confirmation                                │
│                                                              │
│  ⏱️ Elapsed: 45 seconds                                      │
│  📸 [View Live Browser] [Take Screenshot]                    │
│                                                              │
│  🎯 Next in Queue: West Covina Jeep (23.7 miles)            │
│                                                              │
│  💬 Console Log:                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 15:47:23 - Opening galpinjeep.com                      ││
│  │ 15:47:25 - Page loaded, searching for contact links    ││
│  │ 15:47:27 - Found contact URL: /contact-us              ││
│  │ 15:47:29 - Gravity form detected: #gform_1             ││
│  │ 15:47:31 - Filling input_1 (First Name): John          ││
│  │ 15:47:32 - Filling input_2 (Last Name): Smith          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### **Manual Override System**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Manual Override: West Covina Jeep                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ❌ Automation Failed: Contact form not detected             │
│                                                              │
│  🔧 Override Options:                                        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ☐ Skip this dealership                                 ││
│  │ ☑️ Provide manual contact information                  ││
│  │ ☐ Custom form mapping                                  ││
│  │ ☐ Try alternative contact method                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  📝 Manual Contact Details:                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Contact Method: 📧 Email                           ▼   ││
│  │ Contact Info: sales@westcovinajeep.com                 ││
│  │ Notes: Use email template for initial contact          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  📧 Email Template:                                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Subject: Jeep Lease Inquiry from John Smith            ││
│  │                                                         ││
│  │ Hi,                                                     ││
│  │                                                         ││
│  │ I'm interested in leasing a Jeep. Could you please     ││
│  │ send me information about current deals and             ││
│  │ availability? Thanks!                                   ││
│  │                                                         ││
│  │ Contact: john.smith@email.com • (555) 123-4567         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  [Cancel] [📧 Send Email] [💾 Save for Later] [✅ Mark Done] │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **5. Progress Tracking & Analytics**

### **Summary Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│  📈 Campaign Analytics: Beverly Hills Jeep Search           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🎯 Overall Performance                                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Total Dealerships: 5                                   ││
│  │ ✅ Successfully Contacted: 4 (80%)                     ││
│  │ ❌ Failed Attempts: 1 (20%)                            ││
│  │ ⏱️ Total Time: 12 minutes                               ││
│  │ 🎖️ Success Rate: Above Average (75%)                   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  📊 Contact Method Breakdown                                 │
│  ━━━━━━━━━━━━━━━━ 80% Automated Forms (4)                     │
│  ━━━━ 20% Manual Email (1)                                   │
│                                                              │
│  ⏰ Timeline View                                             │
│  15:45 ✅ Santa Monica Chrysler (Success - 2 min)           │
│  15:47 ✅ Galpin Jeep (Success - 3 min)                     │
│  15:50 ✅ Keyes Jeep (Success - 2 min)                      │
│  15:52 ❌ West Covina (Failed - Form detection)             │
│  15:54 📧 West Covina (Manual email sent)                   │
│                                                              │
│  📥 Expected Responses: 2-4 dealers within 24 hours         │
└─────────────────────────────────────────────────────────────┘
```

### **Detailed Contact Reports**
```
┌─────────────────────────────────────────────────────────────┐
│  📋 Detailed Contact Report                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🏪 Santa Monica Chrysler Jeep                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Status: ✅ Success                                      ││
│  │ Contact Time: Today 3:45 PM                            ││
│  │ Duration: 2 minutes 15 seconds                          ││
│  │ Method: Automated form submission                       ││
│  │ Form Type: Gravity Forms (input_1, input_2, input_3)   ││
│  │ Confirmation: "Thank you! We'll contact you soon."     ││
│  │ Screenshots: [Before] [Form Filled] [Confirmation]     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  🏪 West Covina Jeep                                        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Status: ❌ Failed → 📧 Manual Email Sent               ││
│  │ Failed Time: Today 3:52 PM                             ││
│  │ Failure Reason: Contact form not detected              ││
│  │ Manual Resolution: Email sent to sales@westcovinajeep  ││
│  │ Email Status: Delivered                                ││
│  │ Screenshots: [Page Load] [Search Attempt] [No Form]    ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  [📤 Export Report] [📧 Share Results] [🔄 Retry Failed]    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **6. Technical Architecture**

### **Frontend Technology Stack**
- **Framework**: React 18 with TypeScript
- **Styling**: TailwindCSS for rapid UI development
- **State Management**: Redux Toolkit for complex state
- **Real-time**: WebSocket for live progress updates
- **Maps**: Google Maps API for geographic visualization
- **Forms**: React Hook Form with Zod validation

### **Backend Integration Points**
```typescript
// API Endpoints
interface APIEndpoints {
  // Search Management
  searches: {
    list: "GET /api/v1/searches"
    create: "POST /api/v1/searches"
    get: "GET /api/v1/searches/{id}"
    update: "PUT /api/v1/searches/{id}"
    delete: "DELETE /api/v1/searches/{id}"
  }

  // Dealership Discovery
  dealerships: {
    search: "POST /api/v1/dealerships/search"
    makes: "GET /api/v1/dealerships/makes"
  }

  // Contact Automation
  automation: {
    start: "POST /api/v1/automation/start/{searchId}"
    pause: "POST /api/v1/automation/pause/{searchId}"
    stop: "POST /api/v1/automation/stop/{searchId}"
    status: "GET /api/v1/automation/status/{searchId}"
    override: "POST /api/v1/automation/override/{dealershipId}"
  }

  // Real-time Updates
  websocket: "ws://api/v1/ws/automation/{searchId}"
}
```

### **Component Architecture**
```typescript
interface UIComponents {
  // Layout Components
  Layout: "Main application shell with navigation"
  Header: "Search system branding and user menu"
  Sidebar: "Navigation and quick filters"

  // Search Management
  SearchDashboard: "Main search listing interface"
  SearchCard: "Individual search display component"
  CreateSearchWizard: "Multi-step search creation"

  // Dealership Management
  DealershipList: "Sortable/filterable dealer listing"
  DealershipCard: "Individual dealer with toggle controls"
  DealershipMap: "Geographic visualization component"

  // Automation Interface
  AutomationControls: "Start/stop/pause automation"
  ProgressTracker: "Real-time progress visualization"
  LiveConsole: "Automation log and browser view"
  ManualOverride: "Manual intervention interface"

  // Analytics & Reporting
  AnalyticsDashboard: "Campaign performance metrics"
  ContactReport: "Detailed contact attempt results"
  ExportTools: "Data export and sharing utilities"
}
```

### **State Management Structure**
```typescript
interface AppState {
  user: {
    profile: UserProfile
    preferences: UIPreferences
  }

  searches: {
    list: SearchSummary[]
    current: SearchDetails | null
    filters: SearchFilters
  }

  dealerships: {
    discovered: Dealership[]
    selected: string[]
    contactStatus: ContactStatus[]
  }

  automation: {
    isRunning: boolean
    currentTarget: string | null
    progress: AutomationProgress
    logs: AutomationLog[]
  }

  ui: {
    activeModal: string | null
    notifications: Notification[]
    loading: LoadingState
  }
}
```

---

## 🎨 **7. Design System & UX Guidelines**

### **Color Palette**
- **Primary**: Blue (#3B82F6) - Actions and links
- **Success**: Green (#10B981) - Successful contacts
- **Warning**: Orange (#F59E0B) - Manual interventions
- **Error**: Red (#EF4444) - Failed attempts
- **Processing**: Purple (#8B5CF6) - Active automation
- **Neutral**: Gray scale for backgrounds and text

### **Typography Hierarchy**
- **H1**: Search names and page titles (32px, bold)
- **H2**: Section headers (24px, semibold)
- **H3**: Card titles and dealership names (18px, medium)
- **Body**: Standard content (16px, regular)
- **Small**: Meta information and captions (14px, regular)

### **Responsive Design**
- **Desktop**: Full feature set with multi-column layouts
- **Tablet**: Collapsible sidebar, stacked forms
- **Mobile**: Single-column layout, bottom navigation
- **Touch Optimization**: 44px minimum touch targets

### **Accessibility Standards**
- **WCAG 2.1 AA**: Full compliance for screen readers
- **Keyboard Navigation**: Complete keyboard-only operation
- **High Contrast**: Support for reduced vision users
- **Motion Preferences**: Respect reduced motion settings

---

## 🚀 **8. Implementation Phases**

### **Phase 1: Core Search Management (Week 1)**
- ✅ Search dashboard with CRUD operations
- ✅ Basic dealership discovery integration
- ✅ Simple contact form with validation
- ✅ Basic progress tracking

### **Phase 2: Automation Integration (Week 2)**
- ✅ Real-time automation controls
- ✅ WebSocket integration for live updates
- ✅ Manual override system
- ✅ Screenshot and log viewing

### **Phase 3: Enhanced UX (Week 3)**
- ✅ Advanced filtering and sorting
- ✅ Map integration for geographic display
- ✅ Analytics dashboard
- ✅ Export and sharing features

### **Phase 4: Polish & Optimization (Week 4)**
- ✅ Mobile responsiveness
- ✅ Performance optimization
- ✅ Advanced automation settings
- ✅ User onboarding flow

---

## 🔄 **9. Integration with Existing System**

### **Existing Assets Utilization**
- **`api_wrapper.py`**: Direct integration for dealership search
- **`final_retest_with_contact_urls.py`**: Contact automation engine
- **`dealership_distance_calculator.py`**: Geographic functionality
- **`enhanced_stealth_browser_config.py`**: Browser automation
- **Dealerships CSV**: Core data source with 2,409 records

### **WebSocket Integration Example**
```typescript
// Real-time automation updates
const useAutomationUpdates = (searchId: string) => {
  const [status, setStatus] = useState<AutomationStatus>()

  useEffect(() => {
    const ws = new WebSocket(`ws://api/v1/ws/automation/${searchId}`)

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      setStatus(update)

      // Update UI based on automation progress
      switch (update.type) {
        case 'DEALER_STARTED':
          showNotification(`Starting contact: ${update.dealerName}`)
          break
        case 'DEALER_COMPLETED':
          showNotification(`✅ Contacted: ${update.dealerName}`)
          break
        case 'DEALER_FAILED':
          showNotification(`❌ Failed: ${update.dealerName}`)
          break
      }
    }

    return () => ws.close()
  }, [searchId])

  return status
}
```

### **Form Data Flow**
```typescript
// Search creation to automation pipeline
const createSearchWorkflow = async (formData: SearchForm) => {
  // 1. Create search record
  const search = await api.createSearch({
    name: formData.name,
    make: formData.make,
    customerInfo: formData.customer,
    location: formData.location
  })

  // 2. Discover dealerships
  const dealerships = await api.findDealerships({
    make: formData.make,
    zipcode: formData.location.zipcode,
    radius: formData.location.radius
  })

  // 3. Start automation if enabled
  if (formData.autoStart) {
    await api.startAutomation(search.id, {
      selectedDealerships: dealerships.map(d => d.id),
      settings: formData.automationSettings
    })
  }

  return { search, dealerships }
}
```

---

## 📋 **10. Success Metrics & KPIs**

### **User Experience Metrics**
- **Search Creation Time**: Target <3 minutes from start to automation
- **System Response Time**: <2 seconds for all UI interactions
- **Mobile Usability**: 100% feature parity on mobile devices
- **Error Recovery**: Clear error messages and recovery paths

### **Business Metrics**
- **Contact Success Rate**: Maintain >90% automated contact success
- **Time to Value**: Users see first contact results within 5 minutes
- **System Scalability**: Support 100+ concurrent automation sessions
- **Cost Efficiency**: <$0.10 per successful dealer contact

### **Technical Metrics**
- **API Response Times**: 95th percentile <500ms
- **WebSocket Reliability**: 99.9% message delivery rate
- **Browser Automation**: <5% failure rate due to technical issues
- **Data Accuracy**: 100% consistency between UI and automation results

---

**🎯 SYSTEM READY FOR DEVELOPMENT**

This UI specification provides a complete blueprint for building a production-ready lease deal search system that leverages our existing 90%+ success rate automation with an intuitive, powerful user interface.

**Key Differentiators:**
- **Real-time Progress Tracking**: Users see exactly what's happening
- **Manual Override System**: Handle edge cases gracefully
- **Geographic Intelligence**: Distance-based dealership discovery
- **Extensible Architecture**: Easy to add new features and vehicle makes
- **Production Ready**: Built on proven automation with comprehensive error handling

Ready for frontend development with full backend API integration!