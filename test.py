from dataclasses import dataclass
from pint import Quantity, UnitRegistry
from system_engineering.core import Eq, Gt, SystemParams, Q_

@dataclass
class PizzaDroneParam(SystemParams):
    a: Q_
    b: Q_
    c: Q_
    
initial = PizzaDroneParam(
    Q_(2, "m"), 
    Q_(0, "m"),
    Q_(10, "sec"))

res = initial.solve(
    Eq(lambda x: x.a , Q_(2, "m")),
    Eq(lambda x: x.a + x.b, 42),
    Gt(lambda x: x.c, 11),
    lambda x: x.a.magnitude + x.b.magnitude + x.c.magnitude
)

print(res)