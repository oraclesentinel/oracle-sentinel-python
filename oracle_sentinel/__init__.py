"""
Oracle Sentinel SDK - AI-powered prediction market intelligence

Usage:
    from oracle_sentinel import OracleSentinelClient
    
    # Free access for $OSAI holders
    client = OracleSentinelClient(wallet_address="YOUR_WALLET")
    
    # Or pay-per-request with x402
    client = OracleSentinelClient(private_key="YOUR_PRIVATE_KEY")
    
    signals = client.get_bulk_signals()
"""

from .client import OracleSentinelClient
from .exceptions import (
    OracleSentinelError,
    PaymentRequiredError,
    InsufficientBalanceError,
    AuthenticationError,
    NetworkError,
    TransactionError
)

__version__ = "2.1.0"
__author__ = "Oracle Sentinel Team"

__all__ = [
    "OracleSentinelClient",
    "OracleSentinelError",
    "PaymentRequiredError",
    "InsufficientBalanceError",
    "AuthenticationError",
    "NetworkError",
    "TransactionError"
]
