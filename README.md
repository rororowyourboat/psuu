# Parameter Selection Under Uncertainty (PSUU)

A framework for simulation parameter optimization with uncertainty quantification.

## Features

- Model Integration:
  - Protocol-based integration with simulation models
  - Support for CLI-based model execution
  - Built-in cadCAD integration

- Parameter Space:
  - Continuous, integer, and categorical parameters
  - Constraint handling
  - Parameter space validation

- KPI Management:
  - Custom KPI definitions
  - Multi-objective optimization support
  - Real-time KPI calculation

- Optimization:
  - Multiple optimization algorithms (Grid Search, Random Search, Bayesian)
  - Real-time progress streaming
  - Result visualization

## Quick Start

1. Start the backend server:
```bash
python run_server.py
```

2. Start the frontend development server:
```bash
cd frontend
npm install
npm run dev
```

3. Open http://localhost:3000 in your browser

## API Documentation

The API documentation is available in two formats:

1. Interactive Web UI: Visit http://localhost:3000/api-docs in your browser
2. Source Code: See docstrings in `run_server.py`

### Key Endpoints

#### Model Connection
```
POST /api/models/test-connection
Content-Type: application/json

{
  "type": "protocol",
  "details": {
    "moduleClass": "template.model.SIRModel",
    "protocol": "cadcad"
  }
}
```

#### Parameter Space
```
GET /api/parameters
POST /api/parameters
```

#### KPIs
```
GET /api/kpis
POST /api/kpis
```

#### Optimization
```
POST /api/optimization/configure
POST /api/optimization/start
GET /api/optimization/stream
```

## Development

The project uses:
- Backend: Python, Flask, cadCAD
- Frontend: Next.js, TypeScript, TailwindCSS

### Project Structure

```
psuu/
├── frontend/         # Next.js frontend application
│   ├── src/
│   │   ├── api/     # API client
│   │   ├── pages/   # React pages
│   │   └── contexts/# State management
│   └── ...
├── psuu/            # Core PSUU package
│   ├── protocols/   # Model protocols
│   ├── optimizers/  # Optimization algorithms
│   └── ...
└── template/        # Example model implementation
```

### State Management

The frontend uses React Context for state management. The main state includes:
- Model connection status
- Parameter configurations
- KPI definitions
- Optimization settings and results

See `frontend/src/contexts/PsuuContext.tsx` for implementation details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
