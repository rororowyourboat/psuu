"""
Core logic module for the model.

This module contains the core state transition functions and logic for the model,
independent of cadCAD-specific implementation details.
"""

from typing import Dict, Any, Callable, List, Tuple


def update_susceptible(params, state, dt=1.0):
    """
    Update the susceptible population.
    
    Args:
        params: Model parameters
        state: Current state
        dt: Time step
        
    Returns:
        New susceptible population
    """
    S = state['susceptible']
    I = state['infected']
    N = S + I + state['recovered']
    
    beta = params['beta']
    infection_rate = beta * S * I / N
    
    new_S = S - infection_rate * dt
    return max(0, new_S)


def update_infected(params, state, dt=1.0):
    """
    Update the infected population.
    
    Args:
        params: Model parameters
        state: Current state
        dt: Time step
        
    Returns:
        New infected population
    """
    S = state['susceptible']
    I = state['infected']
    N = S + I + state['recovered']
    
    beta = params['beta']
    gamma = params['gamma']
    
    infection_rate = beta * S * I / N
    recovery_rate = gamma * I
    
    new_I = I + (infection_rate - recovery_rate) * dt
    return max(0, new_I)


def update_recovered(params, state, dt=1.0):
    """
    Update the recovered population.
    
    Args:
        params: Model parameters
        state: Current state
        dt: Time step
        
    Returns:
        New recovered population
    """
    I = state['infected']
    R = state['recovered']
    
    gamma = params['gamma']
    recovery_rate = gamma * I
    
    new_R = R + recovery_rate * dt
    return new_R


def get_state_update_functions() -> List[Callable]:
    """
    Get the list of state update functions.
    
    Returns:
        List of state update functions for cadCAD
    """
    def update_s_wrapper(params, substep, state_history, prev_state):
        new_value = update_susceptible(params, prev_state)
        return ("susceptible", new_value)  # Return a tuple as required by cadCAD
    
    def update_i_wrapper(params, substep, state_history, prev_state):
        new_value = update_infected(params, prev_state)
        return ("infected", new_value)  # Return a tuple as required by cadCAD
    
    def update_r_wrapper(params, substep, state_history, prev_state):
        new_value = update_recovered(params, prev_state)
        return ("recovered", new_value)  # Return a tuple as required by cadCAD
    
    def update_timestep(params, substep, state_history, prev_state):
        return ("timestep", prev_state['timestep'] + 1)  # Return a tuple as required by cadCAD
    
    return [update_s_wrapper, update_i_wrapper, update_r_wrapper, update_timestep]


def get_initial_state(params) -> Dict[str, Any]:
    """
    Get initial state for the simulation.
    
    Args:
        params: Model parameters
        
    Returns:
        Initial state dictionary
    """
    population = params.get('population', 1000)
    initial_infected = params.get('initial_infected', 10)
    
    return {
        'susceptible': population - initial_infected,
        'infected': initial_infected,
        'recovered': 0,
        'timestep': 0
    }
