
from typing import Any, Union, Tuple, Callable, TypeVar
from math import exp
from webbrowser import Opera

import numpy as np
from pint import Quantity

A = TypeVar("A")

class Eq:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        # If lhs is callable, call it with A; otherwise, use its value directly
        lhs_value = self.lhs(vars) if callable(self.lhs) else self.lhs
        rhs_value = self.rhs(vars) if callable(self.rhs) else self.rhs
        
        return exp(0.2 * abs(lhs_value - rhs_value)) - 1
    
class Lt:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        # If lhs is callable, call it with A; otherwise, use its value directly
        lhs_value = self.lhs(vars) if callable(self.lhs) else self.lhs
        rhs_value = self.rhs(vars) if callable(self.rhs) else self.rhs
        
        return exp(0.2 * abs(lhs_value - rhs_value)) - 1 if lhs_value > rhs_value else 0
    
class Gt:
    def __init__(self,  
                 lhs: Union[Callable[[A], float], Union[Quantity, float]], 
                 rhs: Union[Callable[[A], float], Union[Quantity, float]]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> float:
        # If lhs is callable, call it with A; otherwise, use its value directly
        lhs_value = self.lhs(vars) if callable(self.lhs) else self.lhs
        rhs_value = self.rhs(vars) if callable(self.rhs) else self.rhs
        
        return exp(0.2 * abs(lhs_value - rhs_value)) - 1 if lhs_value < rhs_value else 0
        
class Mse:
    def __init__(self, *fs: Tuple[Callable[[A], float], ...]) -> None:
        self.fs = fs

    def __call__(self, vars: A) -> float:
        squared_loss = [f(vars) ** 2 for f in self.fs]
        return sum(squared_loss) / len(squared_loss)