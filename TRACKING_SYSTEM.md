# Contact Attempt Tracking System

## Status Management

### Contact Status Definitions

```python
class ContactStatus(Enum):
    PENDING = "pending"                    # Not yet contacted
    IN_PROGRESS = "in_progress"           # Currently being processed
    SUCCESS = "success"                   # Successfully contacted via automation
    FAILED = "failed"                     # Automation failed
    MANUAL_OVERRIDE = "manual_override"   # Manually marked as contacted
    SKIPPED = "skipped"                   # Intentionally skipped
    BLOCKED = "blocked"                   # Site blocking automation
```

### Status Transitions

```
PENDING → IN_PROGRESS → SUCCESS ✓
                      → FAILED → MANUAL_OVERRIDE ✓
                              → retry → IN_PROGRESS
                              
PENDING → MANUAL_OVERRIDE ✓
PENDING → SKIPPED ✓

Any Status → MANUAL_OVERRIDE ✓ (admin override)
```

## Detailed Tracking Fields

### ProjectDealership Table
```sql
CREATE TABLE project_dealerships (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    dealership_id INTEGER REFERENCES dealerships(id),
    
    -- Geographic Data
    distance_miles DECIMAL(5,2),
    search_location_lat DECIMAL(10,8),
    search_location_lng DECIMAL(11,8),
    
    -- Contact Status
    contact_status VARCHAR(20) DEFAULT 'pending',
    contact_attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    
    -- Manual Override Tracking
    manual_status_set_by VARCHAR(255),
    manual_status_set_at TIMESTAMP,
    manual_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(project_id, dealership_id)
);
```

### ContactAttempt Table
```sql
CREATE TABLE contact_attempts (
    id SERIAL PRIMARY KEY,
    project_dealership_id INTEGER REFERENCES project_dealerships(id),
    contact_request_id INTEGER REFERENCES contact_requests(id),
    
    -- Attempt Details
    attempt_number INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Result
    status VARCHAR(20), -- success, failed, timeout, blocked
    error_type VARCHAR(50), -- form_not_found, captcha, timeout, etc.
    error_message TEXT,
    error_stack_trace TEXT,
    
    -- Evidence
    screenshot_before_path VARCHAR(500),
    screenshot_after_path VARCHAR(500),
    screenshot_error_path VARCHAR(500),
    page_source_path VARCHAR(500),
    browser_logs JSON,
    
    -- Automation Details
    automation_strategy VARCHAR(100),
    form_mapping_version VARCHAR(50),
    browser_type VARCHAR(20),
    user_agent TEXT,
    
    -- Performance Metrics
    page_load_time_ms INTEGER,
    form_fill_time_ms INTEGER,
    submission_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Real-time Tracking Features

### Live Progress Updates
```typescript
interface AutomationProgress {
  projectId: string;
  totalDealerships: number;
  processed: number;
  successful: number;
  failed: number;
  currentDealership?: {
    name: string;
    status: 'starting' | 'loading_page' | 'filling_form' | 'submitting';
  };
  estimatedTimeRemaining: number; // seconds
  startedAt: string;
  averageTimePerAttempt: number;
}

// WebSocket events
export enum TrackingEvents {
  AUTOMATION_STARTED = 'automation_started',
  DEALERSHIP_STARTED = 'dealership_started',
  DEALERSHIP_COMPLETED = 'dealership_completed',
  AUTOMATION_COMPLETED = 'automation_completed',
  AUTOMATION_PAUSED = 'automation_paused',
  ERROR_OCCURRED = 'error_occurred',
}
```

### Status Update API
```typescript
// Real-time status updates via WebSocket
interface StatusUpdate {
  projectDealershipId: string;
  oldStatus: ContactStatus;
  newStatus: ContactStatus;
  timestamp: string;
  metadata?: {
    errorType?: string;
    screenshotPath?: string;
    duration?: number;
  };
}
```

## Error Categorization

### Failure Types
```python
class FailureType(Enum):
    # Form Detection Issues
    FORM_NOT_FOUND = "form_not_found"
    FORM_CHANGED = "form_changed"
    MULTIPLE_FORMS = "multiple_forms"
    
    # Element Issues
    FIELD_NOT_FOUND = "field_not_found"
    FIELD_DISABLED = "field_disabled"
    DROPDOWN_OPTION_MISSING = "dropdown_option_missing"
    
    # Interaction Issues
    CAPTCHA_DETECTED = "captcha_detected"
    JAVASCRIPT_ERROR = "javascript_error"
    PAGE_TIMEOUT = "page_timeout"
    SUBMISSION_FAILED = "submission_failed"
    
    # Site Protection
    BOT_DETECTION = "bot_detection"
    RATE_LIMITED = "rate_limited"
    IP_BLOCKED = "ip_blocked"
    
    # Technical Issues
    NETWORK_ERROR = "network_error"
    BROWSER_CRASH = "browser_crash"
    UNEXPECTED_REDIRECT = "unexpected_redirect"
