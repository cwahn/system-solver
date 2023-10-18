# system-engineering
Python system engineering library

# Usage
## Parameters
The parameters of a system shoul be expressed as a `dataclass` inheriting `SystemParam`. The members of the class could be float or `pin` `Quantity`, whihch represent physical quantity with unit. The value of each member will be used as initial guess to solve system numerically.

## Equantions, Restrictions, and Target Function
Often system engineering problem includes complex relations between parameters. Which includes equations, restrictions, and target functions to be minimized.

The `solve` method of the `SystemParam` class will take list of this functions. The key is Callable of signature `Callable[[SystemParam], Union[float, Quantitiy]]`. This functios will take parameters of the system and result a single value. 

### Equation
`Eq`, stands for equation which is concrete relation between parameters. Constructor of `Eq` will take two argugment, `lhs` and `rhs`. Each of them should be either `Callable[[SystemParam], Union[float, Quantitiy]]`, `float`, or `Quantitiy`. They will represent each side of a equation. Each side must have physically coherent units, but with exception of one side is `float`. In this case, the other side is automatically converted to magnitude.

### Constraint or Inequality
Sometimes there are conditions or inequalities that set of method should meet. They can be expressed with `Gt` and `Lt` which stands for 'Greater Than' and 'Lesser Than' respectively. Thes will take two arguments like `Eq`.

### Target Function
All the other callables with signature of `Callable[[SystemParam], Union[float, Quantitiy]]` will be treated as target functions, which should be minimized. If there are more than one target function, they will be combined to form a sigle target function in a manner of MSE(Mean Squared Error).

# Example

```python
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


```
## Result

```
Optimization terminated successfully    (Exit mode 0)
            Current function value: 14.119999999999997
            Iterations: 27
            Function evaluations: 176
            Gradient evaluations: 23
 message: Optimization terminated successfully
 success: True
  status: 0
     fun: 14.119999999999997
       x: [ 1.000e+00  5.000e-01  3.000e-01  1.800e+00  5.000e+00
            2.000e+03  1.000e+01]
     nit: 27
     jac: [       nan  0.000e+00  0.000e+00  1.800e+00  5.000e+00
            0.000e+00  0.000e+00]
    nfev: 176
    njev: 23 

payload: 1.000 kg
frame_mass: 0.500 kg
pizza_box_mass: 0.300 kg
mtow: 1.800 kg
cruising_speed: 5.000 m/s
endurance: 2000.000 s
range: 10.000 km
```

## Requirements
```
Python>=3.10
numpy
Pint==0.22
scipy==1.11.3
typing_extensions==4.8.0
```