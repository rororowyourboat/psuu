# Model Protocol Interface

The Model Protocol Interface provides a standardized way to integrate simulation models with PSUU. This approach enables more direct integration than the CLI-based approach and provides a cleaner, more robust interface.

## Protocol Hierarchy

PSUU provides two main protocol interfaces:

1. **ModelProtocol**: The base protocol for all model types
2. **CadcadModelProtocol**: A specialized protocol for cadCAD models

## The ModelProtocol Interface

The `ModelProtocol` interface defines the core methods that all model implementations should provide:

```python
class ModelProtocol(ABC):
    @abstractmethod
    def run(self, params: Dict[str, Any], **kwargs) -> Union['SimulationResults', pd.DataFrame]:
        """Run simulation with given parameters."""
        pass
    
    @abstractmethod
    def get_parameter_space(self) -> Dict[str, Union[List, Tuple, Dict]]:
        """Return the parameter space definition."""
        pass
    
    @abstractmethod
    def get_kpi_definitions(self) -> Dict[str, Union[Callable, Dict]]:
        """Return KPI calculation functions."""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate if the parameters are valid for this model."""
        # Default implementation using parameter space
        # ...
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about the model."""
        # Default implementation
        # ...
```

## The CadcadModelProtocol Interface

The `CadcadModelProtocol` extends the base protocol with cadCAD-specific functionality:

```python
class CadcadModelProtocol(ModelProtocol):
    def validate_sweep_config(self, sweep_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate cadCAD sweep configuration."""
        # Default implementation
        # ...
    
    def get_cadcad_config(self) -> Dict[str, Any]:
        """Get cadCAD configuration."""
        # This should be overridden by implementing classes
        # ...
```

## Implementing the Protocol

Here's how to implement the protocol for your own model:

```python
from psuu import CadcadModelProtocol, SimulationResults
import pandas as pd

class MyModel(CadcadModelProtocol):
    """My custom simulation model."""
    
    VERSION = "1.0.0"
    
    def __init__(self, timesteps=100, samples=1):
        """Initialize the model."""
        self.timesteps = timesteps
        self.samples = samples
    
    def run(self, params, **kwargs):
        """
        Run the simulation with given parameters.
        
        Args:
            params: Dictionary of parameter values
            **kwargs: Additional run-specific options
            
        Returns:
            SimulationResults object with simulation results
        """
        # Implement your simulation logic here
        # ...
        
        # Create a sample DataFrame
        df = pd.DataFrame({
            'timestep': range(self.timesteps),
            'value': [i * params.get('alpha', 0.5) for i in range(self.timesteps)]
        })
        
        # Calculate KPIs
        kpis = {
            'max_value': df['value'].max(),
            'total_value': df['value'].sum()
        }
        
        # Return standardized results
        return SimulationResults(
            time_series_data=df,
            kpis=kpis,
            metadata={
                'model': self.__class__.__name__,
                'version': self.VERSION,
                'timesteps': self.timesteps,
                'samples': self.samples
            },
            parameters=params
        )
    
    def get_parameter_space(self):
        """
        Return the parameter space definition.
        
        Returns:
            Dictionary mapping parameter names to their valid ranges/values
        """
        return {
            'alpha': {
                'type': 'continuous',
                'range': (0.1, 1.0),
                'description': 'Learning rate'
            },
            'beta': {
                'type': 'discrete',
                'range': [1, 2, 3, 4, 5],
                'description': 'Batch size'
            }
        }
    
    def get_kpi_definitions(self):
        """
        Return KPI calculation functions.
        
        Returns:
            Dictionary mapping KPI names to their calculation functions
        """
        return {
            'max_value': {
                'function': lambda df: df['value'].max(),
                'description': 'Maximum value',
                'tags': ['performance']
            },
            'total_value': {
                'function': lambda df: df['value'].sum(),
                'description': 'Total value',
                'tags': ['cumulative']
            }
        }
    
    def get_cadcad_config(self):
        """
        Get cadCAD configuration.
        
        Returns:
            Dictionary with cadCAD configuration
        """
        return {
            'timesteps': self.timesteps,
            'samples': self.samples,
            'model_type': self.__class__.__name__
        }
```

## Key Protocol Methods

### 1. run(params, **kwargs)

The `run` method is the core of the protocol. It takes a dictionary of parameters and returns either a `SimulationResults` object or a pandas DataFrame.

