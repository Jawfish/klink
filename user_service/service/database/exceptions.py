class UserCreationError(Exception):
    """Raised when the user could not be created in the database"""


class DatabaseConnectionError(Exception):
    """Raised when the database connection could not be established"""


class TransactionCommitError(Exception):
    """Raised when the database transaction could not be committed"""
