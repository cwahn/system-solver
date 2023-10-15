
from dataclasses import dataclass, fields
from typing import Any, Union, Tuple, Callable, TypeVar
from math import exp
from scipy.optimize import minimize, NonlinearConstraint
import numpy as np
from pint import Quantity

Q_ = Quantity

A = TypeVar("A")

def get_magnitude(value: Union[Quantity, float]) -> float:
    return value.magnitude if isinstance(value, Quantity) else value

class Eq:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        lhs_value = get_magnitude(self.lhs(vars) if callable(self.lhs) else self.lhs)
        rhs_value = get_magnitude(self.rhs(vars) if callable(self.rhs) else self.rhs)
        return lhs_value - rhs_value
    
class Lt:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        lhs_value = get_magnitude(self.lhs(vars) if callable(self.lhs) else self.lhs)
        rhs_value = get_magnitude(self.rhs(vars) if callable(self.rhs) else self.rhs)
        return rhs_value - lhs_value
    
class Gt:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        lhs_value = get_magnitude(self.lhs(vars) if callable(self.lhs) else self.lhs)
        rhs_value = get_magnitude(self.rhs(vars) if callable(self.rhs) else self.rhs)
        return lhs_value - rhs_value
        
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
    
    def solve(self, *fs: Tuple[Callable[['SystemParams'], float], ...]) -> 'SystemParams':
        constraints = []
        loss_functions = []

        for f in fs:
            constraint_func = lambda x, func=f: func(self.from_ndarray(x))
            
            if isinstance(f, Eq):
                constraints.append(NonlinearConstraint(constraint_func, 0, 0))
            elif isinstance(f, Gt):
                constraints.append(NonlinearConstraint(constraint_func, 0, np.inf))
            elif isinstance(f, Lt):
                constraints.append(NonlinearConstraint(constraint_func, -np.inf, 0))
            else:
                loss_functions.append(f)

        def objective(x):
            losses = [func(self.from_ndarray(x)) for func in loss_functions]
            mse = sum([loss**2 for loss in losses]) / len(losses)
            return mse

        return self.from_ndarray(
            minimize(
                objective,
                self.to_ndarray(),
                constraints=constraints,
                tol=1e-52).x)  