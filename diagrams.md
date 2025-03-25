# PSUU Software Architecture Diagrams

This document outlines the architecture of PSUU (Parameter Selection Under Uncertainty) and its integration with cadCAD using Mermaid diagrams.

## Table of Contents

1. [Overview: PSUU Architecture](#overview-psuu-architecture)
2. [Integration Patterns: Protocol vs CLI](#integration-patterns)
3. [PSUU-cadCAD Integration Flow](#psuu-cadcad-integration-flow)
4. [Configuration and Experiment Workflow](#configuration-and-experiment-workflow)
5. [Command Line Interface Structure](#command-line-interface-structure)

## Overview: PSUU Architecture

```mermaid
graph TD
    User(User)
    subgraph "PSUU"
        CLI[CLI Interface]
        Config[Configuration Manager]
        Experiment[Experiment Controller]
        Optimizer[Optimization Algorithms]
        Connector[Simulation Connector]
        Protocol[Model Protocol]
        KPI[KPI Calculator]
        Results[Results Aggregator]
    end
    subgraph "Integration Options"
        ModelImpl[Model Implementation]
        CLITool[CLI-based Simulation]
    end
    
    User --> CLI
    User --> Config
    CLI --> Experiment
    Config --> Experiment
    
    Experiment --> Optimizer
    Experiment --> Connector
    Experiment --> Protocol
    Experiment --> KPI
    Experiment --> Results
    
    Protocol --> ModelImpl
    Connector --> CLITool
    
    class Optimizer,Protocol,Connector highlight
    class ModelImpl,CLITool external
```

## Integration Patterns

PSUU provides two main ways to connect with simulation models:

```mermaid
graph LR
    subgraph "PSUU"
        Experiment[PsuuExperiment]
    end
    
    subgraph "Protocol Integration"
        ModelProtocol[ModelProtocol]
        CadcadProtocol[CadcadModelProtocol]
        ModelImpl[Custom Model Implementation]
        
        ModelProtocol --- CadcadProtocol
        CadcadProtocol --- ModelImpl
    end
    
    subgraph "CLI Integration"
        SimConnector[SimulationConnector]
        CadcadConnector[CadcadSimulationConnector]
        CLITool[CLI-based Simulation]
        
        SimConnector --- CadcadConnector
        CadcadConnector --- CLITool
    end
    
    Experiment --> ModelProtocol
    Experiment --> SimConnector
    
    class ModelProtocol,SimConnector,CadcadProtocol,CadcadConnector highlight
    class ModelImpl,CLITool external
```

## PSUU-cadCAD Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant PSUU as PSUU Experiment
    participant Optimizer
    participant Connector as CadcadConnector
    participant cadCAD as cadCAD Model
    
    User->>PSUU: Configure experiment
    User->>PSUU: Set parameters & KPIs
    User->>PSUU: Run optimization
    
    loop Until optimization complete
        PSUU->>Optimizer: Request parameters
        Optimizer-->>PSUU: Suggested parameters
        
        alt Protocol Integration
            PSUU->>cadCAD: model.run(parameters)
            cadCAD->>cadCAD: Execute simulation
            cadCAD-->>PSUU: Return SimulationResults
        else CLI Integration
            PSUU->>Connector: run_simulation(parameters)
            Connector->>cadCAD: Execute CLI command
            cadCAD->>cadCAD: Run simulation
            cadCAD-->>Connector: Write output files
            Connector->>Connector: Parse output files
            Connector-->>PSUU: Return DataFrame results
        end
        
        PSUU->>PSUU: Calculate KPIs
        PSUU->>Optimizer: Update with KPI values
    end
    
    PSUU-->>User: Return best parameters and KPIs
```

## Configuration and Experiment Workflow

```mermaid
flowchart TD
    Start([Start])
    LoadConfig[Load Configuration]
    ValidateConfig[Validate Configuration]
    SetupExp[Setup Experiment]
    SetupParams[Setup Parameter Space]
    SetupKPIs[Setup KPIs]
    SetupOpt[Setup Optimizer]
    RunExp[Run Experiment]
    Results[Process Results]
    End([End])
    
    Start --> LoadConfig
    LoadConfig --> ValidateConfig
    
    ValidateConfig -->|Valid| SetupExp
    ValidateConfig -->|Invalid| Error1[Raise ConfigurationError]
    
    SetupExp --> SetupParams
    SetupParams --> SetupKPIs
    SetupKPIs --> SetupOpt
    
    SetupOpt --> RunExp
    
    RunExp -->|Success| Results
    RunExp -->|Error| Error2[Handle Errors]
    
    Results --> End
    Error1 --> End
    Error2 --> End
    
    subgraph "YAML Configuration File"
        YAML[("
        model:
          class: 'model.SIRModel'
          protocol: 'cadcad'
          
        parameters:
          beta: {type: continuous, min: 0.1, max: 0.5}
          
        kpis:
          peak_infected: {objective: minimize}
          
        optimization:
          algorithm: 'bayesian'
          iterations: 30
        ")]
    end
    
    YAML -.-> LoadConfig
```

## Command Line Interface Structure

```mermaid
graph TD
    cli[psuu]
    
    cli --> init[init: Create config file]
    cli --> add_param[add-param: Add parameter]
    cli --> add_kpi[add-kpi: Add KPI]
    cli --> set_opt[set-optimizer: Configure optimizer]
    cli --> run[run: Run experiment]
    cli --> clone[clone-model: Clone model template]
    cli --> list[list-models: List available models]
    
    clone --> ModelRepo[(Model Repository)]
    
    run --> exp[PsuuExperiment]
    exp --> CLIMode[CLI Integration]
    exp --> ProtocolMode[Protocol Integration]
    
    CLIMode --> CadcadCLI[CadcadSimulationConnector]
    ProtocolMode --> CadcadProtocol[CadcadModelProtocol]
    
    CadcadCLI --> CadcadRun[cadCAD CLI Execution]
    CadcadProtocol --> CadcadModel[cadCAD Model Class]
```

## Class Structure for Model Protocol

```mermaid
classDiagram
    class ModelProtocol {
        <<abstract>>
        +run(params: Dict) SimulationResults
        +get_parameter_space() Dict
        +get_kpi_definitions() Dict
        +validate_parameters(params: Dict) Tuple
        +get_metadata() Dict
    }
    
    class CadcadModelProtocol {
        <<abstract>>
        +run(params: Dict) SimulationResults
        +get_parameter_space() Dict
        +get_kpi_definitions() Dict
        +get_cadcad_config() Dict
        +get_initial_state() Dict
        +validate_params(params: Dict) Tuple
    }
    
    class PsuuExperiment {
        -integration_mode: str
        -model: ModelProtocol
        -simulation_connector: SimulationConnector
        -parameter_space: Dict
        -kpi_calculator: KPICalculator
        -data_aggregator: DataAggregator
        -optimizer: Optimizer
        -objective_name: str
        -maximize: bool
        +add_kpi(name, function, column, operation)
        +set_parameter_space(parameter_space)
        +set_optimizer(method, objective_name, maximize)
        +run(max_iterations, verbose, save_results) ExperimentResults
    }
    
    class SimulationConnector {
        +command: str
        +param_format: str
        +output_format: str
        +output_file: str
        +working_dir: str
        +run_simulation(parameters: Dict) DataFrame
        #_build_command(parameters: Dict) str
    }
    
    class CadcadSimulationConnector {
        +run_simulation(parameters: Dict) DataFrame
    }
    
    ModelProtocol <|-- CadcadModelProtocol
    SimulationConnector <|-- CadcadSimulationConnector
    
    PsuuExperiment --> ModelProtocol : uses
    PsuuExperiment --> SimulationConnector : uses
```

## Data Flow for cadCAD Integration

```mermaid
graph TD
    subgraph "User Input"
        Config[YAML Configuration]
        CLIParams[CLI Parameters]
    end
    
    subgraph "PSUU System"
        ExpSetup[Experiment Setup]
        ExpRunner[Experiment Runner]
        Optimizer[Optimization Algorithm]
        
        DataAgg[Data Aggregator]
        KPICalc[KPI Calculator]
        Results[Results Processing]
    end
    
    subgraph "Simulation Interface"
        ProtocolInterface[Protocol Interface]
        CLIInterface[CLI Interface]
    end
    
    subgraph "cadCAD"
        ModelLogic[Model Logic]
        StateVars[State Variables]
        Policies[Policy Functions]
        Mechanisms[State Update Functions]
        Execution[Simulation Execution]
        DataCollection[Data Collection]
    end
    
    Config --> ExpSetup
    CLIParams --> ExpSetup
    
    ExpSetup --> ExpRunner
    ExpRunner --> Optimizer
    Optimizer --> |Parameter Sets| ExpRunner
    
    ExpRunner --> |Parameters| ProtocolInterface
    ExpRunner --> |Parameters| CLIInterface
    
    ProtocolInterface --> ModelLogic
    CLIInterface --> Execution
    
    ModelLogic --> StateVars
    ModelLogic --> Policies
    ModelLogic --> Mechanisms
    ModelLogic --> Execution
    
    Execution --> DataCollection
    
    DataCollection --> |Results| ProtocolInterface
    DataCollection --> |Output Files| CLIInterface
    
    ProtocolInterface --> |SimulationResults| ExpRunner
    CLIInterface --> |Parsed DataFrame| ExpRunner
    
    ExpRunner --> DataAgg
    DataAgg --> KPICalc
    KPICalc --> Results
    Results --> |Feedback| Optimizer
    
    class Config,CLIParams highlight
    class ProtocolInterface,CLIInterface,ModelLogic,Execution emphasis
```
