# Comprehensive Logging System for Debugging

## Logging Philosophy

Every operation in the system generates structured logs for:
- **Debugging**: Rapid issue identification and resolution
- **Auditing**: Complete operation trail for compliance
- **Monitoring**: Performance and health metrics
- **Analytics**: Usage patterns and optimization insights

## Log Categories

### 1. Application Logs
- **API Requests/Responses**: All HTTP operations
- **Database Operations**: CRUD operations with timing
- **Business Logic**: Decision points and state changes
- **Error Handling**: Exception details with context

### 2. Automation Logs
- **Browser Operations**: Page loads, element interactions
- **Form Processing**: Field mapping and submission attempts
- **Network Requests**: HTTP calls to dealership websites
- **Performance Metrics**: Timing and resource usage

### 3. System Logs
- **Authentication**: Login/logout events
- **Background Jobs**: Task queue operations
- **Infrastructure**: Server health and resource usage
- **Configuration**: Settings changes and deployments

### 4. User Activity Logs
- **Project Operations**: Create, update, delete actions
- **Manual Overrides**: Status changes with reasoning
- **UI Interactions**: Critical user actions
- **Data Exports**: Report generation and downloads

## Logging Data Models

### Core Log Entry Schema
```python
class LogEntry:
    id: str                           # Unique log ID
    timestamp: datetime               # ISO 8601 with timezone
    level: LogLevel                   # DEBUG, INFO, WARN, ERROR, CRITICAL
    category: LogCategory             # API, AUTOMATION, SYSTEM, USER
    operation: str                    # Specific operation name
    message: str                      # Human-readable description
    
    # Context
    user_id: Optional[str]            # Who performed the action
    session_id: Optional[str]         # Session identifier
    request_id: Optional[str]         # Request tracking ID
    project_id: Optional[str]         # Associated project
    dealership_id: Optional[str]      # Associated dealership
    
    # Technical Details
    component: str                    # Module/service name
    function: str                     # Function/method name
    line_number: Optional[int]        # Code line number
    
    # Performance
    duration_ms: Optional[int]        # Operation duration
    memory_usage_mb: Optional[float]  # Memory consumption
    cpu_usage_percent: Optional[float] # CPU utilization
    
    # Structured Data
    metadata: Dict[str, Any]          # Operation-specific data
    error_details: Optional[ErrorDetails] # Exception information
    stack_trace: Optional[str]        # Full stack trace for errors
    
    # Geographic/Network
    ip_address: Optional[str]         # Client IP
    user_agent: Optional[str]         # Browser/client info
    
    created_at: datetime              # Log creation time
```

### Error Details Schema
```python
class ErrorDetails:
    error_type: str                   # Exception class name
    error_code: Optional[str]         # Application error code
    error_message: str                # Error description
    is_retryable: bool               # Can operation be retried
    retry_count: int                 # Current retry attempt
    max_retries: int                 # Maximum retry limit
    
    # Context
    input_data: Optional[Dict]        # Sanitized input that caused error
    system_state: Optional[Dict]      # Relevant system state
    external_references: List[str]    # Related log entries
```

## Operation-Specific Logging

### 1. Project Operations
```python
# Project Creation
log.info("Project creation started", {
    "operation": "project_create",
    "user_id": "user123",
    "metadata": {
        "project_name": "Downtown Search",
        "search_criteria": {
            "location": "New York, NY",
            "radius_miles": 150,
            "makes": ["jeep", "ram"]
        },
        "input_validation": "passed"
    }
})

# Project Update
log.info("Project updated", {
    "operation": "project_update", 
    "project_id": "proj456",
    "metadata": {
        "changed_fields": ["name", "description"],
        "old_values": {"name": "Old Name"},
        "new_values": {"name": "New Name"}
    }
})
```

### 2. Dealership Discovery
```python
# Geographic Search
log.info("Dealership search initiated", {
    "operation": "dealership_search",
    "project_id": "proj456",
    "metadata": {
        "search_location": {"lat": 40.7128, "lng": -74.0060},
        "radius_miles": 150,
        "makes_filter": ["jeep"],
        "database_query_time_ms": 245
    }
})

# Results Found
log.info("Dealership search completed", {
    "operation": "dealership_search_complete",
    "project_id": "proj456",
    "duration_ms": 1250,
    "metadata": {
        "total_found": 45,
        "filtered_count": 42,
        "avg_distance_miles": 67.3,
        "geographic_distribution": {
            "NY": 15, "NJ": 12, "CT": 8, "PA": 7
        }
    }
})
```

