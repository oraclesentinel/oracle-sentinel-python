# Oracle Sentinel SDK

Python SDK for Oracle Sentinel API - AI-powered prediction market intelligence.

## Features

- 🔐 **Signature Verification**: Secure wallet ownership proof for free access
- 💳 **x402 Payments**: Automatic micropayments via Solana/USDC
- 🤖 **AI Signals**: Access trading signals, analysis, and whale activity
- ⚡ **Simple API**: Easy-to-use Python interface

## Installation
```bash
pip install oracle-sentinel
```

With Solana payment support:
```bash
pip install oracle-sentinel[solana]
```

## Quick Start

### Free Access ($OSAI Holders)

If you hold 1000+ $OSAI tokens, you get FREE unlimited access.

**v2.1.0+**: You must provide your private key to prove wallet ownership:
```python
from oracle_sentinel import OracleSentinelClient

# Export private key from Phantom/Solflare
client = OracleSentinelClient(private_key="YOUR_PRIVATE_KEY")

# FREE if you hold 1000+ $OSAI, otherwise auto-pay via x402
signals = client.get_bulk_signals()
print(f"Found {signals['count']} signals")

for signal in signals['signals']:
    print(f"  {signal['signal']}: {signal['question'][:50]}...")
```

### Pay-per-Request (x402)

No $OSAI? Same code - it auto-pays with USDC:
```python
from oracle_sentinel import OracleSentinelClient

# Provide your Solana private key
client = OracleSentinelClient(private_key="YOUR_PRIVATE_KEY")

# Automatically pays if not $OSAI holder
signals = client.get_bulk_signals()     # $0.08 USDC
signal = client.get_signal("slug")      # $0.01 USDC
analysis = client.get_analysis("slug")  # $0.03 USDC
```

## 🔐 Security (v2.1.0)

The SDK uses signature verification to prove wallet ownership:

1. SDK requests challenge from server
2. SDK signs challenge with your private key
3. Server verifies signature matches wallet
4. If valid + holds 1000+ $OSAI → FREE access
5. If invalid or no $OSAI → Pay via x402

**Your private key never leaves your machine** - only the signature is sent.

## API Reference

### Endpoints & Pricing

| Method | Endpoint | Price | Description |
|--------|----------|-------|-------------|
| `get_signal(slug)` | `/api/v1/signal/{slug}` | $0.01 | Trading signal for a market |
| `get_analysis(slug)` | `/api/v1/analysis/{slug}` | $0.03 | Full AI analysis |
| `get_whale_activity(slug)` | `/api/v1/whale/{slug}` | $0.02 | Whale trading activity |
| `get_bulk_signals()` | `/api/v1/bulk` | $0.08 | Top 10 active signals |
| `analyze_market(url)` | `/api/v1/analyze` | $0.05 | Analyze any Polymarket URL |
| `get_info()` | `/api/v1/info` | FREE | API information |

*All endpoints are FREE for verified $OSAI holders (1000+ tokens)*

### Client Options
```python
client = OracleSentinelClient(
    private_key="...",         # Required for free access & payments
    rpc_url="...",             # Solana RPC URL (default: mainnet)
    base_url="...",            # API URL (default: https://oraclesentinel.xyz)
    auto_pay=True              # Auto-pay if not holder (default: True)
)
```

### Utility Methods
```python
# Check USDC balance
balance = client.get_usdc_balance()
print(f"USDC Balance: ${balance}")

# Check if you qualify for free access
status = client.check_holder_status()
print(f"Free access: {status['has_free_access']}")
```

## Error Handling
```python
from oracle_sentinel import (
    OracleSentinelClient,
    PaymentRequiredError,
    InsufficientBalanceError,
    OracleSentinelError
)

try:
    signals = client.get_bulk_signals()
except PaymentRequiredError as e:
    print(f"Payment required: ${e.amount_dollars}")
except InsufficientBalanceError as e:
    print(f"Need ${e.required_dollars}, have ${e.available_dollars}")
except OracleSentinelError as e:
    print(f"API error: {e}")
```

## Token Information

- **Token**: $OSAI
- **Mint**: `HuDBwWRsa4bu8ueaCb7PPgJrqBeZDkcyFqMW5bbXpump`
- **Required**: 1000+ for free access
- **Buy**: [Jupiter](https://jup.ag/swap/SOL-HuDBwWRsa4bu8ueaCb7PPgJrqBeZDkcyFqMW5bbXpump)

## Links

- **PyPI**: https://pypi.org/project/oracle-sentinel/
- **Website**: https://oraclesentinel.xyz
- **API Docs**: https://oraclesentinel.xyz/api/v1/info
- **Twitter**: [@oracle_sentinel](https://twitter.com/oracle_sentinel)

## License

MIT License
