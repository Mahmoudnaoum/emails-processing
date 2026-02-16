# Retool Setup Guide for Email Relationship Analysis System

This guide will help you set up a Retool application to interact with the Email Relationship Analysis API.

## Prerequisites

1. Email Relationship Analysis API server running (http://localhost:8000)
2. Retool account (self-hosted or cloud)
3. Basic understanding of Retool components

## API Configuration

### 1. Create API Resource

1. In Retool, go to **Resources** → **Create new** → **API**
2. Configure the resource:
   - **Name**: `Email Analysis API`
   - **Base URL**: `http://localhost:8000` (or your production URL)
   - **Authentication**: None (for development) or Bearer Token (for production)

### 2. Test Connection

Click **Test connection** to verify the API is accessible.

## Application Structure

### Main Dashboard Components

#### 1. User Management Module

**Components:**
- Table to display all users
- Form to create new users
- User detail view

**API Endpoints:**
- `GET /users` - List all users (need to implement)
- `POST /users` - Create user
- `GET /users/{email}` - Get user by email

**Query Example:**
```javascript
// Create User
POST /users
{
  "email": "{{textInput1.value}}",
  "name": "{{textInput2.value}}"
}
```

#### 2. Email Upload Module

**Components:**
- File upload component for JSON files
- User email selector
- Upload button
- Progress indicator

**API Endpoints:**
- `POST /upload-emails` - Upload and process emails

**Query Example:**
```javascript
// Upload Emails
POST /upload-emails
Headers: {
  "user-email": "{{userDropdown.value}}"
}
Body: FormData {
  "file": "{{fileUpload1.files[0]}}"
}
```

#### 3. Processing Status Module

**Components:**
- Statistics cards showing:
  - Total emails processed
  - Emails filtered
  - Unique threads
  - Processing time
- Progress bar for batch operations

**API Endpoints:**
- `GET /users/{id}/stats` - Get processing statistics

**Query Example:**
```javascript
// Get Stats
GET /users/{{currentUser.id}}/stats
```

#### 4. Relationships Dashboard

**Components:**
- Relationship graph visualization
- Table of relationships with filters
- Relationship strength indicators
- Search functionality

**API Endpoints:**
- `GET /users/{id}/relationships` - Get relationships

**Query Example:**
```javascript
// Get Relationships
GET /users/{{currentUser.id}}/relationships?limit=100
```

**Visualization:**
Use the **Graph** component to visualize relationships:
- Nodes: People
- Edges: Interactions
- Edge thickness: Interaction count
- Node size: Relationship strength

#### 5. Expertise Tracking Module

**Components:**
- Expertise matrix (people × expertise areas)
- Expertise confidence scores
- Search by expertise area
- Filter by confidence level

**API Endpoints:**
- `GET /users/{id}/expertise` - Get expertise data

**Query Example:**
```javascript
// Get Expertise
GET /users/{{currentUser.id}}/expertise
```

**Visualization:**
Use a **Heatmap** or **Table** component:
- Rows: People
- Columns: Expertise areas
- Cells: Confidence scores (color-coded)

#### 6. Interactions Timeline

**Components:**
- Timeline view of interactions
- Date range picker
- Filter by interaction type
- Search by subject/participants

**API Endpoints:**
- `GET /users/{id}/interactions` - Get interactions

**Query Example:**
```javascript
// Get Interactions by Date Range
GET /users/{{currentUser.id}}/interactions
Params: {
  "start_date": "{{dateRange1.value.start}}",
  "end_date": "{{dateRange1.value.end}}"
}
```

**Visualization:**
Use the **Calendar** or **Timeline** component:
- Display interactions chronologically
- Color-code by interaction type
- Show participant count

## Step-by-Step Setup

### Step 1: Create New App

1. Click **Create new app** in Retool
2. Name it: "Email Relationship Analysis"
3. Choose a template or start blank

### Step 2: Set Up API Resources

1. Create the API resource as described above
2. Test all endpoints to ensure they work
3. Save the resource

### Step 3: Build User Management

1. Add a **Table** component for users
2. Create query: `GET /users` (or manually add users)
3. Add **Text Input** components for email and name
4. Create query: `POST /users`
5. Add **Button** to trigger create user query
6. Configure success event to refresh user table

### Step 4: Build Email Upload

1. Add **Dropdown** to select user
2. Add **File Upload** component
3. Create query: `POST /upload-emails`
4. Configure query to use selected user and uploaded file
5. Add **Button** to trigger upload
6. Add **Progress Bar** to show upload status

### Step 5: Build Processing Dashboard

1. Add **Statistics Cards** (4 cards)
2. Create query: `GET /users/{id}/stats`
3. Bind each card to a stat field:
   - Total emails
   - Processed emails
   - Filtered emails
   - Unique threads

### Step 6: Build Relationships View

1. Add **Graph** component
2. Create query: `GET /users/{id}/relationships`
3. Configure graph:
   - Nodes: `{{relationships.data}}`
   - Node label: `person_name`
   - Node ID: `person_id`
   - Edges: Based on interaction_count
4. Add **Search Input** to filter relationships
5. Add **Table** component for detailed view

### Step 7: Build Expertise Matrix

1. Add **Table** or **Heatmap** component
2. Create query: `GET /users/{id}/expertise`
3. Configure display:
   - Rows: People names
   - Columns: Expertise areas
   - Values: Confidence scores
4. Add color coding for confidence levels
5. Add filter by minimum confidence

### Step 8: Build Interactions Timeline

1. Add **Date Range Picker** component
2. Add **Timeline** component
3. Create query: `GET /users/{id}/interactions`
4. Configure query to use date range
5. Bind timeline to query results
6. Add **Search Input** for subject/participants
7. Add **Filter Dropdown** for interaction type

### Step 9: Add Navigation

1. Add **Tabs** component for main sections:
   - Dashboard
   - Relationships
   - Expertise
   - Interactions
   - Settings
2. Configure each tab to show relevant components
3. Add **Sidebar** for quick navigation

### Step 10: Polish and Test

1. Add loading states to all queries
2. Add error handling with user-friendly messages
3. Add tooltips and help text
4. Test all functionality
5. Optimize for different screen sizes

## Advanced Features

### Real-time Updates

Use Retool's **WebSocket** or **Polling** for real-time updates:

```javascript
// Poll for updates
setInterval(() => {
  getStats.trigger()
}, 30000) // Every 30 seconds
```

### Export Functionality

Add export buttons for data:

```javascript
// Export to CSV
const csv = convertToCSV(relationships.data)
downloadFile(csv, 'relationships.csv', 'text/csv')
```

### Advanced Filtering

Add complex filters:

```javascript
// Filter by multiple criteria
const filtered = relationships.data.filter(r => 
  r.interaction_count > 5 &&
  r.last_interaction_date > '2024-01-01'
)
```

### Collaboration Features

Add user comments and annotations:

```javascript
// Add comment to relationship
POST /relationships/{{relationship.id}}/comments
{
  "comment": "{{commentInput.value}}",
  "user_id": "{{currentUser.id}}"
}
```

## Deployment

### Self-Hosted Retool

1. Deploy API server to your server
2. Update Retool API resource URL
3. Configure authentication
4. Set up SSL certificates

### Cloud Retool

1. Deploy API server with public URL
2. Configure CORS on API server
3. Set up authentication tokens
4. Update Retool API resource

## Troubleshooting

### Connection Issues

1. Check API server is running
2. Verify CORS settings
3. Check firewall rules
4. Test API endpoints directly

### Data Not Loading

1. Check query parameters
2. Verify user ID is correct
3. Check API response format
4. Review browser console for errors

### Performance Issues

1. Reduce data returned (use pagination)
2. Add caching to queries
3. Optimize database queries
4. Use lazy loading for large datasets

## Best Practices

1. **Security**: Always use authentication in production
2. **Error Handling**: Provide clear error messages
3. **Performance**: Implement pagination and caching
4. **User Experience**: Add loading states and progress indicators
5. **Testing**: Test all user flows thoroughly
6. **Documentation**: Keep Retool queries well-documented

## Next Steps

1. Implement additional API endpoints as needed
2. Add more visualizations and insights
3. Integrate with other tools (CRM, calendar)
4. Add notification system
5. Implement advanced analytics

## Support

For issues with Retool:
- Retool Documentation: https://docs.retool.com
- Retool Community: https://community.retool.com

For issues with the API:
- Check API logs
- Test endpoints directly
- Review API documentation at `/docs`