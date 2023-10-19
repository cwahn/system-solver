from dataclasses import dataclass
from system_solver.core import Q, System, equation


# State all the system variables with initial values and optioanl bounds of variables
# Q(value: Num, units=None, min: Num = None, max: Num = None, const: bool = False)
@dataclass
class DroneSystem(System):
    payload: Q = Q(1, "kg", const=True)
    frame_mass: Q = Q(1, "kg", 0.5)
    pizza_box_mass: Q = Q(0.5, "kg", 0.3)
    mtow: Q = Q(4, "kg")
    cruising_speed: Q = Q(7, "m/s", 5, 15)
    endurance: Q = Q(15, "min", 10, 25)
    range: Q = Q(12, "km", 10)

    # Equations and inequalities should return lhs, rhs
    @equation
    def speed_eq(self):
        return self.cruising_speed, self.range / self.endurance

    @equation
    def mass_eq(self):
        return self.mtow, self.payload + self.frame_mass + self.pizza_box_mass


# Optional objective function to minimize
solved_system, _ = DroneSystem().solve(lambda x: x.mtow / x.range.magnitude)

print(solved_system)
