# Oracle Sentinel SDK

Python SDK for Oracle Sentinel API - AI-powered prediction market intelligence.

## Features

- 🔐 **Token Gating**: Free unlimited access for $OSAI holders (1000+ tokens)
- 💳 **x402 Payments**: Automatic micropayments via Solana/USDC
- 🤖 **AI Signals**: Access trading signals, analysis, and whale activity
- ⚡ **Simple API**: Easy-to-use Python interface

## Installation
```bash
pip install oracle-sentinel-sdk  # v2.0 with x402 support
```

For x402 payment support (auto-pay):
```bash
pip install oracle-sentinel-sdk  # v2.0 with x402 support[solana]
```

## Quick Start

### Option 1: Free Access ($OSAI Holders)

If you hold 1000+ $OSAI tokens, you get FREE unlimited access:
```python
from oracle_sentinel import OracleSentinelClient

# Just provide your wallet address
client = OracleSentinelClient(wallet_address="YOUR_WALLET_ADDRESS")

# Get signals - FREE!
signals = client.get_bulk_signals()
print(f"Found {signals['count']} signals")

for signal in signals['signals']:
    print(f"  {signal['signal']}: {signal['question'][:50]}... (edge: {signal['edge']}%)")
```

### Option 2: Pay-per-Request (x402)

No $OSAI? Pay with USDC per request:
```python
from oracle_sentinel import OracleSentinelClient

# Provide your Solana private key for auto-payment
client = OracleSentinelClient(
    private_key="YOUR_SOLANA_PRIVATE_KEY",
    rpc_url="https://api.mainnet-beta.solana.com"  # or your preferred RPC
)

# Get signals - automatically pays $0.08 USDC
signals = client.get_bulk_signals()

# Get single signal - pays $0.01 USDC
signal = client.get_signal("bitcoin-above-100k")

# Get full analysis - pays $0.03 USDC
analysis = client.get_analysis("bitcoin-above-100k")
```

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

*All endpoints are FREE for $OSAI holders (1000+ tokens)*

### Client Options
```python
client = OracleSentinelClient(
    wallet_address="...",      # For token gating (free access)
    private_key="...",         # For x402 payment (auto-pay)
    rpc_url="...",             # Solana RPC URL (default: mainnet)
    base_url="...",            # API URL (default: https://oraclesentinel.xyz)
    auto_pay=True              # Enable automatic payment (default: True)
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
    print(f"Payment required: {e.amount} USDC atomic units")
except InsufficientBalanceError as e:
    print(f"Need {e.required}, have {e.available}")
except OracleSentinelError as e:
    print(f"API error: {e}")
```

## Token Information

- **Token**: $OSAI
- **Mint**: `HuDBwWRsa4bu8ueaCb7PPgJrqBeZDkcyFqMW5bbXpump`
- **Required**: 1000+ for free access
- **Buy**: [Jupiter](https://jup.ag/swap/SOL-HuDBwWRsa4bu8ueaCb7PPgJrqBeZDkcyFqMW5bbXpump)

## Links

- **Website**: https://oraclesentinel.xyz
- **API Docs**: https://oraclesentinel.xyz/api/v1/info
- **Twitter**: [@OracleSentinel](https://twitter.com/OracleSentinel)

## License

MIT License
