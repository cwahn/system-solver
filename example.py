from dataclasses import dataclass
from system_engineering.core import Q, System, equation


@dataclass
class DroneSystem(System):
    payload: Q
    frame_mass: Q
    pizza_box_mass: Q
    mtow: Q
    cruising_speed: Q
    endurance: Q
    range: Q

    @equation
    def speed_eq(self):
        return self.cruising_speed, self.range / self.endurance

    @equation
    def mass_eq(self):
        return self.mtow, self.payload + self.frame_mass + self.pizza_box_mass


drone_instance = DroneSystem(
    payload=Q(1, "kg", const=True),
    frame_mass=Q(1, "kg", 0.5),
    pizza_box_mass=Q(0.5, "kg", 0.3),
    mtow=Q(4, "kg"),
    cruising_speed=Q(7, "m/s", 5, 15),
    endurance=Q(15, "min", 10, 25),
    range=Q(12, "km", 10),
)

res, report = drone_instance.solve(
    [
        lambda x: x.mtow.magnitude,
        lambda x: 1 / x.range.magnitude,
    ]
)

print(report, "\n")
print(res.to_str())