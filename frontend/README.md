# PSUU Frontend

A modern web interface for Parameter Selection Under Uncertainty (PSUU) that helps users connect to simulation models, configure parameters, define KPIs, run optimizations, and visualize results.

## Features

- Model connection configuration
- Parameter space definition
- KPI selection and objective setting
- Optimization configuration and execution
- Results visualization and analysis

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Running PSUU backend (API)

### Installation

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

## Project Structure

- `/src/components` - Reusable UI components
- `/src/views` - Page components
- `/src/contexts` - React context providers for state management
- `/src/api` - API integration with PSUU backend
- `/src/hooks` - Custom React hooks
- `/src/utils` - Utility functions

## Using the Interface

1. Connect to a model using the Model Setup page
2. Configure parameter spaces on the Parameters page
3. Select and configure KPIs on the KPIs page
4. Set up and run optimization on the Optimization page
5. Visualize and analyze results on the Results page

## Development

This project is built with:

- Next.js - React framework
- TailwindCSS - Styling
- Radix UI - Accessible component primitives
- React Hook Form - Form handling
- Plotly.js - Data visualization

## Backend Integration

This frontend connects to a PSUU API which should be running separately. The API endpoints are defined in `/src/api/index.ts`.