```

### Retry Logic
```python
class RetryConfig:
    max_attempts: int = 3
    base_delay: int = 60  # seconds
    exponential_backoff: bool = True
    
    # Specific retry strategies by error type
    retry_strategies = {
        FailureType.PAGE_TIMEOUT: {"max_attempts": 2, "delay": 30},
        FailureType.NETWORK_ERROR: {"max_attempts": 5, "delay": 10},
        FailureType.CAPTCHA_DETECTED: {"max_attempts": 0},  # No retry
        FailureType.BOT_DETECTION: {"max_attempts": 0},     # No retry
        FailureType.FORM_NOT_FOUND: {"max_attempts": 1, "delay": 300},
    }
```

## Analytics & Reporting

### Success Rate Metrics
```sql
-- Project success rate
SELECT 
    p.name,
    COUNT(*) as total_dealerships,
    COUNT(CASE WHEN pd.contact_status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN pd.contact_status = 'failed' THEN 1 END) as failed,
    COUNT(CASE WHEN pd.contact_status = 'manual_override' THEN 1 END) as manual,
    ROUND(
        COUNT(CASE WHEN pd.contact_status IN ('success', 'manual_override') THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as success_rate_percent
FROM projects p
JOIN project_dealerships pd ON p.id = pd.project_id
GROUP BY p.id, p.name;
```

### Error Analysis
```sql
-- Most common failure types
SELECT 
    ca.error_type,
    COUNT(*) as occurrences,
    ROUND(AVG(ca.duration_seconds), 2) as avg_duration,
    COUNT(DISTINCT ca.project_dealership_id) as unique_dealerships
FROM contact_attempts ca
WHERE ca.status = 'failed'
GROUP BY ca.error_type
ORDER BY occurrences DESC;
```

### Performance Metrics
```sql
-- Automation performance by dealership
SELECT 
    d.name as dealership_name,
    d.website,
    COUNT(ca.id) as total_attempts,
    COUNT(CASE WHEN ca.status = 'success' THEN 1 END) as successful_attempts,
    ROUND(AVG(ca.duration_seconds), 2) as avg_duration,
    ROUND(AVG(ca.page_load_time_ms), 0) as avg_page_load_ms
FROM dealerships d
JOIN project_dealerships pd ON d.id = pd.dealership_id
JOIN contact_attempts ca ON pd.id = ca.project_dealership_id
GROUP BY d.id, d.name, d.website
HAVING COUNT(ca.id) >= 3  -- Only dealerships with multiple attempts
ORDER BY successful_attempts DESC, avg_duration ASC;
```

## Manual Override System

### Override Interface
```typescript
interface ManualOverride {
  projectDealershipId: string;
  newStatus: 'manual_override' | 'skipped';
  notes: string;
  contactMethod?: 'phone' | 'email' | 'in_person' | 'other';
  contactedBy: string;
  contactedAt: string;
  followUpRequired?: boolean;
  followUpDate?: string;
}
```

### Audit Trail
```sql
CREATE TABLE status_changes (
    id SERIAL PRIMARY KEY,
    project_dealership_id INTEGER REFERENCES project_dealerships(id),
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by VARCHAR(255),
    change_reason VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Notification System

### Alert Types
```python
class AlertType(Enum):
    HIGH_FAILURE_RATE = "high_failure_rate"      # >50% failures in batch
    AUTOMATION_STUCK = "automation_stuck"        # No progress in 10 minutes  
    CAPTCHA_BLOCKING = "captcha_blocking"        # Multiple captcha detections
    SITE_CHANGES = "site_changes"                # Form mapping failures
    COMPLETION = "completion"                    # Automation finished
```

### Notification Channels
- **In-App**: Real-time UI notifications
- **Email**: Summary reports and alerts
- **Slack/Teams**: Integration for team notifications
- **Webhook**: Custom integrations

## Integrated Logging System

### Operation Logging
Every tracking operation generates detailed logs:

```python
# Status change logging
log.info("Contact status updated", {
    "operation": "status_change",
    "project_id": "proj123",
    "dealership_id": "dealer456", 
    "old_status": "pending",
    "new_status": "success",
    "duration_ms": 15400,
    "metadata": {
        "attempt_number": 1,
        "automation_strategy": "standard_form",
        "confirmation_detected": true,
        "screenshot_captured": true
    }
})

# Manual override logging
log.info("Manual status override applied", {
    "operation": "manual_override",
    "project_id": "proj123",
    "dealership_id": "dealer456",
    "user_id": "user789",
    "metadata": {
        "old_status": "failed", 
        "new_status": "manual_override",
        "reason": "Called directly",
        "contact_method": "phone",
        "notes": "Spoke with sales manager"
    }
})

# Performance metrics logging
log.info("Automation batch completed", {
    "operation": "batch_complete",
    "project_id": "proj123",
    "duration_ms": 1800000,
    "metadata": {
        "total_processed": 25,
        "success_count": 20,
        "failure_count": 5,
        "avg_time_per_attempt": 72000,
        "error_breakdown": {
            "captcha_detected": 3,
            "form_not_found": 2
        }
    }
})
```

### Real-time Tracking Logs
```python
# WebSocket event logging
log.debug("Status update broadcasted", {
    "operation": "websocket_broadcast",
    "project_id": "proj123",
    "event_type": "status_update",
    "metadata": {
        "connected_clients": 2,
        "message_size_bytes": 245,
        "broadcast_time_ms": 15
    }
})

# Progress update logging
log.debug("Progress update sent", {
    "operation": "progress_update",
    "project_id": "proj123",
    "metadata": {
        "current_progress": 0.65,
        "estimated_completion": "2024-01-01T11:30:00Z",
        "current_dealership": "City Motors",
        "queue_size": 8
    }
})
```

### Error Tracking Integration
```python
# Failure analysis logging
log.error("Contact attempt failed with detailed context", {
    "operation": "contact_attempt_failure",
    "project_id": "proj123", 
    "dealership_id": "dealer456",
    "error_details": {
        "error_type": "CaptchaDetected",
        "error_code": "CAPTCHA_001",
        "is_retryable": false
    },
    "metadata": {
        "attempt_number": 1,
        "page_url": "https://dealer.com/contact",
        "time_to_failure_ms": 8500,
        "browser_logs": [...],
        "screenshot_path": "/screenshots/error_dealer456.png",
        "form_mapping_version": "v1.2.0"
    }
})
```

## Data Export & Reporting

### Export Formats
- **CSV**: Dealership results with status and timestamps
- **Excel**: Multi-sheet report with summary and details
- **PDF**: Executive summary with charts
- **JSON**: Raw data for integrations
- **Debug Package**: Complete logs, screenshots, and metadata

### Standard Reports
1. **Project Summary**: Overview with success rates
2. **Detailed Results**: Per-dealership status and attempts  
3. **Error Analysis**: Failure patterns and recommendations
4. **Performance Report**: Speed and efficiency metrics
5. **Compliance Report**: Rate limiting and respectful automation evidence
6. **Debug Report**: Complete operation logs with error context

### Enhanced Export with Logs
```python
# Export with comprehensive logging
log.info("Data export initiated", {
    "operation": "data_export",
    "project_id": "proj123",
    "user_id": "user789",
    "metadata": {
        "export_format": "debug_package",
        "include_logs": true,
        "include_screenshots": true,
        "date_range": "2024-01-01 to 2024-01-07",
        "total_records": 156,
        "log_entries": 2453
    }
})

# Export completion logging
log.info("Data export completed", {
    "operation": "data_export_complete",
    "project_id": "proj123",
    "duration_ms": 15600,
    "metadata": {
        "file_size_mb": 25.6,
        "compression_ratio": 0.73,
        "download_url": "/exports/proj123_debug_20240101.zip",
        "expires_at": "2024-01-08T00:00:00Z"
    }
})
```