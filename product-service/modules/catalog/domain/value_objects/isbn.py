import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ISBN:
    value: str

    def __post_init__(self):
        cleaned = self._clean(self.value)
        object.__setattr__(self, 'value', cleaned)
        if cleaned and not self._is_valid(cleaned):
            raise ValueError(f"Invalid ISBN: {self.value}")

    @staticmethod
    def _clean(value: str) -> str:
        return re.sub(r'[-\s]', '', value).upper()

    @staticmethod
    def _is_valid(value: str) -> bool:
        if len(value) == 10:
            return ISBN._validate_isbn10(value)
        elif len(value) == 13:
            return ISBN._validate_isbn13(value)
        return False

    @staticmethod
    def _validate_isbn10(value: str) -> bool:
        if not re.match(r'^\d{9}[\dX]$', value):
            return False
        total = 0
        for i, char in enumerate(value):
            if char == 'X':
                digit = 10
            else:
                digit = int(char)
            total += digit * (10 - i)
        return total % 11 == 0

    @staticmethod
    def _validate_isbn13(value: str) -> bool:
        if not re.match(r'^\d{13}$', value):
            return False
        total = 0
        for i, char in enumerate(value):
            digit = int(char)
            if i % 2 == 0:
                total += digit
            else:
                total += digit * 3
        return total % 10 == 0

    def is_isbn10(self) -> bool:
        return len(self.value) == 10

    def is_isbn13(self) -> bool:
        return len(self.value) == 13

    def to_isbn13(self) -> 'ISBN':
        if self.is_isbn13():
            return self
        if not self.is_isbn10():
            raise ValueError("Cannot convert non-ISBN10 to ISBN13")
        base = '978' + self.value[:-1]
        total = 0
        for i, char in enumerate(base):
            digit = int(char)
            total += digit if i % 2 == 0 else digit * 3
        check = (10 - (total % 10)) % 10
        return ISBN(base + str(check))

    def __str__(self) -> str:
        return self.value

    @classmethod
    def empty(cls) -> 'ISBN':
        instance = object.__new__(cls)
        object.__setattr__(instance, 'value', '')
        return instance
