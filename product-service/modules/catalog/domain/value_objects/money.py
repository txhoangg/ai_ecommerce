from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = 'VND'

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        if self.amount < Decimal('0'):
            raise ValueError(f"Money amount cannot be negative: {self.amount}")

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
        result = self.amount - other.amount
        if result < Decimal('0'):
            raise ValueError("Subtraction would result in negative money")
        return Money(result, self.currency)

    def __mul__(self, factor) -> 'Money':
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __lt__(self, other: 'Money') -> bool:
        return self.amount < other.amount

    def __le__(self, other: 'Money') -> bool:
        return self.amount <= other.amount

    def __gt__(self, other: 'Money') -> bool:
        return self.amount > other.amount

    def __ge__(self, other: 'Money') -> bool:
        return self.amount >= other.amount

    def format(self) -> str:
        if self.currency == 'VND':
            return f"{int(self.amount):,}đ"
        return f"{self.amount:.2f} {self.currency}"

    @classmethod
    def from_string(cls, value: str, currency: str = 'VND') -> 'Money':
        try:
            return cls(Decimal(value), currency)
        except InvalidOperation:
            raise ValueError(f"Invalid money value: {value}")

    @classmethod
    def zero(cls, currency: str = 'VND') -> 'Money':
        return cls(Decimal('0'), currency)
