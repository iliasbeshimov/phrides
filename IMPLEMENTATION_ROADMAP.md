# Implementation Roadmap: Lease Deal Search System

**Based on completed UI_SPECIFICATION.md - Ready for development**

## 🎯 **Development Phases**

### **Phase 1: Backend API Foundation (Week 1)**
**Priority: High** - Foundation for all frontend work

#### **Database Schema Design**
```sql
-- Core search tracking tables
CREATE TABLE searches (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    make VARCHAR(50) NOT NULL,
    customer_first_name VARCHAR(100) NOT NULL,
    customer_last_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_zipcode VARCHAR(5) NOT NULL,
    search_zipcode VARCHAR(5) NOT NULL,
    radius_miles INTEGER NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Discovered dealerships for each search
CREATE TABLE search_dealerships (
    id INTEGER PRIMARY KEY,
    search_id INTEGER REFERENCES searches(id),
    dealer_name VARCHAR(255) NOT NULL,
    dealer_website VARCHAR(255),
    dealer_phone VARCHAR(20),
    dealer_address TEXT,
    distance_miles DECIMAL(5,1),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    selected BOOLEAN DEFAULT true,
    contact_status VARCHAR(20) DEFAULT 'pending',
    contact_attempted_at TIMESTAMP,
    contact_completed_at TIMESTAMP,
    contact_success BOOLEAN DEFAULT false,
    contact_error_message TEXT,
    contact_confirmation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detailed automation logs and screenshots
CREATE TABLE contact_attempts (
    id INTEGER PRIMARY KEY,
    search_dealership_id INTEGER REFERENCES search_dealerships(id),
    attempt_number INTEGER DEFAULT 1,
    automation_status VARCHAR(50),
    step_description TEXT,
    screenshot_path VARCHAR(500),
    browser_logs TEXT,
    error_details TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    success BOOLEAN DEFAULT false
);

-- Manual overrides and custom contact methods
CREATE TABLE manual_overrides (
    id INTEGER PRIMARY KEY,
    search_dealership_id INTEGER REFERENCES search_dealerships(id),
    override_type VARCHAR(50), -- 'email', 'phone', 'skip', 'custom_form'
    override_details TEXT,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **API Endpoints Development**
```python
# Search Management APIs
POST   /api/v1/searches              # Create new search
GET    /api/v1/searches              # List all searches
GET    /api/v1/searches/{id}         # Get search details
PUT    /api/v1/searches/{id}         # Update search
DELETE /api/v1/searches/{id}         # Delete search

# Dealership Discovery APIs
POST   /api/v1/searches/{id}/discover # Discover dealerships for search
GET    /api/v1/searches/{id}/dealerships # Get dealerships for search
PUT    /api/v1/searches/{id}/dealerships/{dealer_id}/toggle # Toggle selection

# Contact Automation APIs
POST   /api/v1/searches/{id}/start   # Start automation
POST   /api/v1/searches/{id}/pause   # Pause automation
POST   /api/v1/searches/{id}/stop    # Stop automation
GET    /api/v1/searches/{id}/status  # Get automation status

# Manual Override APIs
POST   /api/v1/dealerships/{id}/override # Create manual override
PUT    /api/v1/dealerships/{id}/override/{override_id} # Update override

# Analytics APIs
GET    /api/v1/searches/{id}/analytics # Get search analytics
GET    /api/v1/searches/{id}/export    # Export search results

# WebSocket for Real-time Updates
WS     /ws/searches/{id}/automation    # Live automation updates
```

#### **Integration with Existing System**
```python
# Extend existing modules
from dealership_distance_calculator import DealershipDistanceCalculator
from final_retest_with_contact_urls import ContactFormAutomator
from config import Config

class SearchManager:
    def __init__(self):
        self.distance_calc = DealershipDistanceCalculator()
        self.contact_automator = ContactFormAutomator()

    def create_search(self, search_data):
        # 1. Validate input data
        # 2. Store search in database
        # 3. Discover dealerships using existing distance calculator
        # 4. Return search with discovered dealerships

    def start_automation(self, search_id):
        # 1. Get selected dealerships
        # 2. Launch existing contact automation
        # 3. Track progress in database
        # 4. Send WebSocket updates
```

### **Phase 2: Frontend Foundation (Week 2)**
**Priority: High** - Core user interface

#### **React Application Setup**
```bash
# Technology stack
npx create-react-app lease-tracker --template typescript
cd lease-tracker

# Core dependencies
npm install @reduxjs/toolkit react-redux
npm install @tailwindcss/forms @tailwindcss/typography
npm install axios socket.io-client
npm install react-hook-form @hookform/resolvers zod
npm install lucide-react # For icons
npm install react-router-dom

# Development tools
npm install --save-dev @types/node @types/react @types/react-dom
```

#### **Core Components Development**
```typescript
// Component hierarchy
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Layout.tsx
│   ├── search/
│   │   ├── SearchDashboard.tsx
│   │   ├── SearchCard.tsx
│   │   ├── CreateSearchWizard.tsx
│   │   └── SearchFilters.tsx
│   ├── dealerships/
│   │   ├── DealershipList.tsx
│   │   ├── DealershipCard.tsx
│   │   └── DealershipMap.tsx
│   ├── automation/
│   │   ├── AutomationControls.tsx
│   │   ├── ProgressTracker.tsx
│   │   ├── LiveConsole.tsx
│   │   └── ManualOverride.tsx
│   └── analytics/
│       ├── AnalyticsDashboard.tsx
│       ├── ContactReport.tsx
│       └── ExportTools.tsx
├── hooks/
│   ├── useSearches.ts
│   ├── useAutomation.ts
│   └── useWebSocket.ts
├── store/
│   ├── searchSlice.ts
│   ├── dealershipSlice.ts
│   ├── automationSlice.ts
│   └── store.ts
└── types/
    ├── search.ts
    ├── dealership.ts
    └── automation.ts
