# UI Components & User Interface Design

## Main Application Structure

### Layout Components
```typescript
// App Shell
<AppLayout>
  <Header />
  <Sidebar />
  <MainContent />
  <Footer />
</AppLayout>

// Navigation
<Sidebar>
  - Dashboard
  - Projects
  - Settings
  - Help
</Sidebar>
```

## Page Components

### 1. Dashboard Page
```typescript
<Dashboard>
  <StatsOverview>
    - Total Projects
    - Active Projects
    - Success Rate
    - Recent Activity
  </StatsOverview>
  
  <RecentProjects>
    - Quick project cards
    - Status indicators
    - Action buttons
  </RecentProjects>
  
  <ActivityFeed>
    - Real-time contact attempts
    - Success/failure notifications
    - System status updates
  </ActivityFeed>
</Dashboard>
```

### 2. Projects List Page
```typescript
<ProjectsList>
  <ProjectsHeader>
    <SearchFilter />
    <StatusFilter />
    <CreateProjectButton />
  </ProjectsHeader>
  
  <ProjectsTable>
    columns: [
      - Name
      - Created Date
      - Status
      - Total Dealerships
      - Success Rate
      - Last Activity
      - Actions
    ]
  </ProjectsTable>
  
  <ProjectCard> // Alternative card view
    - Project name & description
    - Progress bar
    - Status badges
    - Quick actions
  </ProjectCard>
</ProjectsList>
```

### 3. Project Detail Page
```typescript
<ProjectDetail>
  <ProjectHeader>
    <ProjectInfo />
    <ProjectActions>
      - Edit Project
      - Start/Resume Automation
      - Retry Failed
      - Export Results
      - Archive/Delete
    </ProjectActions>
  </ProjectHeader>
  
  <ProjectStats>
    <StatCard title="Total" value={totalCount} />
    <StatCard title="Contacted" value={contactedCount} />
    <StatCard title="Success" value={successCount} />
    <StatCard title="Failed" value={failedCount} />
  </ProjectStats>
  
  <DealershipsSection>
    <DealershipsFilters>
      - Status filter
      - Distance range
      - Make filter
      - Search by name
    </DealershipsFilters>
    
    <DealershipsTable>
      columns: [
        - Dealership Name
        - Address
        - Distance
        - Make
        - Contact Status
        - Last Attempt
        - Actions
      ]
    </DealershipsTable>
  </DealershipsSection>
</ProjectDetail>
```

### 4. Project Creation Wizard
```typescript
<ProjectWizard>
  <Step1_BasicInfo>
    <FormField label="Project Name" required />
    <FormField label="Description" />
  </Step1_BasicInfo>
  
  <Step2_SearchCriteria>
    <AddressInput 
      placeholder="Enter address or zip code"
      validation="geocoding"
    />
    <RadiusSlider 
      min={10} 
      max={500} 
      default={150}
      unit="miles"
    />
    <MakeSelector 
      options={['Jeep', 'Ram', 'Chrysler']}
      multiple
    />
  </Step2_SearchCriteria>
  
  <Step3_UserInfo>
    <FormField label="First Name" required />
    <FormField label="Last Name" required />
    <FormField label="Email" type="email" required />
    <FormField label="Phone" type="tel" />
    <FormField label="Preferred Contact Method" />
  </Step3_UserInfo>
  
  <Step4_Message>
    <MessageTemplateSelector />
    <CustomMessageEditor />
    <VariableInserter /> // {firstName}, {makes}, etc.
  </Step4_Message>
  
  <Step5_Review>
    <ProjectSummary />
    <DealershipPreview /> // Show sample results
    <CreateButton />
  </Step5_Review>
</ProjectWizard>
```

## Reusable UI Components

### Form Components
```typescript
<FormField>
  - Label with optional indicator
  - Input with validation
  - Error message display
  - Help text
</FormField>

<AddressAutocomplete>
  - Google Places integration
  - Validation and geocoding
  - Address standardization
</AddressAutocomplete>

<MakeSelector>
  - Multi-select with checkboxes
  - Visual brand logos
  - Search/filter capability
</MakeSelector>
```

### Data Display Components
```typescript
<StatusBadge>
  variants: [
    - pending (yellow)
    - success (green) 
    - failed (red)
    - manual_override (blue)
  ]
</StatusBadge>

<ProgressBar>
  - Percentage complete
  - Color coding by status
  - Animated transitions
</ProgressBar>

<DataTable>
  - Sortable columns
  - Filterable rows
  - Pagination
  - Bulk selection
  - Export functionality
</DataTable>
```

### Action Components
```typescript
<ActionButton>
  variants: [
    - primary (blue)
    - secondary (gray)
    - success (green)
    - danger (red)
    - warning (yellow)
  ]
  - Loading states
  - Confirmation dialogs
</ActionButton>

<BulkActions>
  - Select all/none
  - Status updates
  - Retry automation
  - Export selected
</BulkActions>
```

### Modal Components
```typescript
<ConfirmationModal>
  - Action confirmation
  - Warning messages
  - Cancel/proceed options
</ConfirmationModal>

<DealershipDetailModal>
  - Full dealership info
  - Contact attempt history
  - Manual status override
  - Notes section
</DealershipDetailModal>

<ContactAttemptModal>
  - Attempt timeline
  - Screenshots gallery
  - Error details
  - Retry options
</ContactAttemptModal>
```

## Real-time Features

### Live Updates
```typescript
<LiveStatusUpdater>
  - WebSocket connection
  - Real-time status changes
  - Progress notifications
  - Error alerts
</LiveStatusUpdater>

<AutomationProgress>
  - Live progress bar
  - Current dealership being processed
  - Success/failure counters
  - ETA calculation
</AutomationProgress>
```

### Notifications
```typescript
<NotificationSystem>
  types: [
    - success: "Contact attempt successful"
    - error: "Automation failed for [dealer]"
    - info: "Processing batch 3 of 10"
    - warning: "Rate limit reached, pausing"
  ]
  - Toast notifications
  - Dismissible alerts
  - Notification history
</NotificationSystem>
```

## Responsive Design

### Breakpoints
- **Mobile**: < 768px (single column, collapsed navigation)
- **Tablet**: 768px - 1024px (adapted layout, touch-friendly)
- **Desktop**: > 1024px (full feature set)

### Mobile Adaptations
- **Navigation**: Collapsible hamburger menu
- **Tables**: Horizontal scroll or card transformation
- **Forms**: Stacked layout with larger touch targets
- **Actions**: Bottom sheet for bulk actions

## Accessibility Features

### ARIA Labels
- Screen reader support
- Keyboard navigation
- Focus management
- Color contrast compliance

### Keyboard Shortcuts
- `Ctrl+N`: New project
- `Ctrl+S`: Save current form
- `Space`: Toggle selection
- `Enter`: Primary action
- `Esc`: Cancel/close modal

## Performance Optimizations

### Data Loading
- Lazy loading for large tables
- Virtual scrolling for performance
- Infinite scroll for project lists
- Optimistic updates for better UX

### Caching Strategy
- Project data caching
- Dealership search results
- Form state preservation
- Browser storage for preferences