### 3. Browser Automation
```python
# Automation Start
log.info("Browser automation started", {
    "operation": "automation_start",
    "project_id": "proj456",
    "metadata": {
        "dealership_count": 25,
        "browser_config": {
            "headless": true,
            "viewport": "1920x1080",
            "user_agent": "Mozilla/5.0..."
        },
        "rate_limiting": {
            "delay_between_requests": 2.0,
            "max_concurrent": 3
        }
    }
})

# Individual Dealership Attempt
log.info("Dealership contact attempt started", {
    "operation": "contact_attempt_start",
    "project_id": "proj456",
    "dealership_id": "dealer789",
    "metadata": {
        "attempt_number": 1,
        "dealership_name": "City Motors",
        "contact_url": "https://citymotors.com/contact",
        "form_mapping_version": "v1.2.0",
        "browser_session_id": "session_abc123"
    }
})

# Page Load
log.debug("Page loaded", {
    "operation": "page_load",
    "dealership_id": "dealer789",
    "duration_ms": 2300,
    "metadata": {
        "url": "https://citymotors.com/contact",
        "status_code": 200,
        "page_size_kb": 245,
        "resources_loaded": 23,
        "javascript_errors": []
    }
})

# Form Interaction
log.debug("Form field filled", {
    "operation": "form_field_fill",
    "dealership_id": "dealer789",
    "metadata": {
        "field_name": "first_name",
        "field_selector": "input[name='fname']",
        "field_type": "text",
        "value_length": 4,  # Don't log actual values for privacy
        "fill_time_ms": 150
    }
})

# Form Submission
log.info("Form submission attempted", {
    "operation": "form_submit",
    "dealership_id": "dealer789",
    "metadata": {
        "form_selector": "#contact-form",
        "submit_method": "click",
        "submit_selector": "button[type='submit']",
        "form_fields_filled": 8,
        "checkboxes_checked": 2
    }
})

# Success/Failure
log.info("Contact attempt completed", {
    "operation": "contact_attempt_complete",
    "project_id": "proj456", 
    "dealership_id": "dealer789",
    "duration_ms": 15400,
    "metadata": {
        "result": "success",
        "confirmation_detected": true,
        "confirmation_text": "Thank you for your inquiry",
        "screenshot_paths": [
            "/screenshots/before_dealer789_20240101.png",
            "/screenshots/after_dealer789_20240101.png"
        ],
        "performance": {
            "page_load_time_ms": 2300,
            "form_fill_time_ms": 5400,
            "submission_time_ms": 1200,
            "total_wait_time_ms": 6500
        }
    }
})
```

### 4. Error Logging
```python
# Automation Errors
log.error("Form submission failed", {
    "operation": "form_submit_error",
    "project_id": "proj456",
    "dealership_id": "dealer789",
    "error_details": {
        "error_type": "CaptchaDetected",
        "error_code": "CAPTCHA_001",
        "error_message": "reCAPTCHA challenge detected",
        "is_retryable": false,
        "retry_count": 0,
        "max_retries": 3
    },
    "metadata": {
        "page_url": "https://dealership.com/contact",
        "captcha_type": "recaptcha_v2",
        "captcha_selector": ".g-recaptcha",
        "screenshot_path": "/screenshots/captcha_dealer789.png"
    },
    "stack_trace": "Traceback (most recent call last)..."
})

# System Errors
log.critical("Database connection failed", {
    "operation": "database_connection_error",
    "error_details": {
        "error_type": "ConnectionError",
        "error_message": "Could not connect to PostgreSQL",
        "is_retryable": true,
        "retry_count": 2,
        "max_retries": 5
    },
    "metadata": {
        "database_host": "localhost",
        "database_port": 5432,
        "connection_timeout": 30,
        "ssl_enabled": true
    }
})
```

### 5. User Activity Logging
```python
# Manual Status Override
log.info("Manual status override applied", {
    "operation": "manual_status_override",
    "user_id": "user123",
    "project_id": "proj456",
    "dealership_id": "dealer789",
    "metadata": {
        "old_status": "failed",
        "new_status": "manual_override",
        "reason": "Called dealership directly",
        "notes": "Spoke with sales manager, appointment scheduled",
        "contact_method": "phone",
        "override_timestamp": "2024-01-01T10:30:00Z"
    }
})

# Data Export
log.info("Project data exported", {
    "operation": "project_export",
    "user_id": "user123",
    "project_id": "proj456",
    "metadata": {
        "export_format": "excel",
        "include_attempts": true,
        "status_filter": ["success", "manual_override"],
        "total_records": 42,
        "file_size_mb": 2.3,
        "export_duration_ms": 1800
    }
})
```

