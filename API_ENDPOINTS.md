# API Endpoints Specification

## Base URL: `/api/v1`

## Authentication
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`
- **Login Endpoint**: `POST /auth/login`

## Request Logging
Every API request generates comprehensive logs for debugging:
- **Request ID**: Unique identifier for tracing (header: `X-Request-ID`)
- **User Context**: User ID, session info, IP address
- **Performance**: Response time, database query count
- **Errors**: Detailed error context with stack traces

---

## Projects API

### List Projects
```http
GET /projects
Query Parameters:
  - status: string (draft, active, completed, archived)
  - page: integer (default: 1)
  - limit: integer (default: 20)
  - search: string (search by name)
  - sort: string (name, created_at, updated_at)
  - order: string (asc, desc)

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "name": "Project Name",
      "description": "Project description",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "search_criteria": {
        "location": "New York, NY",
        "radius_miles": 150,
        "makes": ["jeep", "ram"]
      },
      "stats": {
        "total_dealerships": 45,
        "contacted_count": 23,
        "success_count": 18,
        "failed_count": 5,
        "success_rate": 78.26
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

### Get Project Details
```http
GET /projects/{project_id}

Response: 200 OK
{
  "id": "uuid",
  "name": "Project Name",
  "description": "Project description",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "search_criteria": {
    "location": "New York, NY",
    "coordinates": {"lat": 40.7128, "lng": -74.0060},
    "radius_miles": 150,
    "makes": ["jeep", "ram"]
  },
  "user_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "(555) 123-4567"
  },
  "contact_template": {
    "subject": "Vehicle Inquiry",
    "message": "I'm interested in your {makes} inventory..."
  },
  "stats": {
    "total_dealerships": 45,
    "contacted_count": 23,
    "success_count": 18,
    "failed_count": 5,
    "pending_count": 22,
    "manual_override_count": 0,
    "success_rate": 78.26
  }
}
```

### Create Project
```http
POST /projects

Request Body:
{
  "name": "Project Name",
  "description": "Project description",
  "search_criteria": {
    "location": "New York, NY",
    "radius_miles": 150,
    "makes": ["jeep", "ram"]
  },
  "user_info": {
    "first_name": "John",
    "last_name": "Doe", 
    "email": "john@example.com",
    "phone": "(555) 123-4567",
    "preferred_contact": "email"
  },
  "contact_template": {
    "message": "Custom message template..."
  }
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Project Name",
  "status": "draft",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Project
```http
PUT /projects/{project_id}

Request Body: (same as create, partial updates allowed)

Response: 200 OK
```

### Delete Project
```http
DELETE /projects/{project_id}

Response: 204 No Content
```

---

## Dealerships API

### Get Project Dealerships
```http
GET /projects/{project_id}/dealerships
Query Parameters:
  - status: string (pending, success, failed, manual_override)
  - make: string (filter by vehicle make)
  - distance_min: number (minimum distance in miles)
  - distance_max: number (maximum distance in miles)
  - search: string (search by dealership name)
  - page: integer
  - limit: integer
  - sort: string (name, distance, status, last_attempt)
  - order: string (asc, desc)

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "dealership": {
        "id": "uuid",
        "name": "Downtown Jeep",
        "address": "123 Main St, City, ST 12345",
        "phone": "(555) 123-4567",
        "website": "https://dealership.com",
        "makes_supported": ["jeep"]
      },
      "distance_miles": 12.5,
      "contact_status": "success",
      "contact_attempts": 1,
      "last_attempt_at": "2024-01-01T10:00:00Z",
      "manual_notes": null,
      "manual_status_set_by": null
    }
  ],
  "pagination": {...}
}
```

### Update Dealership Status
```http
PATCH /projects/{project_id}/dealerships/{dealership_id}

Request Body:
{
  "contact_status": "manual_override",
  "manual_notes": "Called directly, spoke with sales manager",
  "manual_status_set_by": "user@example.com"
}

Response: 200 OK
```

### Bulk Update Dealership Status
```http
PATCH /projects/{project_id}/dealerships/bulk

Request Body:
{
  "dealership_ids": ["uuid1", "uuid2", "uuid3"],
  "contact_status": "manual_override",
  "manual_notes": "Bulk manual update",
  "manual_status_set_by": "user@example.com"
}

