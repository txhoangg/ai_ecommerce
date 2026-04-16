class ProductServiceException(Exception):
    """Base exception for product service."""
    pass


class BookNotFoundException(ProductServiceException):
    """Raised when a book is not found."""
    def __init__(self, message: str = "Book not found"):
        self.message = message
        super().__init__(self.message)


class BookTypeNotFoundException(ProductServiceException):
    """Raised when a book type is not found."""
    def __init__(self, message: str = "Book type not found"):
        self.message = message
        super().__init__(self.message)


class CategoryNotFoundException(ProductServiceException):
    """Raised when a category is not found."""
    def __init__(self, message: str = "Category not found"):
        self.message = message
        super().__init__(self.message)


class PublisherNotFoundException(ProductServiceException):
    """Raised when a publisher is not found."""
    def __init__(self, message: str = "Publisher not found"):
        self.message = message
        super().__init__(self.message)


class InvalidBookDataException(ProductServiceException):
    """Raised when book data is invalid."""
    def __init__(self, message: str = "Invalid book data"):
        self.message = message
        super().__init__(self.message)


class InsufficientStockException(ProductServiceException):
    """Raised when stock is insufficient."""
    def __init__(self, book_id: int, requested: int, available: int):
        self.book_id = book_id
        self.requested = requested
        self.available = available
        self.message = (
            f"Insufficient stock for book {book_id}: "
            f"requested {requested}, available {available}"
        )
        super().__init__(self.message)


class AuthenticationException(ProductServiceException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)
