from dataclasses import dataclass
from system_engineering.core import Q, System, equation


# State all the system variables
@dataclass
class DroneSystem(System):
    payload: Q
    frame_mass: Q
    pizza_box_mass: Q
    mtow: Q
    cruising_speed: Q
    endurance: Q
    range: Q

    # Should return lhs, rhs of a equation
    @equation
    def speed_eq(self):
        return self.cruising_speed, self.range / self.endurance

    # Should return lhs, rhs of a equation
    @equation
    def mass_eq(self):
        return self.mtow, self.payload + self.frame_mass + self.pizza_box_mass


# Initial values and optioanl bounds of variables
# Q(value: Num, units=None, min: Num = None, max: Num = None, const: bool = False)
drone_system = DroneSystem(
    payload=Q(1, "kg", const=True),
    frame_mass=Q(1, "kg", 0.5),
    pizza_box_mass=Q(0.5, "kg", 0.3),
    mtow=Q(4, "kg"),
    cruising_speed=Q(7, "m/s", 5, 15),
    endurance=Q(15, "min", 10, 25),
    range=Q(12, "km", 10),
)

# Optional objective function to minimize
solved_system, report = drone_system.solve(lambda x: x.mtow / x.range.magnitude)


print(solved_system, "\n")
print(report)
