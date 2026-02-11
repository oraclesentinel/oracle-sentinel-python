"""Custom exceptions for Oracle Sentinel SDK"""


class OracleSentinelError(Exception):
    """Base exception for Oracle Sentinel SDK"""
    pass


class PaymentRequiredError(OracleSentinelError):
    """Raised when payment is required but not provided"""
    
    def __init__(self, amount: int, currency: str = "USDC"):
        self.amount = amount
        self.currency = currency
        self.amount_dollars = amount / 1_000_000
        super().__init__(
            f"Payment required: ${self.amount_dollars:.2f} {currency}"
        )


class InsufficientBalanceError(OracleSentinelError):
    """Raised when wallet has insufficient USDC balance"""
    
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        self.required_dollars = required / 1_000_000
        self.available_dollars = available / 1_000_000
        super().__init__(
            f"Insufficient balance: need ${self.required_dollars:.2f}, "
            f"have ${self.available_dollars:.2f}"
        )


class AuthenticationError(OracleSentinelError):
    """Raised when authentication fails"""
    pass


class NetworkError(OracleSentinelError):
    """Raised when network request fails"""
    pass


class TransactionError(OracleSentinelError):
    """Raised when Solana transaction fails"""
    pass
