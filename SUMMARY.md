# PSUU: Parameter Selection Under Uncertainty

## Overview

PSUU is a framework that integrates:
1. Backend optimization engine (Python)
2. Web-based user interface (Next.js)
3. Template model implementation (cadCAD)

## Components

### 1. PSUU Module

Core optimization framework that provides:
- Model protocol integration
- Parameter space management
- KPI calculation
- Multiple optimization algorithms
- Real-time progress streaming

Installation:
```bash
pip install -e .
```

### 2. Frontend UI

Web interface for:
- Model connection configuration
- Parameter space definition
- KPI selection and objectives
- Optimization configuration
- Real-time results visualization

Setup:
```bash
cd frontend
npm install
npm run dev
```

### 3. Template Model

Example SIR epidemiological model demonstrating:
- Protocol implementation
- Parameter definition
- KPI calculation
- Integration with PSUU

## Ways to Run

### 1. Development Mode

Best for development and testing:

```bash
# Terminal 1: Start backend
python run_server.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Visit http://localhost:3000

### 2. CLI Mode

Best for scripted optimization:

```bash
# Initialize config
python -m psuu.cli init

# Add parameters
python -m psuu.cli add-param beta --type continuous --min 0.1 --max 0.5
python -m psuu.cli add-param gamma --type continuous --min 0.01 --max 0.1

# Add KPIs
python -m psuu.cli add-kpi peak_infected --objective --maximize false

# Run optimization
python -m psuu.cli run --method bayesian --iterations 20
```

### 3. Python API

Best for custom integration:

```python
from psuu import PsuuExperiment
from template.model import SIRModel

# Create experiment
experiment = PsuuExperiment()
experiment.model = SIRModel()

# Configure
experiment.set_parameter_space({
    'beta': (0.1, 0.5),
    'gamma': (0.01, 0.1)
})

# Run optimization
results = experiment.run(
    method='bayesian',
    iterations=20,
    objective='peak_infected',
    maximize=False
)
```

## Protocol Integration

Models can integrate with PSUU in three ways:

### 1. Protocol Implementation

Best for Python models:
```python
from psuu.protocols import ModelProtocol

class MyModel(ModelProtocol):
    def get_parameter_space(self):
        return {...}
    
    def get_kpi_definitions(self):
        return {...}
    
    def run(self, params):
        return {...}
```

### 2. CLI Integration

Best for external executables:
```python
experiment = PsuuExperiment(
    simulation_command="./model",
    param_format="--{name} {value}",
    output_format="json"
)
```

### 3. Custom Protocol

Best for special requirements:
```python
from psuu.protocols import BaseProtocol

class CustomProtocol(BaseProtocol):
    def connect(self):
        ...
    
    def run_simulation(self, params):
        ...
```

## Project Structure

```
psuu/
├── frontend/         # Next.js frontend
│   ├── src/
│   │   ├── api/     # API client
│   │   ├── pages/   # React pages
│   │   └── contexts/# State management
│   └── ...
├── psuu/            # Core package
│   ├── protocols/   # Model protocols
│   ├── optimizers/  # Optimization algorithms
│   └── ...
└── template/        # Example model
    ├── model.py     # SIR model
    ├── params.py    # Parameter definitions
    └── kpi.py       # KPI calculations