Response: 200 OK
{
  "updated_count": 3,
  "errors": []
}
```

---

## Contact Automation API

### Start Automation
```http
POST /projects/{project_id}/automation/start

Request Body:
{
  "dealership_ids": ["uuid1", "uuid2"], // optional, default: all pending
  "batch_size": 5,                      // optional, default: 3
  "delay_between_attempts": 2.0,        // optional, default: 2.0 seconds
  "max_retries": 3                      // optional, default: 3
}

Response: 202 Accepted
{
  "automation_job_id": "uuid",
  "status": "started",
  "total_dealerships": 25,
  "estimated_duration": 1800 // seconds
}
```

### Get Automation Status
```http
GET /projects/{project_id}/automation/status

Response: 200 OK
{
  "automation_job_id": "uuid",
  "status": "running", // queued, running, paused, completed, failed
  "progress": {
    "total_dealerships": 25,
    "processed": 10,
    "successful": 8,
    "failed": 2,
    "current_dealership": {
      "name": "City Motors",
      "status": "filling_form"
    }
  },
  "started_at": "2024-01-01T10:00:00Z",
  "estimated_completion": "2024-01-01T10:30:00Z"
}
```

### Pause/Resume Automation
```http
POST /projects/{project_id}/automation/pause
POST /projects/{project_id}/automation/resume

Response: 200 OK
{
  "status": "paused" // or "resumed"
}
```

### Stop Automation
```http
POST /projects/{project_id}/automation/stop

Response: 200 OK
{
  "status": "stopped",
  "final_stats": {
    "processed": 15,
    "successful": 12,
    "failed": 3
  }
}
```

### Retry Failed Attempts
```http
POST /projects/{project_id}/automation/retry

Request Body:
{
  "dealership_ids": ["uuid1", "uuid2"], // optional, default: all failed
  "max_retries": 2
}

Response: 202 Accepted
```

---

## Contact Attempts API

### Get Contact Attempts
```http
GET /projects/{project_id}/dealerships/{dealership_id}/attempts

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "attempt_number": 1,
      "status": "success",
      "started_at": "2024-01-01T10:00:00Z",
      "completed_at": "2024-01-01T10:02:30Z",
      "duration_seconds": 150,
      "error_type": null,
      "error_message": null,
      "screenshots": {
        "before": "/screenshots/before_uuid.png",
        "after": "/screenshots/after_uuid.png",
        "error": null
      },
      "automation_strategy": "standard_form_fill",
      "browser_type": "chromium"
    }
  ]
}
```

### Get Contact Attempt Details
```http
GET /attempts/{attempt_id}

Response: 200 OK
{
  "id": "uuid",
  "project_dealership_id": "uuid",
  "attempt_number": 1,
  "status": "failed",
  "error_type": "captcha_detected",
  "error_message": "reCAPTCHA challenge detected on page",
  "error_stack_trace": "...",
  "screenshots": {...},
  "browser_logs": [...],
  "automation_details": {
    "strategy": "standard_form_fill",
    "form_mapping_version": "v1.2.0",
    "page_load_time_ms": 2300,
    "form_fill_time_ms": 5400,
    "submission_time_ms": 1200
  }
}
```

---

## Analytics & Reporting API

### Get Project Analytics
```http
GET /projects/{project_id}/analytics

Response: 200 OK
{
  "success_metrics": {
    "overall_success_rate": 78.5,
    "automation_success_rate": 65.2,
    "manual_completion_rate": 13.3,
    "total_contacted": 45,
    "avg_attempts_per_dealership": 1.2
  },
  "performance_metrics": {
    "avg_time_per_attempt": 180, // seconds
    "fastest_attempt": 45,
    "slowest_attempt": 300,
    "total_automation_time": 8100
  },
  "error_breakdown": {
    "captcha_detected": 5,
    "form_not_found": 2,
    "timeout": 3,
    "network_error": 1
  },
  "geographic_distribution": [
    {
      "state": "NY",
      "total": 15,
      "success": 12,
      "success_rate": 80.0
    }
  ]
}
```

### Export Project Data
```http
GET /projects/{project_id}/export
Query Parameters:
  - format: string (csv, excel, json)
  - include_attempts: boolean (default: false)
  - status_filter: string (comma-separated statuses)