**Parameters:**
- `params`: Dictionary of parameter values
- `**kwargs`: Additional run-specific options (timesteps, samples, etc.)

**Returns:**
- `SimulationResults` object or pandas DataFrame containing simulation results

### 2. get_parameter_space()

This method defines the parameter space for your model, which is used for validation and optimization.

**Returns:**
- Dictionary mapping parameter names to their valid ranges/values
  - For continuous parameters: `(min, max)` tuples or dictionaries with 'type' and 'range'
  - For discrete parameters: lists of values or dictionaries with 'type' and 'range'

Example parameter space:
```python
{
    'alpha': (0.1, 1.0),  # Continuous parameter
    'beta': [1, 2, 3, 4, 5],  # Discrete parameter
    'gamma': {
        'type': 'continuous',
        'range': (0.01, 0.1),
        'description': 'Recovery rate'
    }
}
```

### 3. get_kpi_definitions()

This method defines the KPIs that can be calculated from the simulation results.

**Returns:**
- Dictionary mapping KPI names to either:
  - Callable functions that compute the KPI from simulation results
  - Dictionaries with 'function', 'description', and optional 'tags'

Example KPI definitions:
```python
{
    'max_value': lambda df: df['value'].max(),  # Simple function
    'total_value': {
        'function': lambda df: df['value'].sum(),
        'description': 'Total value',
        'tags': ['cumulative']
    }
}
```

### 4. validate_parameters(params)

This method validates if the given parameters are valid for the model. The default implementation checks against the parameter space, but you can override it for custom validation.

**Parameters:**
- `params`: Dictionary of parameter values to validate

**Returns:**
- Tuple of (is_valid, error_message_if_any)

### 5. get_metadata()

This method returns metadata about the model, such as name, description, and version.

**Returns:**
- Dictionary with model metadata

## Using the SimulationResults Class

The `SimulationResults` class provides a standardized container for simulation results:

```python
from psuu import SimulationResults

# Create results with time series data and KPIs
results = SimulationResults(
    time_series_data=df,  # pandas DataFrame with time series data
    kpis={                # Dictionary of KPI values
        'max_value': 100.0,
        'total_value': 5000.0
    },
    metadata={            # Metadata about the simulation
        'model': 'MyModel',
        'version': '1.0.0',
        'timesteps': 100,
        'samples': 3
    },
    parameters={          # Parameters used for this simulation
        'alpha': 0.5,
        'beta': 3
    }
)

# Accessing results
print(f"Time series data shape: {results.time_series_data.shape}")
print(f"Max value KPI: {results.kpis['max_value']}")

# Converting to DataFrame for PSUU integration
df = results.to_dataframe()

# Saving results to files
saved_files = results.save("results/my_simulation", formats=["csv", "json"])
```

## Adapting Existing Models

You can adapt existing models to use the protocol by creating wrapper classes:

```python
class ExistingModelWrapper(CadcadModelProtocol):
    def __init__(self, existing_model):
        self.model = existing_model
    
    def run(self, params, **kwargs):
        # Run the existing model
        results_df = self.model.run_simulation(params)
        
        # Convert to SimulationResults
        return SimulationResults(
            time_series_data=results_df,
            kpis=self._calculate_kpis(results_df),
            parameters=params
        )
    
    def _calculate_kpis(self, df):
        return {
            'kpi1': df['metric'].max(),
            'kpi2': df['metric'].mean()
        }
    
    def get_parameter_space(self):
        # Return parameter space from existing model or define here
        return {
            'param1': (0, 1),
            'param2': [1, 2, 3]
        }
    
    def get_kpi_definitions(self):
        return {
            'kpi1': lambda df: df['metric'].max(),
            'kpi2': lambda df: df['metric'].mean()
        }
```

## Benefits of Using the Protocol Interface

Using the protocol interface provides several benefits:

1. **Standardization**: Consistent interface for all models
2. **Self-Documentation**: Models document their own parameters and KPIs
3. **Validation**: Built-in parameter validation
4. **Direct Integration**: No need for CLI execution
5. **Flexibility**: Works with any simulation model
6. **Robust Error Handling**: Better error identification and recovery
7. **Metadata**: Additional information about the model
8. **Efficiency**: In-memory data passing instead of file I/O

The protocol interface is the recommended approach for integrating models with PSUU, especially for Python-based models where direct integration is possible.
