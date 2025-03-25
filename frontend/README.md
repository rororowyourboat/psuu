# PSUU Frontend

Frontend UI for Parameter Selection Under Uncertainty (PSUU) - A framework for simulation parameter optimization.

## Features

- Interactive Model Connection
- Parameter Space Configuration
- KPI Definition & Selection
- Real-time Optimization Progress
- API Documentation Browser

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
npm start
```

## Project Structure

```
src/
├── api/          # API client and type definitions
├── components/   # Reusable React components
├── contexts/     # State management (PsuuContext)
├── pages/        # Next.js pages
│   ├── index.tsx       # Model connection
│   ├── parameters.tsx  # Parameter config
│   ├── kpis.tsx       # KPI selection
│   ├── optimization.tsx# Optimization config
│   ├── results.tsx    # Results view
│   └── api-docs.tsx   # API documentation
└── styles/      # Global styles and Tailwind config
```

## API Integration

The frontend communicates with the PSUU backend server using REST API and Server-Sent Events for real-time updates. See `src/api/index.ts` for implementation details.

### Key API Endpoints

- Model Connection: `POST /api/models/test-connection`
- Parameters: `GET/POST /api/parameters`
- KPIs: `GET/POST /api/kpis`
- Optimization: 
  - `POST /api/optimization/configure`
  - `POST /api/optimization/start`
  - `GET /api/optimization/stream` (SSE)

## State Management

Uses React Context for global state management. The main state includes:

```typescript
interface PsuuState {
  // Connection
  modelConnection: ModelConnection | null;
  isConnected: boolean;
  
  // Parameters
  parameters: Parameter[];
  
  // KPIs
  kpis: KPI[];
  
  // Optimization
  optimizationConfig: OptimizationConfig | null;
  currentJob: JobStatus;
  optimizationResults: OptimizationResult | null;
}
```

See `src/contexts/PsuuContext.tsx` for full implementation.

## Technologies

- Next.js 14
- TypeScript
- TailwindCSS
- Server-Sent Events (SSE)

## Requirements

- Node.js >= 18.0.0
- PSUU Backend Server

## Development

1. Clone repository
2. Install dependencies: `npm install`
3. Start backend server: `python run_server.py` (in root directory)
4. Start frontend: `npm run dev`
5. Visit http://localhost:3000

## Contributing

1. Fork repository
2. Create feature branch
3. Submit pull request

## License

MIT License - See LICENSE file for details
