
from dataclasses import dataclass, fields
from typing import Any, Self, Union, Tuple, Callable, TypeVar
from math import exp
from scipy.optimize import minimize
import numpy as np
from pint import Quantity

def get_magnitude(value: Union[Quantity, float]) -> float:
    return value.magnitude if isinstance(value, Quantity) else value

A = TypeVar("A")

class Eq:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        # If lhs is callable, call it with A; otherwise, use its value directly
        lhs_value = get_magnitude(self.lhs(vars) if callable(self.lhs) else self.lhs)
        rhs_value = get_magnitude(self.rhs(vars) if callable(self.rhs) else self.rhs)
        
        return exp(0.2 * abs(lhs_value - rhs_value)) - 1
    
class Lt:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        # If lhs is callable, call it with A; otherwise, use its value directly
        lhs_value = get_magnitude(self.lhs(vars) if callable(self.lhs) else self.lhs)
        rhs_value = get_magnitude(self.rhs(vars) if callable(self.rhs) else self.rhs)
        
        return exp(0.2 * abs(lhs_value - rhs_value)) - 1 if lhs_value > rhs_value else 0
    
class Gt:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        # If lhs is callable, call it with A; otherwise, use its value directly
        lhs_value = get_magnitude(self.lhs(vars) if callable(self.lhs) else self.lhs)
        rhs_value = get_magnitude(self.rhs(vars) if callable(self.rhs) else self.rhs)
        
        return exp(0.2 * abs(lhs_value - rhs_value)) - 1 if lhs_value < rhs_value else 0
        
class Mse:
    def __init__(self, *fs: Tuple[Callable[[A], float], ...]) -> None:
        self.fs = fs

    def __call__(self, vars: A) -> float:
        squared_loss = [f(vars) ** 2 for f in self.fs]
        return sum(squared_loss) / len(squared_loss)

@dataclass
class SystemParams:
    def to_ndarray(self):
        return np.array([get_magnitude(getattr(self, field.name)) for field in fields(self)]).flatten()
    
    def from_ndarray(self, values: np.ndarray) -> 'SystemParams':
        quantities = {
            field.name: 
            (Quantity(value, getattr(self, field.name).units) if isinstance(getattr(self, field.name), Quantity) else value) for value, field in zip(values, fields(self))
        }
        return type(self)(**quantities)
    
    def solve(self, f: Callable[['SystemParams'], float]) -> 'SystemParams':
        return self.from_ndarray(
            minimize(
                lambda x: f(self.from_ndarray(x)),
                  self.to_ndarray(),
                  tol=1e-9).x) 