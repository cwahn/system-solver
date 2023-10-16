# system-engineering
Python system engineering library

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
