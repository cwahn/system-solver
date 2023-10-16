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
from system_engineering.core import Eq, Gt, SystemParams, Q_

# Specified values are initial value of numeric optimization
@dataclass
class PizzaDroneParams(SystemParams):
    payload: Q_ = Q_(1, "kg")
    frame_mass: Q_ =  Q_(1, "kg")
    pizza_box_mass: Q_ = Q_(0.5, "kg")
    mtow: Q_ = Q_(4, "kg")
    cruising_speed: Q_ = Q_(5, "m/s")
    endurance: Q_ = Q_(10, "min")
    range: Q_ = Q_(10, "km")

res, report = PizzaDroneParams().solve(
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

```
## Result

```
Optimization terminated successfully    (Exit mode 0)
            Current function value: 3.2399999999999913
            Iterations: 10
            Function evaluations: 55
            Gradient evaluations: 6
 message: Optimization terminated successfully
 success: True
  status: 0
     fun: 3.2399999999999913
       x: [ 1.000e+00  5.000e-01  3.000e-01  1.800e+00  5.235e-01
            2.000e+01  1.047e+01]
     nit: 10
     jac: [ 0.000e+00  0.000e+00  0.000e+00  3.600e+00  0.000e+00
            0.000e+00  0.000e+00]
    nfev: 55
    njev: 6 

payload: 1.000 kg
frame_mass: 0.500 kg
pizza_box_mass: 0.300 kg
mtow: 1.800 kg
cruising_speed: 0.524 m/s
endurance: 20.000 min
range: 10.471 km
```

## Requirements
```
Python>=3.10
numpy
Pint==0.22
scipy==1.11.3
typing_extensions==4.8.0
```