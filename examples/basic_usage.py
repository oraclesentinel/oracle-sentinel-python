"""
Basic usage example for Oracle Sentinel SDK
"""
from oracle_sentinel import OracleSentinelClient, PaymentRequiredError


# =============================================================
# Option 1: Free access for $OSAI holders
# =============================================================
def example_free_access():
    """If you hold 1000+ $OSAI, you get FREE unlimited access"""
    
    client = OracleSentinelClient(
        wallet_address="YOUR_WALLET_ADDRESS"  # Must hold 1000+ $OSAI
    )
    
    # Check if you have free access
    status = client.check_holder_status()
    print(f"Free access: {status['has_free_access']}")
    
    if status['has_free_access']:
        # Get signals - FREE!
        signals = client.get_bulk_signals()
        print(f"\nFound {signals['count']} signals:")
        
        for sig in signals['signals'][:5]:
            print(f"  [{sig['signal']}] {sig['question'][:50]}...")


# =============================================================
# Option 2: Pay-per-request with x402
# =============================================================
def example_paid_access():
    """Pay with USDC per request if you don't have $OSAI"""
    
    client = OracleSentinelClient(
        private_key="YOUR_SOLANA_PRIVATE_KEY",
        rpc_url="https://api.mainnet-beta.solana.com"
    )
    
    # Check USDC balance first
    balance = client.get_usdc_balance()
    print(f"USDC Balance: ${balance:.2f}")
    
    if balance >= 0.08:
        # Get signals - auto-pays $0.08 USDC
        signals = client.get_bulk_signals()
        print(f"Got {signals['count']} signals")


# =============================================================
# Error handling
# =============================================================
def example_error_handling():
    """Proper error handling"""
    from oracle_sentinel import (
        PaymentRequiredError,
        InsufficientBalanceError,
        OracleSentinelError
    )
    
    client = OracleSentinelClient(
        wallet_address="SOME_WALLET",
        auto_pay=False
    )
    
    try:
        signals = client.get_bulk_signals()
        print(f"Got {signals['count']} signals")
        
    except PaymentRequiredError as e:
        print(f"Need to pay: ${e.amount_dollars:.2f}")
        
    except InsufficientBalanceError as e:
        print(f"Not enough USDC: need ${e.required_dollars:.2f}")
        
    except OracleSentinelError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_error_handling()
