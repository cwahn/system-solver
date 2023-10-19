from dataclasses import dataclass
from system_solver.core import Q, Gt, Lt, System, equation, greater_than


# State all the system variables with 
@dataclass
class DroneSystem(System):
    payload: Q
    frame_mass: Q
    pizza_box_mass: Q
    mtow: Q
    cruising_speed: Q
    endurance: Q
    range: Q

    # Equations and inequalities should return lhs, rhs
    @equation
    def speed_eq(self):
        return self.cruising_speed, self.range / self.endurance

    @equation
    def mass_eq(self):
        return self.mtow, self.payload + self.frame_mass + self.pizza_box_mass

    @greater_than
    def mtow_min(self):
        return self.mtow, Q(0, "kg")

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


# Optional objective function to minimize with extra constraints and other methods
solved_system, report = drone_system.solve(
    lambda x: x.mtow / x.range.magnitude,
    extra_constraints=[
        Gt(lambda x: x.mtow, Q(1.9, "kg")),
        Lt(lambda x: x.range, Q(22, "km")),
    ],
    method="trust-constr",
)

print(solved_system, "\n")
print(report)
