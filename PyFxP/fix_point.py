import warnings

from .registry import Registry, OppType


class FixedPoint:
    """
    FixedPoint represents a value using a Qm.n fixed-point format.

    :param val: Value to initialise with. Can be:
        - float: interpreted as a real number
        - int: raw fixed-point integer representation
        - str: binary string representing fixed-point bit pattern
    :param int_width: Number of integer bits (not including sign)
    :param fract_width: Number of fractional bits
    :param signed: Whether the value is signed (two's complement)
    """

    def __init__(self, val: int | float | str, int_width: int, fract_width: int, signed: bool = False):
        """ FixedPoint class construtor """

        self._int_width: int = int_width
        self._fract_width: int = fract_width
        self._total_width: int = int_width + fract_width + (1 if signed else 0)
        self._signed: bool = signed

        # Define bounds set by Qm.n scheme
        self._min_val = -(1 << (self._total_width - 1)) if signed else 0
        self._max_val = (1 << (self._total_width - 1)) - 1 if signed else (1 << self._total_width) - 1

        # Convert input value to raw integer representation
        match val:
            case int():
                raw_int_val = val

            case float():
                raw_int_val = round(val * (1 << self._fract_width))

            case str():
                raw_int_val = self._bin_to_int(val)
                
            case _:
                raise TypeError("Value must be float, int, or binary str")
            
        # Clip true integer value to range defined by Qm.n scheme
        if raw_int_val > self._max_val:
            warnings.warn(f"Overflow: Value {raw_int_val} exceeds maximum {self._max_val} and will be clipped", RuntimeWarning)
            self._val_int = self._max_val
        elif raw_int_val < self._min_val:
            warnings.warn(f"Underflow: Value {raw_int_val} below minimum {self._min_val} and will be clipped", RuntimeWarning)
            self._val_int = self._min_val
        else:
            self._val_int = raw_int_val

        # Define float and binary bit string representations
        self._val_float = self._int_to_float(self._val_int)
        self._val_bin = self._int_to_bin(self._val_int)

        # Log creation of var
        Registry.log_var(fxp=self)
        
    @property
    def val_float(self) -> float:
        return self._val_float

    @property
    def val_int(self) -> int:
        return self._val_int

    @property
    def val_bin(self) -> str:
        return self._val_bin

    @property
    def int_width(self) -> int:
        return self._int_width

    @property
    def fract_width(self) -> int:
        return self._fract_width
    
    @property
    def total_width(self) -> int:
        return self._total_width

    @property
    def signed(self) -> bool:
        return self._signed

    def _int_to_float(self, val_int: int) -> float:
        """
        Convert internal integer representation to float using Qm.n format.
        Handles sign-extension for signed numbers.
        """
        if self._signed:
            if val_int > self._max_val:
                val_int -= 1 << self._total_width  # two's complement
        return val_int / (1 << self._fract_width)

    def _int_to_bin(self, val_int: int) -> str:
        """
        Convert fixed-point integer to binary string of length `total_width`.
        """
        mask = (1 << self._total_width) - 1
        return format(val_int & mask, f"0{self._total_width}b")

    def _bin_to_int(self, val_bin: str) -> int:
        """
        Convert binary string to fixed-point integer.
        Handles sign extension if needed.
        """
        if len(val_bin) != self._total_width:
            raise ValueError(f"Binary string must be {self._total_width} bits")
        raw = int(val_bin, 2)
        if self._signed and val_bin[0] == '1':
            # Negative in two's complement
            raw -= 1 << self._total_width
        return raw

    def __add__(self, other: "FixedPoint") -> "FixedPoint":
        """
        Add two FixedPoint numbers and return a new FixedPoint result.
        The result uses Q(m+1).n format to avoid overflow.
        """
        if not isinstance(other, FixedPoint):
            raise TypeError("Can only add FixedPoint to FixedPoint")

        if self._fract_width != other.fract_width:
            raise ValueError("Fractional widths must match for addition")

        result_signed = self._signed or other.signed
        result_fract = self._fract_width
        result_int = max(self._int_width + self._signed, other.int_width + other.signed) + 1

        result_val : int = self._val_int + other.val_int

        result = FixedPoint(val=result_val, int_width=result_int - int(result_signed), fract_width=result_fract, signed=result_signed)

        Registry.log_op(lhs=self, rhs=other, result=result, opp_type=OppType.__ADD__)

        return result

    def __sub__(self, other: "FixedPoint") -> "FixedPoint":
        """
        Subtract two FixedPoint numbers and return a new FixedPoint result.
        The result uses Q(m+1).n format to avoid overflow.
        """
        if not isinstance(other, FixedPoint):
            raise TypeError("Can only subtract FixedPoint from FixedPoint")

        if self._fract_width != other.fract_width:
            raise ValueError("Fractional widths must match for subtraction")

        result_signed = self._signed or other.signed
        result_fract = self._fract_width
        result_int = max(self._int_width, other.int_width) + 1

        result_val : int = self._val_int - other.val_int

        result = FixedPoint(val=result_val, int_width=result_int, fract_width=result_fract, signed=result_signed)

        Registry.log_op(lhs=self, rhs=other, result=result, opp_type=OppType.__SUB__)

        return result

    def __mul__(self, other: "FixedPoint") -> "FixedPoint":
        """
        Multiply two FixedPoint numbers and return a new FixedPoint result.
        An unsigned result uses Q(m1 + m2).(n1 + n2) format.
        A signed result uses Q(m1 + m2 + 1).(n1 + n2) format.
        """
        if not isinstance(other, FixedPoint):
            raise TypeError("Can only multiply FixedPoint by FixedPoint")

        result_signed = self._signed or other.signed
        result_int = self._int_width + other.int_width + int(self._signed and other.signed)
        result_fract = self._fract_width + other.fract_width

        result_val = self._val_int * other.val_int

        result = FixedPoint(val=result_val, int_width=result_int, fract_width=result_fract, signed=result_signed)

        Registry.log_op(lhs=self, rhs=other, result=result, opp_type=OppType.__MUL__)

        return result
