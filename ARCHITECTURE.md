# Dealership Contact Automation - System Architecture

## Overview
A robust, extensible system for automated contact form submission across automotive dealership websites with geographic filtering and intelligent form mapping.

## High-Level Architecture

### Core Components

1. **Data Layer**
   - Dealership database (CSV → SQLite/PostgreSQL)
   - Form mapping configurations
   - User input validation schemas

2. **Business Logic Layer**
   - Geographic filtering (distance calculations)
   - Dealership selection engine
   - Form automation orchestrator
   - Retry and error handling mechanisms

3. **Web Automation Layer**
   - Browser automation (Playwright/Selenium)
   - Form discovery and mapping
   - Dynamic element handling
   - Anti-bot detection mitigation

4. **Configuration Layer**
   - Dealership-specific form mappings
   - Field mapping templates
   - Automation rules and constraints

5. **API/Interface Layer**
   - CLI interface for batch operations
   - Web UI for interactive use
   - REST API for integration

## Data Models

### Core Entities
```python
class Project:
    - id, name, description
    - created_at, updated_at, created_by
    - search_criteria (location, radius, makes)
    - user_info (name, email, phone, etc.)
    - status (draft, active, completed, archived)
    - total_dealerships, contacted_count, success_count, failed_count

class Dealership:
    - id, dealer_code, name, address, coordinates
    - website, phone, email
    - makes_supported, services_available
    - form_mapping_id, last_contacted

class ProjectDealership:
    - project_id, dealership_id
    - distance_from_search_location
    - contact_status (pending, success, failed, manual_override)
    - contact_attempts, last_attempt_at
    - manual_status_set_by, manual_status_set_at
    - notes

class ContactRequest:
    - id, project_id
    - user_info (name, email, phone, address)
    - vehicle_preferences (makes, models, budget)
    - custom_message, template_used

class FormMapping:
    - dealership_id, contact_page_url
    - field_mappings, dropdown_options
    - required_checkboxes, submit_selectors
    - validation_rules, last_verified_at

class ContactAttempt:
    - id, project_dealership_id, request_id
    - timestamp, status, error_details
    - screenshots, browser_logs
    - retry_count, completion_time
    - automation_strategy_used
```

## File Structure

```
dealership-contact-automation/
├── src/
│   ├── core/
│   │   ├── models/          # Data models and schemas
│   │   ├── database/        # Database operations
│   │   ├── geolocation/     # Distance calculations
│   │   └── validation/      # Input validation
│   ├── automation/
│   │   ├── browser/         # Browser automation engine
│   │   ├── forms/           # Form discovery and mapping
│   │   ├── selectors/       # Element selector strategies
│   │   └── handlers/        # Event and error handlers
│   ├── mapping/
│   │   ├── discovery/       # Auto-discover contact forms
│   │   ├── templates/       # Form mapping templates
│   │   └── validators/      # Form validation rules
│   ├── services/
│   │   ├── projects/        # Project management logic
│   │   ├── dealerships/     # Dealership search and filtering
│   │   ├── contact/         # Contact orchestration
│   │   └── tracking/        # Status tracking and reporting
│   ├── interfaces/
│   │   ├── cli/             # Command-line interface
│   │   ├── web/             # Web UI (React/Vue frontend)
│   │   │   ├── components/  # Reusable UI components
│   │   │   ├── pages/       # Main application pages
│   │   │   ├── hooks/       # Custom React hooks
│   │   │   └── utils/       # Frontend utilities
│   │   └── api/             # REST API endpoints
│   │       ├── projects/    # Project CRUD endpoints
│   │       ├── dealerships/ # Dealership search endpoints
│   │       ├── contact/     # Contact automation endpoints
│   │       └── tracking/    # Status and reporting endpoints
│   └── utils/
│       ├── logging/         # Structured logging
│       ├── config/          # Configuration management
│       └── helpers/         # Utility functions
├── data/
│   ├── dealerships/         # CSV files by make
│   ├── mappings/            # Form mapping configurations
│   ├── schemas/             # JSON schemas
│   └── exports/             # Results and reports
├── config/
│   ├── automation.yml       # Browser and timing settings
│   ├── database.yml         # Database configuration
│   └── logging.yml          # Logging configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── docs/
    ├── api/
    ├── mapping-guide.md
    └── troubleshooting.md
```

## Form Mapping Strategy

### Discovery Pipeline
- Automated page crawling to find contact forms
- Common pattern recognition (contact, sales, inquiry pages)
- Form element classification and field detection

### Configuration System
```yaml
# Example: data/mappings/dealership_123.yml
dealership_id: "123"
contact_url: "https://dealer.com/contact"
form_selector: "#contact-form"
fields:
  first_name: 
    selector: "input[name='fname']"
    type: "text"
    required: true
  vehicle_interest:
    selector: "select[name='vehicle']"
    type: "dropdown"
    options_mapping:
      "jeep": "Jeep"
      "ram": "Ram Trucks"
checkboxes:
  privacy_consent:
    selector: "input[name='consent']"
    required: true
submit:
  selector: "button[type='submit']"
  wait_for: ".success-message"
```

### Automation Engine Features
- Multi-step form handling
- Dynamic element waiting and retry logic
- Screenshot capture for verification
- Rate limiting and respectful automation
- Captcha detection (manual intervention trigger)

## Extensibility & Robustness

### Plugin Architecture
- Custom form handlers for specific dealer networks
- Extensible field mapping strategies
- Custom validation rules
- Integration adapters (CRM, lead management)

### Configuration Management
- Environment-specific settings (dev/staging/prod)
- Feature flags for experimental functionality
- A/B testing for automation strategies
- Dynamic rate limiting based on dealer response

### Robustness Features
- **Error Recovery**: Automatic retry with exponential backoff
- **Monitoring**: Success/failure tracking with detailed metrics
- **Failsafes**: Manual intervention triggers for complex forms
- **Data Integrity**: Transaction logging and rollback capabilities
- **Compliance**: Respect robots.txt and rate limiting

### Scalability Considerations
- **Queue System**: Background job processing for large batches
- **Distributed**: Multiple browser instances for parallel processing
- **Caching**: Form mapping cache to reduce discovery overhead
- **Database**: Optimized queries for geographic filtering

## Technology Stack Recommendations

### Core Technologies
- **Backend**: Python 3.9+ with FastAPI/Flask
- **Database**: PostgreSQL with PostGIS for geographic queries
- **Browser Automation**: Playwright (faster, more reliable than Selenium)
- **Task Queue**: Celery with Redis
- **Configuration**: YAML + Pydantic for validation

### Optional Technologies
- **Frontend**: React/Vue.js for web interface
- **Containerization**: Docker for deployment
- **Monitoring**: Grafana + Prometheus
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)