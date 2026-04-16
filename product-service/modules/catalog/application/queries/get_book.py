from dataclasses import dataclass


@dataclass
class GetBookQuery:
    book_id: int
    active_only: bool = True