## Log Configuration

### Log Levels by Environment
```yaml
# Development
logging:
  level: DEBUG
  console: true
  file: true
  structured: true
  
# Staging  
logging:
  level: INFO
  console: true
  file: true
  structured: true
  
# Production
logging:
  level: INFO
  console: false
  file: true
  structured: true
  external: true  # Send to ELK/Datadog
```

### Log Outputs
```yaml
outputs:
  console:
    enabled: true
    format: "human_readable"  # For development
    
  file:
    enabled: true
    format: "json"
    rotation: "daily"
    retention_days: 90
    max_size_mb: 100
    
  elasticsearch:
    enabled: true  # Production only
    index_pattern: "dealership-automation-{date}"
    
  datadog:
    enabled: false
    api_key: "${DATADOG_API_KEY}"
```

## Log Storage Schema

### Database Table
```sql
CREATE TABLE application_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    level VARCHAR(10) NOT NULL,
    category VARCHAR(20) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    
    -- Context
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100),
    request_id VARCHAR(100),
    project_id UUID REFERENCES projects(id),
    dealership_id UUID REFERENCES dealerships(id),
    
    -- Technical
    component VARCHAR(100) NOT NULL,
    function_name VARCHAR(100),
    line_number INTEGER,
    
    -- Performance
    duration_ms INTEGER,
    memory_usage_mb DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    
    -- Data
    metadata JSONB,
    error_details JSONB,
    stack_trace TEXT,
    
    -- Network
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_logs_timestamp ON application_logs(timestamp);
CREATE INDEX idx_logs_level ON application_logs(level);
CREATE INDEX idx_logs_operation ON application_logs(operation);
CREATE INDEX idx_logs_project_id ON application_logs(project_id);
CREATE INDEX idx_logs_user_id ON application_logs(user_id);
CREATE INDEX idx_logs_error_type ON application_logs USING GIN ((error_details->>'error_type'));
```

## Log Query & Analysis

### Common Debug Queries
```sql
-- Find all errors for a specific project
SELECT timestamp, operation, message, error_details
FROM application_logs 
WHERE project_id = 'proj456' 
  AND level = 'ERROR'
ORDER BY timestamp DESC;

-- Automation performance analysis
SELECT 
    dealership_id,
    AVG(duration_ms) as avg_duration,
    COUNT(*) as attempt_count,
    COUNT(CASE WHEN operation = 'contact_attempt_complete' 
               AND metadata->>'result' = 'success' THEN 1 END) as success_count
FROM application_logs
WHERE operation IN ('contact_attempt_complete')
  AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY dealership_id;

-- Error pattern analysis
SELECT 
    error_details->>'error_type' as error_type,
    COUNT(*) as occurrences,
    COUNT(DISTINCT dealership_id) as affected_dealerships
FROM application_logs
WHERE level = 'ERROR' 
  AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY error_details->>'error_type'
ORDER BY occurrences DESC;
```

## Debug Tools & Interfaces

### Log Viewer API
```http
GET /api/v1/logs
Query Parameters:
  - level: string (DEBUG, INFO, WARN, ERROR, CRITICAL)
  - category: string (API, AUTOMATION, SYSTEM, USER)
  - operation: string
  - project_id: uuid
  - user_id: uuid
  - start_time: datetime
  - end_time: datetime
  - search: string (full-text search)
  - limit: integer (default: 100)
  - offset: integer (default: 0)
```

### Real-time Log Streaming
```javascript
// WebSocket connection for live logs
const logSocket = io('/logs');

logSocket.on('log_entry', (logData) => {
  // Real-time log display in UI
  console.log(`[${logData.level}] ${logData.message}`);
});

// Filter real-time logs
logSocket.emit('subscribe', {
  filters: {
    level: ['ERROR', 'WARN'],
    project_id: 'proj456'
  }
});
```

### Log Export & Analysis
- **Structured Export**: JSON/CSV for analysis tools
- **Integration**: ELK Stack, Splunk, Datadog
- **Alerting**: Automated alerts on error patterns
- **Dashboards**: Grafana dashboards for monitoring

## Privacy & Security

### Data Sanitization
- **PII Removal**: Never log personal information
- **Value Masking**: Log field types, not actual values
- **URL Sanitization**: Remove query parameters with sensitive data
- **Error Context**: Include enough detail for debugging without exposing secrets

### Log Retention
- **Development**: 30 days local storage
- **Production**: 90 days database + 1 year archive
- **Compliance**: GDPR-compliant data handling
- **Encryption**: Logs encrypted at rest and in transit