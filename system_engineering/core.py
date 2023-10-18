from dataclasses import dataclass, fields
import inspect
from typing import Any, List, Union, Tuple, Callable, TypeVar
from math import exp
from scipy.optimize import minimize, NonlinearConstraint
import numpy as np
from pint import Quantity

Q_ = Quantity
A = TypeVar("A")
Num = Union[int, float]


class Q(Q_):
    def __new__(
        cls,
        value: Num,
        units=None,
        min: Num = None,
        max: Num = None,
        const: bool = False,
        **kwargs,
    ):
        instance = super(Q, cls).__new__(cls, value, units)
        instance.min = min if const == False else value
        instance.max = max if const == False else value
        return instance

    def bound(self) -> tuple[Q_, Q_]:
        return (self.min, self.max)


def _magnitude(value: Union[Q, Num]) -> Num:
    return value.magnitude if isinstance(value, Q) else value


def _is_quantity(value: Union[Q, Num]) -> bool:
    return isinstance(value, Q_)


def _assert_dimensionality(lhs: Union[Q, Num], rhs: Union[Q, Num]):
    if _is_quantity(lhs) and _is_quantity(rhs):
        if lhs.dimensionality != rhs.dimensionality:
            raise ValueError("The quantities don't have the same dimensionality.")


class Eq:
    def __init__(
        self,
        lhs: Union[Callable[[A], Num], Union[Q, Num]],
        rhs: Union[Callable[[A], Num], Union[Q, Num]] = 0,
    ) -> None:
        _assert_dimensionality(lhs, rhs)
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> Num:
        lhs_ = self.lhs(vars) if callable(self.lhs) else self.lhs
        rhs_ = self.rhs(vars) if callable(self.rhs) else self.rhs
        return _magnitude(lhs_ - rhs_)


class Lt:
    def __init__(
        self,
        lhs: Union[Callable[[A], Num], Union[Q, Num]],
        rhs: Union[Callable[[A], Num], Union[Q, Num]],
    ) -> None:
        _assert_dimensionality(lhs, rhs)
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> Num:
        lhs_ = self.lhs(vars) if callable(self.lhs) else self.lhs
        rhs_ = self.rhs(vars) if callable(self.rhs) else self.rhs
        return _magnitude(lhs_ - rhs_)


class Gt:
    def __init__(
        self,
        lhs: Union[Callable[[A], Num], Union[Q, Num]],
        rhs: Union[Callable[[A], Num], Union[Q, Num]],
    ) -> None:
        _assert_dimensionality(lhs, rhs)
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, vars: A) -> Num:
        lhs_ = self.lhs(vars) if callable(self.lhs) else self.lhs
        rhs_ = self.rhs(vars) if callable(self.rhs) else self.rhs
        return _magnitude(lhs_ - rhs_)


# Constraint method decorator
def equation(func):
    def wrapper(self, other):
        lhs, rhs = func(other)
        return _magnitude(lhs - rhs)

    wrapper.constraint_type = "equation"
    return wrapper


# Constraint method decorator
def less_than(func):
    def wrapper(self, other):
        lhs, rhs = func(other)
        return _magnitude(lhs - rhs)

    wrapper.constraint_type = "less_than"
    return wrapper


# Constraint method decorator
def greater_than(func):
    def wrapper(self, other):
        lhs, rhs = func(other)
        return _magnitude(lhs - rhs)

    wrapper.constraint_type = "greater_than"
    return wrapper


@dataclass
class System:
    def to_ndarray(self):
        arr = []
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, Q_):
                arr.append(value.magnitude)
            else:
                arr.append(value)
        return np.array(arr).flatten()

    def from_ndarray(self, values: np.ndarray) -> "System":
        quantities = {
            field.name: (
                Q(value, getattr(self, field.name).units)
                if isinstance(getattr(self, field.name), Q_)
                else value
            )
            for value, field in zip(values, fields(self))
        }
        return type(self)(**quantities)

    def _get_constraints(self):
        constraints = []
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "constraint_type"):
                wrapped_constraint = lambda x, m=method: m(self.from_ndarray(x))

                match method.constraint_type:
                    case "equation":
                        constraints.append(
                            NonlinearConstraint(wrapped_constraint, 0, 0)
                        )
                    case "less_than":
                        constraints.append(
                            NonlinearConstraint(wrapped_constraint, -np.inf, 0)
                        )
                    case "greater_than":
                        constraints.append(
                            NonlinearConstraint(wrapped_constraint, 0, np.inf)
                        )
        return constraints

    def solve(
        self,
        objective_funcs: Callable[["System"], Num] | None = None,
        extra_constraints: List[Callable[["System"], Num]] = [],
    ) -> Tuple["System", str]:
        objective = (
            (lambda x: _magnitude(objective_funcs(self.from_ndarray(x))))
            if not objective_funcs == None
            else (lambda x: 0.0)
        )

        constraints = self._get_constraints()

        bounds = [getattr(self, field.name).bound() for field in fields(self)]

        for f in extra_constraints:
            wrapped_constraint = lambda x, func=f: func(self.from_ndarray(x))

            if isinstance(f, Eq):
                constraints.append(NonlinearConstraint(wrapped_constraint, 0, 0))
            elif isinstance(f, Lt):
                constraints.append(NonlinearConstraint(wrapped_constraint, -np.inf, 0))
            elif isinstance(f, Gt):
                constraints.append(NonlinearConstraint(wrapped_constraint, 0, np.inf))

        result = minimize(
            objective,
            self.to_ndarray(),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            tol=1e-15,
            options={"maxiter": 1000, "disp": False},
        )

        return self.from_ndarray(result.x), result

    def __str__(self) -> str:
        output = []
        for field, value in self.__dict__.items():
            if isinstance(value, Q_):
                formatted_value = "{:.3f~P}".format(value)
                output.append(f"{field}: {formatted_value}")
            else:
                output.append(f"{field}: {value:.3f}")
        return "\n".join(output)
