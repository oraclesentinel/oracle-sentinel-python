"""
Oracle Sentinel API Client with x402 payment support.
"""

import json
import base64
import requests
from typing import Optional, Dict, Any

from .exceptions import (
    OracleSentinelError,
    PaymentRequiredError,
    InsufficientBalanceError,
    AuthenticationError,
    NetworkError,
    TransactionError
)

# Optional Solana imports
try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import VersionedTransaction
    from solders.message import MessageV0
    from solders.instruction import Instruction, AccountMeta
    from solders.hash import Hash
    from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False


class OracleSentinelClient:
    """
    Oracle Sentinel API Client.
    
    Two modes of operation:
    1. Token Gating (FREE): Provide wallet_address that holds 1000+ $OSAI
    2. x402 Payment: Provide private_key to auto-pay per request
    
    Example:
        # Free access for $OSAI holders
        client = OracleSentinelClient(wallet_address="YOUR_WALLET")
        
        # Pay-per-request
        client = OracleSentinelClient(private_key="YOUR_PRIVATE_KEY")
        
        # Get signals
        signals = client.get_bulk_signals()
    """
    
    BASE_URL = "https://oraclesentinel.xyz"
    DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
    
    # Solana constants
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    USDC_DECIMALS = 6
    TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
    
    def __init__(
        self,
        wallet_address: Optional[str] = None,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        base_url: Optional[str] = None,
        auto_pay: bool = True,
        timeout: int = 30
    ):
        """
        Initialize Oracle Sentinel client.
        
        Args:
            wallet_address: Solana wallet address (for token gating / free access)
            private_key: Solana private key base58 string (for x402 payment)
            rpc_url: Solana RPC URL
            base_url: API base URL
            auto_pay: Auto-pay when 402 received (default: True)
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or self.BASE_URL).rstrip('/')
        self.rpc_url = rpc_url or self.DEFAULT_RPC
        self.auto_pay = auto_pay
        self.timeout = timeout
        self.session = requests.Session()
        
        # Setup wallet
        self._keypair = None
        self._wallet_address = None
        
        if private_key:
            if not SOLANA_AVAILABLE:
                raise OracleSentinelError(
                    "Solana libraries required for x402 payment. "
                    "Install with: pip install oracle-sentinel-sdk[solana]"
                )
            try:
                self._keypair = Keypair.from_base58_string(private_key)
                self._wallet_address = str(self._keypair.pubkey())
            except Exception as e:
                raise OracleSentinelError(f"Invalid private key: {e}")
                
        elif wallet_address:
            self._wallet_address = wallet_address
        else:
            raise OracleSentinelError(
                "Provide wallet_address (for free access) or "
                "private_key (for x402 payment)"
            )
    
    @property
    def wallet_address(self) -> str:
        """Get wallet address"""
        return self._wallet_address
    
    @property
    def can_pay(self) -> bool:
        """Check if client can make x402 payments"""
        return self._keypair is not None
    
    # ==================== API Methods ====================
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get API information (FREE).
        
        Returns:
            API info including version, endpoints, pricing
        """
        return self._request("GET", "/api/v1/info", allow_payment=False)
    
    def get_signal(self, slug: str) -> Dict[str, Any]:
        """
        Get trading signal for a market.
        
        Price: $0.01 USDC (FREE for $OSAI holders)
        
        Args:
            slug: Market slug (e.g., "bitcoin-above-100k")
            
        Returns:
            Signal with recommendation, confidence, edge
        """
        return self._request("GET", f"/api/v1/signal/{slug}")
    
    def get_analysis(self, slug: str) -> Dict[str, Any]:
        """
        Get full AI analysis for a market.
        
        Price: $0.03 USDC (FREE for $OSAI holders)
        
        Args:
            slug: Market slug
            
        Returns:
            Full analysis with reasoning and factors
        """
        return self._request("GET", f"/api/v1/analysis/{slug}")
    
    def get_whale_activity(self, slug: str) -> Dict[str, Any]:
        """
        Get whale trading activity for a market.
        
        Price: $0.02 USDC (FREE for $OSAI holders)
        
        Args:
            slug: Market slug
            
        Returns:
            Whale trades and sentiment
        """
        return self._request("GET", f"/api/v1/whale/{slug}")
    
    def get_bulk_signals(self) -> Dict[str, Any]:
        """
        Get top 10 active trading signals.
        
        Price: $0.08 USDC (FREE for $OSAI holders)
        
        Returns:
            List of top signals
        """
        return self._request("GET", "/api/v1/bulk")
    
    def analyze_market(self, url: str) -> Dict[str, Any]:
        """
        Analyze any Polymarket URL.
        
        Price: $0.05 USDC (FREE for $OSAI holders)
        
        Args:
            url: Polymarket market URL
            
        Returns:
            Market analysis
        """
        return self._request("POST", "/api/v1/analyze", data={"url": url})
    
    # ==================== Utility Methods ====================
    
    def get_usdc_balance(self) -> float:
        """
        Get USDC balance of wallet.
        
        Returns:
            Balance in dollars
        """
        if not self._wallet_address:
            return 0.0
        
        try:
            resp = self.session.post(
                self.rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        self._wallet_address,
                        {"mint": self.USDC_MINT},
                        {"encoding": "jsonParsed"}
                    ]
                },
                timeout=self.timeout
            ).json()
            
            accounts = resp.get("result", {}).get("value", [])
            if not accounts:
                return 0.0
            
            amount = accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
            return float(amount) if amount else 0.0
        except Exception:
            return 0.0
    
    def check_holder_status(self) -> Dict[str, Any]:
        """
        Check if wallet qualifies for free access.
        
        Returns:
            Dict with is_holder and has_free_access
        """
        try:
            self._request("GET", "/api/v1/bulk", allow_payment=False)
            return {"is_holder": True, "has_free_access": True}
        except PaymentRequiredError:
            return {"is_holder": False, "has_free_access": False}
    
    # ==================== Internal Methods ====================
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OracleSentinel-SDK/2.0.0"
        }
        if self._wallet_address:
            headers["X-Wallet-Address"] = self._wallet_address
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        allow_payment: bool = True
    ) -> Dict[str, Any]:
        """Make API request with x402 payment handling."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == "GET":
                resp = self.session.get(url, headers=headers, timeout=self.timeout)
            else:
                resp = self.session.post(url, headers=headers, json=data, timeout=self.timeout)
        except requests.RequestException as e:
            raise NetworkError(f"Request failed: {e}")
        
        # Handle 402 Payment Required
        if resp.status_code == 402:
            if not allow_payment or not self.auto_pay:
                payment_info = resp.json()
                amount = int(payment_info.get("accepts", [{}])[0].get("maxAmountRequired", 0))
                raise PaymentRequiredError(amount)
            
            if not self.can_pay:
                raise OracleSentinelError(
                    "Payment required. Hold 1000+ $OSAI for free access, "
                    "or provide private_key for x402 payment."
                )
            
            # Create and send payment
            payment_info = resp.json()
            payment_header = self._create_x402_payment(payment_info)
            headers["X-Payment"] = payment_header
            
            # Retry with payment
            try:
                if method.upper() == "GET":
                    resp = self.session.get(url, headers=headers, timeout=self.timeout)
                else:
                    resp = self.session.post(url, headers=headers, json=data, timeout=self.timeout)
            except requests.RequestException as e:
                raise NetworkError(f"Payment request failed: {e}")
        
        # Handle errors
        if resp.status_code == 401:
            raise AuthenticationError("Authentication failed")
        
        if resp.status_code != 200:
            raise OracleSentinelError(f"API error {resp.status_code}: {resp.text}")
        
        return resp.json()
    
    def _create_x402_payment(self, payment_info: Dict) -> str:
        """Create x402 payment header"""
        
        accepts = payment_info.get("accepts", [])
        if not accepts:
            raise OracleSentinelError("No payment options")
        
        req = accepts[0]
        amount = int(req.get("maxAmountRequired", 0))
        pay_to = req.get("payTo")
        asset = req.get("asset")
        fee_payer = req.get("extra", {}).get("feePayer")
        network = req.get("network")
        scheme = req.get("scheme", "exact")
        
        if not all([amount, pay_to, asset, fee_payer]):
            raise OracleSentinelError("Invalid payment requirements")
        
        # Check balance
        balance = self.get_usdc_balance()
        balance_atomic = int(balance * 1_000_000)
        if balance_atomic < amount:
            raise InsufficientBalanceError(amount, balance_atomic)
        
        # Create transaction
        tx_bytes = self._create_usdc_transfer_tx(amount, pay_to, fee_payer)
        
        # Build payment payload
        payload = {
            "x402Version": 2,
            "scheme": scheme,
            "network": network,
            "payload": {
                "transaction": base64.b64encode(tx_bytes).decode()
            }
        }
        
        return base64.b64encode(json.dumps(payload).encode()).decode()
    
    def _create_usdc_transfer_tx(
        self,
        amount: int,
        destination: str,
        fee_payer: str
    ) -> bytes:
        """Create USDC transfer transaction"""
        import struct
        
        # Get recent blockhash
        resp = self.session.post(
            self.rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLatestBlockhash",
                "params": [{"commitment": "confirmed"}]
            },
            timeout=self.timeout
        ).json()
        
        blockhash = resp["result"]["value"]["blockhash"]
        
        # Derive ATAs
        source_ata = self._get_ata(self._wallet_address, self.USDC_MINT)
        dest_ata = self._get_ata(destination, self.USDC_MINT)
        
        # Build instructions
        instructions = [
            set_compute_unit_limit(20_000),
            set_compute_unit_price(1),
            self._transfer_checked_ix(
                source_ata, self.USDC_MINT, dest_ata,
                self._wallet_address, amount, self.USDC_DECIMALS
            )
        ]
        
        # Build message
        msg = MessageV0.try_compile(
            Pubkey.from_string(fee_payer),
            instructions,
            [],
            Hash.from_string(blockhash)
        )
        
        # Create and sign transaction
        tx = VersionedTransaction(msg, [self._keypair])
        return bytes(tx)
    
    def _get_ata(self, owner: str, mint: str) -> str:
        """Get Associated Token Address"""
        owner_pk = Pubkey.from_string(owner)
        mint_pk = Pubkey.from_string(mint)
        token_program = Pubkey.from_string(self.TOKEN_PROGRAM_ID)
        ata_program = Pubkey.from_string(self.ASSOCIATED_TOKEN_PROGRAM_ID)
        
        seeds = [bytes(owner_pk), bytes(token_program), bytes(mint_pk)]
        ata, _ = Pubkey.find_program_address(seeds, ata_program)
        return str(ata)
    
    def _transfer_checked_ix(
        self,
        source: str,
        mint: str,
        dest: str,
        owner: str,
        amount: int,
        decimals: int
    ) -> Instruction:
        """Create transferChecked instruction"""
        import struct
        
        # Instruction discriminator for TransferChecked = 12
        data = struct.pack("<BQB", 12, amount, decimals)
        
        accounts = [
            AccountMeta(Pubkey.from_string(source), False, True),
            AccountMeta(Pubkey.from_string(mint), False, False),
            AccountMeta(Pubkey.from_string(dest), False, True),
            AccountMeta(Pubkey.from_string(owner), True, False),
        ]
        
        return Instruction(
            Pubkey.from_string(self.TOKEN_PROGRAM_ID),
            data,
            accounts
        )
