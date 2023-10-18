from dataclasses import dataclass, fields
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
        return lhs_ - rhs_


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
        return lhs_ - rhs_


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
        return lhs_ - rhs_


@dataclass
class System:
    # def __post_init__(self):
    #     for field in fields(self):
    #         value = getattr(self, field.name)
    #         if isinstance(value, (int, Num)) and isinstance(field.type, str):
    #             setattr(self, field.name, Q(value, field.type))

    def to_ndarray(self):
        arr = []
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, Q):
                arr.append(value.magnitude)
            else:
                arr.append(value)
        return np.array(arr).flatten()

    def from_ndarray(self, values: np.ndarray) -> "System":
        quantities = {
            field.name: (
                Q(value, getattr(self, field.name).units)
                if isinstance(getattr(self, field.name), Q)
                else value
            )
            for value, field in zip(values, fields(self))
        }
        return type(self)(**quantities)

    def solve(self, fs: List[Callable[["System"], Num]]) -> "System":
        constraints = []
        loss_fs = []

        for f in fs:
            constraint_func = lambda x, func=f: func(self.from_ndarray(x))

            if isinstance(f, Eq):
                constraints.append(NonlinearConstraint(constraint_func, 0, 0))
            elif isinstance(f, Lt):
                constraints.append(NonlinearConstraint(constraint_func, -np.inf, 0))
            elif isinstance(f, Gt):
                constraints.append(NonlinearConstraint(constraint_func, 0, np.inf))
            else:
                loss_fs.append(f)

        bounds = [getattr(self, field.name).bound() for field in fields(self)]

        def objective(x):
            squared_losses = [loss_f(self.from_ndarray(x)) ** 2 for loss_f in loss_fs]
            return sum(squared_losses) / len(squared_losses)

        result = minimize(
            objective,
            self.to_ndarray(),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            tol=1e-15,
            options={"maxiter": 1000, "disp": True},
        )

        return self.from_ndarray(result.x), result

    def to_str(self) -> str:
        output = []
        for field, value in self.__dict__.items():
            if isinstance(value, Q):
                formatted_value = "{:.3f~P}".format(value)
                output.append(f"{field}: {formatted_value}")
            else:
                output.append(f"{field}: {value:.3f}")
        return "\n".join(output)
