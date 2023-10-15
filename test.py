from dataclasses import dataclass
from system_engineering.core import Eq, Gt, SystemParams, Q_

@dataclass
class PizzaDroneParam(SystemParams):
    payload: Q_
    frame_mass: Q_
    pizza_box_mass: Q_
    mtow: Q_
    cruising_speed: Q_
    endurance: Q_
    range: Q_
    
initial = PizzaDroneParam(
    payload= Q_(1, "kg"), 
    frame_mass=  Q_(1, "kg"),
    pizza_box_mass= Q_(0.5, "kg"),
    mtow = Q_(4, "kg"),
    cruising_speed = Q_(5, "m/s"),
    endurance = Q_(10, "min"),
    range = Q_(10, "km"))

res, report = initial.solve(
    Eq(lambda x: x.payload , Q_(1, "kg")),
    Eq(lambda x: x.mtow, lambda x: x.payload + x.frame_mass + x.pizza_box_mass),
    Gt(lambda x: x.frame_mass, Q_(0.5, "kg")),
    Gt(lambda x: x.pizza_box_mass, Q_(0.3, "kg")),
    Gt(lambda x: x.endurance, Q_(20, "min")),
    Gt(lambda x: x.range, Q_(10, "km")),
    Eq(lambda x: x.cruising_speed , lambda x: x.range / x.endurance),
    lambda x: x.mtow
)

print(report, "\n")
print(res.to_str())