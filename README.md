# system-solver
Python system of equation solving & optimization library

## Usage

### System Variables
The variables of a system should be expressed as a `dataclass` inheriting from `System`. Each member of this class should be of type `Q` which represents a physical quantity with a unit and optional bounds. The initial value of each member will be used as an initial guess to solve the system numerically.

### Equations, Restrictions, and Objective Function
In system engineering problems, there often exist complex relations between variables which include equations, restrictions, and objective functions to be minimized.

The `solve` method of the `System` class will use all equations and restrictions defined within the system class, and it will attempt to minimize the provided objective function.

#### Equation
Equations represent concrete relations between variables. They should be defined as methods within the system class and decorated with the `@equation` decorator. These methods should return two values, representing the left and right hand sides of the equation.

#### Constraint or Inequality
There might be conditions or inequalities that a set of variables should meet. These can be represented as methods within the system class and decorated with the `@less_than` or `@greater_than` decorators.

#### Objective Function
The objective function is a callable with the signature `Callable[[System], Union[float, Quantity]]` that the `solve` method attempts to minimize. This function takes the system variables and returns a single value. Only one objective function can be provided for minimization.

## Example

```python
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
```
### Result

```
payload: 1.000 kg
frame_mass: 0.500 kg
pizza_box_mass: 0.300 kg
mtow: 1.800 kg
cruising_speed: 15.000 m/s
endurance: 25.000 min
range: 22.500 km 
```

## Requirements
```
Python>=3.10
numpy
Pint==0.22
scipy==1.11.3
typing_extensions==4.8.0
```
