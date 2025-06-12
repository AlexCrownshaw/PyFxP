from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fix_point import FixedPoint


class OppType(Enum):
    __ADD__ = 0
    __SUB__ = 1
    __MUL__ = 2
    

@dataclass
class Opp:
    lhs: "FixedPoint"
    rhs: "FixedPoint"
    result: "FixedPoint"
    opp_type: OppType


class Registry:

    var_registry : list["FixedPoint"] = []
    op_registry : list[Opp] = []

    @classmethod
    def log_var(cls, fxp : "FixedPoint") -> None:
        cls.var_registry.append(fxp)

    @classmethod
    def log_op(cls, lhs : "FixedPoint", rhs: "FixedPoint", result : "FixedPoint", opp_type: OppType) -> None:
        cls.op_registry.append(Opp(lhs=lhs, rhs=rhs, result=result, opp_type=opp_type))
