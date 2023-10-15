from dataclasses import dataclass, fields
from typing import Callable, Self, Union
import numpy as np
from pint import Quantity, UnitRegistry
from scipy.optimize import minimize

from system_engineering.core import Eq, Mse, SystemParams

ureg = UnitRegistry()
Q = Quantity

def get_magnitude(value: Union[Quantity, float]) -> float:
    return value.magnitude if isinstance(value, Quantity) else value

@dataclass
class PizzaDroneParam(SystemParams):
    a: Q
    b: Q
    
initial = PizzaDroneParam(2 * ureg.meter, 0 * ureg.meter)

res = initial.solve(
    Mse(
    Eq(lambda x: x.a , 2 * ureg.meter),
    Eq(lambda x: x.a + x.b, 42)
    ))

print(res)