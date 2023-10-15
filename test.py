from dataclasses import dataclass, fields
from typing import Callable, Self, Union
import numpy as np
from pint import Quantity, UnitRegistry
from scipy.optimize import minimize

from system_engineering.core import Eq, Mse

ureg = UnitRegistry
Q = Quantity

def get_magnitude(value: Union[Quantity, float]) -> float:
    return value.magnitude if isinstance(value, Quantity) else value

@dataclass
class PizzaDroneParam:
    a: Q
    b: Q

    def to_ndarray(self):
        return np.array([get_magnitude(getattr(self, field.name)) for field in fields(self)]).flatten()
    
    def from_ndarray(self, values: np.ndarray) -> Self:
        quantities = {
            field.name: 
            (Q(value, getattr(self, field.name).units) if isinstance(getattr(self, field.name), Quantity) else value ) for value, field in zip(values, fields(self))}
        return PizzaDroneParam(**quantities)
    
    def design(self, f: Callable[[Self], float]) -> Self:
        return self.from_ndarray(
            minimize(
                lambda x: f(self.from_ndarray(x)),
                  self.to_ndarray(),
                  tol=1e-9).x)
    
initial = PizzaDroneParam(2, 0)

res = initial.design(Mse(
    Eq(lambda x: x.a , 2),
    Eq(lambda x: x.a + x.b, 42)
    ))

print(res)