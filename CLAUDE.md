# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains automotive dealership data, specifically Jeep dealership information in CSV format. The project appears to be focused on auto contacting and dealership management for car leasing operations.

## Data Structure

- **Main Data File**: `Dealerships - Jeep.csv` - Contains comprehensive dealership information including:
  - Dealer codes, locations, and contact information
  - Geographic coordinates (latitude/longitude) 
  - Business hours for sales, service, and parts departments
  - Website and email contact details
  - Distance calculations and business center classifications

## Data Schema

The CSV contains the following key fields:
- `dealer_code`, `dealer_name`, `address_line1`, `city`, `state`, `zip_code`
- `latitude`, `longitude`, `phone`, `website`, `email`  
- `sales_hours`, `service_hours`, `parts_hours` (JSON format with daily schedules)
- `sales_available`, `service_available`, `parts_available` (Y/N flags)
- `last_updated`, `found_via_function`, `found_via_strategy`

## Project Overview - Updated Architecture

This project has evolved into a comprehensive **Dealership Contact Automation System** with:

### Core Features
- **Project Management**: Named projects with full CRUD operations
- **Geographic Filtering**: Address/zip + radius-based dealership discovery
- **Multi-Make Support**: Jeep, Ram, Chrysler (expandable)
- **Automated Contact Forms**: Browser automation for form submission
- **Status Tracking**: Real-time progress with manual override capabilities
- **Web UI**: Complete React frontend for project management

### Key Components
- **Backend**: Python FastAPI with PostgreSQL
- **Frontend**: React with TypeScript, TailwindCSS
- **Automation**: Playwright for browser automation
- **Real-time**: WebSocket for live updates
- **Task Queue**: Celery for background processing

### Development Commands
```bash
# Backend setup
pip install -r requirements.txt
uvicorn src.interfaces.api.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev

# Database migrations
alembic upgrade head

# Run automation worker
celery -A src.automation.worker worker --loglevel=info
```

## Working with the Data

### Original CSV Data
- Business hours stored as JSON objects with daily schedules
- Coordinate data available for mapping and distance calculations
- The `has_quote` field indicates dealership pricing availability
- Use `business_center` and `dma` fields for regional analysis

### Database Schema
- **Projects**: User-created contact campaigns
- **ProjectDealerships**: Many-to-many with status tracking
- **ContactAttempts**: Detailed automation logs with screenshots
- **FormMappings**: Dealership-specific form configurations

## System Architecture Files

- `ARCHITECTURE.md` - Complete system design
- `PROJECT_WORKFLOW.md` - Project lifecycle and user flow
- `UI_COMPONENTS.md` - Frontend component specifications
- `TRACKING_SYSTEM.md` - Status tracking and analytics
- `API_ENDPOINTS.md` - Complete REST API specification
- `LOGGING_SYSTEM.md` - Comprehensive logging for debugging

## Logging & Debugging

Every operation generates structured logs for easy debugging:
- **Request Tracing**: Unique request IDs for complete operation tracking
- **Performance Metrics**: Response times, database query counts, memory usage
- **Error Context**: Detailed error information with stack traces
- **Automation Logs**: Browser interactions, form submissions, screenshot captures
- **User Activity**: Manual overrides, status changes, data exports

### Debug Commands
```bash
# View logs in real-time
tail -f logs/application.json | jq

# Query specific operation logs
grep "contact_attempt" logs/application.json | jq '.metadata'

# Export debug package for support
curl -X GET "/api/v1/debug/export?project_id=123&include_logs=true"
```