Response: 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="project_data.csv"
```

---

## WebSocket Events

### Connection
```javascript
// Connect to project-specific updates
const socket = io('/projects/{project_id}');
```

### Event Types
```javascript
// Automation progress updates
socket.on('automation_progress', (data) => {
  // { processed: 10, total: 25, current_dealership: {...} }
});

// Status changes
socket.on('status_update', (data) => {
  // { dealership_id: 'uuid', old_status: 'pending', new_status: 'success' }
});

// Error alerts
socket.on('error_alert', (data) => {
  // { dealership_id: 'uuid', error_type: 'captcha_detected', message: '...' }
});

// Automation completion
socket.on('automation_completed', (data) => {
  // { total_processed: 25, successful: 20, failed: 5, duration: 1800 }
});
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` (400): Invalid request data
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict (e.g., duplicate name)
- `RATE_LIMITED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

---

## Debug Endpoints

### Get Request Logs
```http
GET /debug/logs
Query Parameters:
  - request_id: string (trace specific request)
  - user_id: string
  - start_time: datetime
  - end_time: datetime
  - level: string (DEBUG, INFO, WARN, ERROR)
  - operation: string
  - limit: integer (default: 100)

Response: 200 OK
{
  "data": [
    {
      "id": "log_uuid",
      "timestamp": "2024-01-01T10:00:00Z",
      "level": "INFO",
      "operation": "project_create",
      "message": "Project created successfully",
      "request_id": "req_12345",
      "user_id": "user_789",
      "duration_ms": 1250,
      "metadata": {
        "project_name": "Downtown Search",
        "validation_time_ms": 45,
        "database_time_ms": 890
      }
    }
  ]
}
```

### Get Automation Logs
```http
GET /projects/{project_id}/logs
Query Parameters:
  - dealership_id: string (specific dealership logs)
  - level: string
  - operation: string (contact_attempt_start, form_submit, etc.)
  - start_time: datetime
  - end_time: datetime

Response: 200 OK
{
  "data": [
    {
      "timestamp": "2024-01-01T10:00:00Z",
      "level": "DEBUG",
      "operation": "form_field_fill",
      "dealership_name": "City Motors",
      "message": "Form field filled successfully",
      "metadata": {
        "field_name": "first_name",
        "field_selector": "input[name='fname']",
        "fill_time_ms": 150
      }
    }
  ]
}
```

### Export Debug Data
```http
GET /debug/export
Query Parameters:
  - project_id: string
  - format: string (json, csv)
  - include_logs: boolean
  - include_screenshots: boolean
  - start_time: datetime
  - end_time: datetime

Response: 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="debug_export.zip"
```

---

## Request/Response Logging Examples

### Successful Request Log
```json
{
  "timestamp": "2024-01-01T10:00:00Z",
  "level": "INFO",
  "operation": "api_request",
  "message": "API request completed successfully",
  "request_id": "req_12345",
  "user_id": "user_789",
  "session_id": "sess_456",
  "duration_ms": 1250,
  "metadata": {
    "method": "POST",
    "path": "/api/v1/projects",
    "status_code": 201,
    "request_size_bytes": 342,
    "response_size_bytes": 156,
    "database_queries": 3,
    "database_time_ms": 890,
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.100"
  }
}
```

### Error Request Log
```json
{
  "timestamp": "2024-01-01T10:05:00Z",
  "level": "ERROR",
  "operation": "api_request_error",
  "message": "Validation failed for project creation",
  "request_id": "req_12346",
  "user_id": "user_789",
  "duration_ms": 45,
  "error_details": {
    "error_type": "ValidationError",
    "error_code": "VALIDATION_ERROR",
    "error_message": "Project name is required",
    "is_retryable": false
  },
  "metadata": {
    "method": "POST",
    "path": "/api/v1/projects",
    "status_code": 400,
    "validation_errors": [
      {
        "field": "name",
        "message": "This field is required"
      }
    ],
    "request_body_sanitized": {
      "description": "Project description",
      "search_criteria": "..."
    }
  }
}
```