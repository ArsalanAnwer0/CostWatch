# CostWatch Frontend Features

This document describes all the features and components available in the CostWatch frontend application.

## Dashboard Features

### Overview Section
- **Cost Summary Cards**: Display current month costs, last month comparison, savings opportunities, and total resources
- **Cost Trend Chart**: Interactive SVG-based line chart showing 30-day cost trends
- **Service Breakdown**: Grid of AWS services with cost percentages and visual progress bars
- **Top Optimizations**: Quick view of the most impactful cost-saving recommendations

### Resources Section
- **Tabbed Interface**: Switch between EC2, RDS, and S3 resources
- **Sortable Tables**: Click column headers to sort by any field
- **Status Badges**: Color-coded indicators for resource states (running, stopped, etc.)
- **Cost Information**: Per-resource monthly cost and utilization metrics

### Optimizations Section
- **Priority-Based Display**: High/medium/low severity recommendations
- **Savings Calculations**: Monthly savings potential for each recommendation
- **Resource Lists**: Affected resources for each optimization
- **Quick Actions**: View details and implement buttons

### Alerts Section
- **Real-time Notifications**: Budget alerts and anomaly detection
- **Severity Levels**: Color-coded high/medium/low severity alerts
- **Read/Unread Status**: Visual distinction for new alerts
- **Action Buttons**: Acknowledge and view details options

## UI Components

### Core Components
- **CostCard**: Metric display cards with trend indicators
- **CostChart**: Custom SVG line chart for cost visualization
- **ResourceTable**: Sortable, filterable table for AWS resources
- **OptimizationCard**: Recommendation cards with savings info

### Utility Components
- **LoadingSpinner**: Configurable loading indicator (small/medium/large)
- **ErrorBoundary**: Catches React errors and displays fallback UI
- **Modal**: Reusable dialog component with backdrop and sizes
- **SearchBar**: Search input with clear button
- **Badge**: Status indicators with multiple color variants
- **Toast**: Notification system for success/error/warning messages
- **ToastContainer**: Manages multiple toast notifications

## Custom React Hooks

### Available Hooks
- **useDebounce**: Delay value updates for search/filter operations
- **useLocalStorage**: Persist state in browser localStorage
- **useWindowSize**: Track window dimensions for responsive design

## Utility Functions

### Formatters (utils/formatters.js)
- `formatCurrency()` - Format numbers as currency
- `formatCompactNumber()` - Format with K, M, B suffixes
- `formatPercentage()` - Format decimal as percentage
- `formatDate()` - Format dates with locale support
- `formatRelativeTime()` - "2 hours ago" style timestamps
- `formatFileSize()` - Format bytes to KB/MB/GB
- `truncateText()` - Truncate long strings with ellipsis
- `formatARN()` - Extract resource name from AWS ARN

### Validators (utils/validation.js)
- `isValidEmail()` - Email format validation
- `validatePassword()` - Password strength checker
- `isValidAWSAccountId()` - 12-digit AWS account validation
- `isValidAWSRegion()` - AWS region code validation
- `isValidURL()` - URL format validation
- `isValidPhone()` - Phone number validation
- `isRequired()` - Required field validation
- `isValidLength()` - String length validation
- `isInRange()` - Number range validation
- `isValidCreditCard()` - Luhn algorithm credit card validation

## Constants

### Application Constants (constants/index.js)
- **API Configuration**: Timeout, retry settings
- **AWS Regions**: All available AWS regions with names
- **AWS Services**: List of supported services
- **Resource States**: Running, stopped, terminated, etc.
- **Alert Severity**: High, medium, low levels
- **Optimization Types**: Right-sizing, unused resources, etc.
- **Chart Colors**: Consistent color scheme
- **Status Colors**: State-specific colors
- **Error Messages**: Standardized error messages
- **Success Messages**: Standardized success messages

## Animations and Transitions

### Available Animations (styles/animations.css)
- **fadeIn**: Fade in elements
- **slideUp**: Slide up with fade
- **slideDown**: Slide down with fade
- **scaleIn**: Scale in with fade
- **pulse**: Pulsing animation for emphasis
- **shimmer**: Loading skeleton effect
- **Stagger animations**: Sequential animations for lists
- **Hover effects**: Lift and scale transforms

## Demo Mode Features

### Instant Demo Capability
- Works without backend setup
- Comprehensive mock AWS data
- Realistic cost trends and patterns
- Sample EC2, RDS, and S3 resources
- Pre-configured optimization recommendations
- Simulated alerts and notifications
- Auto-login with any credentials

## Code Organization

### Directory Structure
```
frontend/src/
├── components/       # Reusable UI components
├── pages/           # Page-level components
├── services/        # API and mock data services
├── hooks/           # Custom React hooks
├── utils/           # Helper functions
├── constants/       # Application constants
├── styles/          # Global styles and animations
└── config/          # Configuration files
```

### Import Simplification
- Central export points for components, hooks, and utils
- Clean import statements: `import { CostCard } from 'components'`
- Organized by feature and purpose

## Best Practices

### Performance Optimizations
- Debounced search inputs
- Optimized re-renders with React hooks
- CSS animations for smooth transitions
- Lazy loading where appropriate

### Accessibility
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus management in modals
- Semantic HTML structure

### User Experience
- Loading states for async operations
- Error boundaries for graceful failures
- Toast notifications for user feedback
- Responsive design for all screen sizes
- Smooth animations and transitions

## Getting Started

### Quick Start
```bash
cd frontend
npm install
npm start
```

Visit http://localhost:3000 and login with any email/password to explore the fully functional dashboard!

### Using Components
```javascript
import { CostCard, LoadingSpinner, Modal } from 'components';
import { formatCurrency, isValidEmail } from 'utils';
import { useDebounce, useLocalStorage } from 'hooks';

function MyComponent() {
  const [value, setValue] = useLocalStorage('myKey', 'default');
  const debouncedValue = useDebounce(value, 500);

  return (
    <CostCard
      title="Total Cost"
      amount={12450.67}
      icon="💰"
    />
  );
}
```

## Future Enhancements

### Planned Features
- Dark mode support
- Advanced filtering and search
- Export to CSV/PDF
- Custom dashboard layouts
- Real-time WebSocket updates
- Multi-account support
- Budget planning tools
- Cost forecasting

---

For more information, see:
- [Local Setup Guide](LOCAL_SETUP.md)
- [API Documentation](API.md)
- [Main README](../README.md)
