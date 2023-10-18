from dataclasses import dataclass
from system_engineering.core import Eq, Gt, Lt, System, Q


@dataclass
class DroneSystem(System):
    payload: Q
    frame_mass: Q
    pizza_box_mass: Q
    mtow: Q
    cruising_speed: Q
    endurance: Q
    range: Q


drone_instance = DroneSystem(
    payload=Q(1, "kg", const=True),
    frame_mass=Q(1, "kg", 0.5),
    pizza_box_mass=Q(0.5, "kg", 0.3),
    mtow=Q(4, "kg"),
    cruising_speed=Q(7, "m/s", 5, 10),
    endurance=Q(900, "s", 1200),
    range=Q(12, "km", 10),
)

res, report = drone_instance.solve(
    [
        Eq(lambda x: x.cruising_speed, lambda x: x.range / x.endurance),
        Eq(lambda x: x.mtow, lambda x: x.payload + x.frame_mass + x.pizza_box_mass),
        lambda x: x.mtow.magnitude,
        lambda x: x.cruising_speed.magnitude,
    ]
)

print(report, "\n")
print(res.to_str())