```

#### **State Management Structure**
```typescript
interface AppState {
  searches: {
    list: SearchSummary[]
    current: SearchDetails | null
    filters: SearchFilters
    loading: boolean
    error: string | null
  }

  dealerships: {
    discovered: Dealership[]
    selected: string[]
    contactStatus: Record<string, ContactStatus>
  }

  automation: {
    isRunning: boolean
    currentTarget: string | null
    progress: AutomationProgress
    logs: AutomationLog[]
    settings: AutomationSettings
  }

  ui: {
    activeModal: string | null
    notifications: Notification[]
    loading: LoadingState
  }
}
```

### **Phase 3: Core Features (Week 3)**
**Priority: High** - Essential functionality

#### **Search Management Implementation**
- **Search Dashboard** with filtering and sorting
- **Create Search Wizard** with 3-step process
- **Search Detail View** with dealership list
- **Search Status Tracking** (pending, active, completed)

#### **Dealership Discovery Integration**
- **Geographic Search** using existing distance calculator
- **Dealership Cards** with toggle switches
- **Distance Sorting** and filtering
- **Map Integration** (optional for MVP)

#### **Basic Automation Control**
- **Start/Stop/Pause** automation
- **Progress Tracking** with status updates
- **Error Handling** and retry mechanisms
- **Manual Override** interface

### **Phase 4: Advanced Features (Week 4)**
**Priority: Medium** - Enhanced user experience

#### **Real-time Updates**
- **WebSocket Integration** for live progress
- **Live Console** showing automation steps
- **Real-time Status Changes** across UI
- **Notification System** for important events

#### **Analytics and Reporting**
- **Success Rate Tracking** per search
- **Contact Method Analysis** (automated vs manual)
- **Performance Metrics** (time per contact, failure rates)
- **Export Functionality** (CSV, PDF reports)

#### **Advanced Automation Features**
- **Batch Operations** (start multiple searches)
- **Scheduling** (start automation at specific times)
- **Custom Form Mappings** for difficult sites
- **Screenshot Gallery** for verification

### **Phase 5: Polish and Optimization (Week 5)**
**Priority: Medium** - Production readiness

#### **Mobile Responsiveness**
- **Responsive Design** for all screen sizes
- **Touch Optimization** for mobile devices
- **Progressive Web App** features
- **Offline Capability** (basic functionality)

#### **Performance Optimization**
- **Code Splitting** for faster loading
- **Image Optimization** for screenshots
- **Caching Strategy** for API responses
- **Bundle Size Optimization**

#### **User Experience Enhancements**
- **Onboarding Flow** for new users
- **Keyboard Shortcuts** for power users
- **Dark Mode** support
- **Accessibility Improvements** (WCAG 2.1)

---

## 🛠 **Technical Decisions**

### **Backend Framework**
- **FastAPI** for REST API (high performance, automatic docs)
- **SQLAlchemy** for database ORM
- **Pydantic** for data validation
- **WebSockets** for real-time updates

### **Frontend Framework**
- **React 18** with TypeScript for type safety
- **Redux Toolkit** for state management
- **TailwindCSS** for rapid UI development
- **React Hook Form** for form handling

### **Database**
- **SQLite** for development and small deployments
- **PostgreSQL** for production (better concurrency)
- **Alembic** for database migrations

### **Deployment Strategy**
- **Docker** containers for easy deployment
- **Docker Compose** for development environment
- **Environment Variables** for configuration
- **GitHub Actions** for CI/CD

---

## 📊 **Success Metrics**

### **Development Milestones**
- [ ] **Week 1**: Backend API complete with database schema
- [ ] **Week 2**: Frontend foundation with basic search creation
- [ ] **Week 3**: Full search and automation workflow working
- [ ] **Week 4**: Real-time updates and analytics implemented
- [ ] **Week 5**: Production-ready with mobile support

### **Performance Targets**
- **API Response Time**: <500ms for 95th percentile
- **UI Responsiveness**: <100ms for state updates
- **Search Creation**: <3 minutes from start to automation
- **Contact Success Rate**: Maintain existing 90%+ automation success

### **User Experience Goals**
- **Intuitive Interface**: New users can create search in <5 minutes
- **Real-time Feedback**: Users see progress within seconds
- **Mobile Friendly**: 100% feature parity on mobile devices
- **Error Recovery**: Clear error messages and recovery paths

---

## 🚀 **Getting Started**

### **Development Environment Setup**
```bash
# 1. Backend setup
cd backend/
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload

# 2. Frontend setup
cd frontend/
npm install
npm start

# 3. Database setup
alembic upgrade head

# 4. Environment variables
cp .env.example .env
# Fill in your API keys
```

### **First Implementation Tasks**
1. **Set up database schema** and run migrations
2. **Create basic search API endpoints**
3. **Build search creation form** in React
4. **Integrate dealership discovery** with existing system
5. **Test end-to-end workflow** with one search

---

**🎯 READY FOR DEVELOPMENT**

This roadmap provides a clear path from our current foundation (90%+ contact automation + geographic discovery) to a full-featured search and contact tracking system with an intuitive user interface.

**Next Action**: Choose Phase 1 (Backend) or Phase 2 (Frontend) to start implementation!