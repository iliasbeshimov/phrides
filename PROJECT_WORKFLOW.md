# Project Management Workflow

## Project Lifecycle

### 1. Project Creation
- **Create New Project**: User enters project name and description
- **Define Search Criteria**: Address/zip code, radius (default 150 miles), vehicle makes
- **Enter User Information**: Name, email, phone, and additional contact details
- **Set Custom Message**: Template or custom message for dealership forms
- **Save as Draft**: Project saved with status "draft"

### 2. Dealership Discovery
- **Geographic Search**: Find all dealerships within specified radius
- **Make Filtering**: Filter by selected vehicle makes
- **Distance Calculation**: Calculate and store distance from search location
- **Create ProjectDealership Records**: Link each dealership to project with "pending" status
- **Project Status**: Update to "active" with dealership counts

### 3. Contact Automation Phase
- **Batch Processing**: Process dealerships in batches (configurable size)
- **Form Automation**: Attempt automated contact for each dealership
- **Status Tracking**: Update contact_status for each attempt
  - `pending` → `success` (form submitted successfully)
  - `pending` → `failed` (automation failed)
- **Error Handling**: Capture screenshots and error details for failed attempts
- **Progress Updates**: Real-time updates of success/failure counts

### 4. Manual Review & Override
- **Review Failed Attempts**: User reviews dealerships with failed automation
- **Manual Contact**: User manually contacts dealerships outside the system
- **Status Override**: Mark dealerships as manually contacted
  - `failed` → `manual_override`
  - `pending` → `manual_override`
- **Add Notes**: Track manual contact details and outcomes

### 5. Project Management
- **Edit Project**: Update name, description, or search criteria
- **Retry Failed**: Re-attempt automation for failed dealerships
- **Archive/Complete**: Mark project as completed or archived
- **Delete Project**: Remove project and all associated data
- **Duplicate Project**: Create new project based on existing one

## Contact Status Flow

```
pending → automation_attempt → success ✓
                             → failed → manual_review → manual_override ✓
                                     → retry_automation → success ✓
                                                       → failed (cycle)
```

## UI User Flow

### Dashboard
- **Project List**: All projects with status summary
- **Quick Stats**: Total projects, active projects, completion rates
- **Recent Activity**: Latest contact attempts and status changes

### Project Detail View
- **Project Info**: Name, description, created date, search criteria
- **Summary Stats**: Total/contacted/success/failed dealership counts
- **Dealership Table**: Filterable list with contact status
- **Action Buttons**: Start automation, retry failed, export results

### Project Creation Flow
1. **New Project Form**: Name, description
2. **Search Setup**: Address/zip, radius, makes selection
3. **User Info Form**: Contact details for form submission
4. **Message Template**: Custom message or template selection
5. **Review & Create**: Confirm details and create project
6. **Dealership Discovery**: Automatic search and filtering
7. **Ready to Contact**: Project ready for automation

### Dealership Management
- **Status Filtering**: View by status (all, pending, success, failed, manual)
- **Bulk Actions**: Retry selected, mark as manual, export subset
- **Individual Actions**: View attempt details, manual override, add notes
- **Contact History**: Timeline of all contact attempts per dealership

## Status Tracking Features

### Real-time Updates
- **WebSocket Connection**: Live updates during automation runs
- **Progress Bar**: Visual progress indicator with ETA
- **Live Logs**: Stream of contact attempts and results

### Detailed Tracking
- **Attempt Timeline**: Complete history of contact attempts
- **Screenshot Gallery**: Visual confirmation of successful submissions
- **Error Analysis**: Categorized failure reasons with suggested fixes
- **Performance Metrics**: Success rates, average completion time

### Reporting
- **Project Summary**: Completion rates, geographic distribution
- **Export Options**: CSV/Excel export of results
- **Custom Reports**: Filterable data exports
- **Analytics Dashboard**: Success rate trends, common failure patterns