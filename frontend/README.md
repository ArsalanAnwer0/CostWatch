# CostWatch Frontend

React-based frontend for CostWatch cloud cost optimization platform.

## Features

- **Dashboard**: Overview of AWS costs with charts and metrics
- **Resource Management**: View EC2, RDS, and S3 resources
- **Cost Optimization**: Recommendations for cost savings
- **Alerts**: Cost anomalies and budget notifications
- **Mock Data**: Works immediately without backend for demos

## Quick Start

### Development Mode

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will open at `http://localhost:3000`

### Demo Mode (No Backend Required)

The frontend includes comprehensive mock data and works standalone:

1. **Login**: Use any email/password to login (demo mode)
2. **Dashboard**: See real-time cost data, charts, and metrics
3. **Resources**: Browse EC2, RDS, and S3 instances
4. **Optimizations**: View cost-saving recommendations
5. **Alerts**: Check cost anomalies and notifications

### Production Mode

For production with real backend:

1. Create `.env.local`:

```bash
REACT_APP_API_URL=http://your-api-gateway:8002
REACT_APP_ENVIRONMENT=production
```

2. Uncomment production login code in `LoginPage.js`

3. Build for production:

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/           # Static files
├── src/
│   ├── components/   # Reusable components
│   │   ├── CostCard.js
│   │   ├── CostChart.js
│   │   ├── ResourceTable.js
│   │   └── OptimizationCard.js
│   ├── pages/        # Page components
│   │   ├── LandingPage.js
│   │   ├── LoginPage.js
│   │   ├── RegisterPage.js
│   │   └── UpdatedDashboard.js
│   ├── services/     # API and data services
│   │   ├── api.js
│   │   └── mockData.js
│   ├── config/       # Configuration
│   │   └── api.js
│   └── App.js        # Main app component
```

## Components

### CostCard
Displays cost metrics with trend indicators.

```jsx
<CostCard
  title="Current Month Cost"
  amount={12450.67}
  change={-18.3}
  icon="💰"
  trend="down"
/>
```

### CostChart
SVG-based line chart for cost trends.

```jsx
<CostChart data={costTrendsData} height={250} />
```

### ResourceTable
Sortable table for AWS resources.

```jsx
<ResourceTable resources={ec2Instances} type="ec2" />
```

### OptimizationCard
Shows cost-saving recommendations.

```jsx
<OptimizationCard
  optimization={optimizationData}
  onImplement={handleImplement}
/>
```

## Mock Data

The app includes realistic mock data in `services/mockData.js`:

- AWS resource data (EC2, RDS, S3)
- Cost trends and predictions
- Optimization recommendations
- Alerts and notifications

Perfect for demos and testing without backend!

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | API Gateway URL | `http://localhost:8002` |
| `REACT_APP_RESOURCE_SCANNER_URL` | Resource Scanner URL | `http://localhost:8000` |
| `REACT_APP_COST_ANALYZER_URL` | Cost Analyzer URL | `http://localhost:8001` |
| `REACT_APP_ANALYTICS_ENGINE_URL` | Analytics Engine URL | `http://localhost:8003` |
| `REACT_APP_ALERT_MANAGER_URL` | Alert Manager URL | `http://localhost:8004` |
| `REACT_APP_ENVIRONMENT` | Environment | `development` |

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Docker

Build and run with Docker:

```bash
# Build
docker build -t costwatch-frontend .

# Run
docker run -p 3000:3000 costwatch-frontend
```

## Features by Page

### Landing Page
- Marketing content
- Features showcase
- Call to action

### Login Page
- Demo mode: Auto-login with any credentials
- Production mode: Real authentication

### Dashboard
- **Overview Tab**
  - Cost summary cards
  - 30-day cost trend chart
  - Service cost breakdown
  - Top optimization opportunities

- **Resources Tab**
  - EC2 instances table
  - RDS databases table
  - S3 buckets table
  - Sortable columns
  - Status indicators

- **Optimizations Tab**
  - Cost-saving recommendations
  - Severity levels
  - Potential monthly savings
  - Implementation actions

- **Alerts Tab**
  - Cost anomalies
  - Budget notifications
  - Unread indicators

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

See the main project [CONTRIBUTING.md](../docs/CONTRIBUTING.md)

## License

See main project [LICENSE](../LICENSE)
