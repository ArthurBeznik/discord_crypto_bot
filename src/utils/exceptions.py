# exceptions.py

class CryptoResolveException(Exception):
    """Raised when a cryptocurrency cannot be resolved in the crypto map."""
    def __init__(self, crypto):
        super().__init__(f"Could not resolve cryptocurrency: {crypto}")


class FormattingException(Exception):
    """Raised when an error occurs during formatting of data for output."""
    def __init__(self, message="An error occurred in formatting data"):
        super().__init__(message)


class PriceFetchException(Exception):
    """Raised when there is an error fetching price data from the external API."""
    def __init__(self, crypto, status_code=None):
        message = f"Failed to fetch price for {crypto}"
        if status_code:
            message += f" (HTTP {status_code})"
        super().__init__(message)


class DatabaseOperationException(Exception):
    """Raised when a database operation fails."""
    def __init__(self, operation, detail=""):
        message = f"Database operation '{operation}' failed"
        if detail:
            message += f": {detail}"
        super().__init__(message)


class AlertNotFoundException(Exception):
    """Raised when a specific alert cannot be found in the database."""
    def __init__(self, alert_id, user_id):
        super().__init__(f"Alert with ID {alert_id} not found for user {user_id}")

# Add more custom exceptions here as needed
