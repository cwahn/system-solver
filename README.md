# system-engineering
Python system engineering library

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


# Initial value and bound of variables
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
system_solution, report = drone_system.solve(lambda x: x.mtow / x.range.magnitude)


print(system_solution, "\n")
print(report)


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

 message: Optimization terminated successfully
 success: True
  status: 0
     fun: 0.07999999999999997
       x: [ 1.000e+00  5.000e-01  3.000e-01  1.800e+00  1.500e+01
            2.500e+01  2.250e+01]
     nit: 28
     jac: [       nan  0.000e+00  0.000e+00  4.444e-02 -0.000e+00
           -0.000e+00 -3.556e-03]
    nfev: 172
    njev: 24
```

## Requirements
```
Python>=3.10
numpy
Pint==0.22
scipy==1.11.3
typing_extensions==4.8.0
```