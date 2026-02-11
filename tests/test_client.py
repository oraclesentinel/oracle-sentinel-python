"""Tests for Oracle Sentinel SDK"""
import pytest
from oracle_sentinel import (
    OracleSentinelClient,
    OracleSentinelError,
    PaymentRequiredError
)


def test_client_requires_auth():
    """Test that client requires wallet_address or private_key"""
    with pytest.raises(OracleSentinelError):
        OracleSentinelClient()


def test_client_with_wallet():
    """Test client initialization with wallet address"""
    client = OracleSentinelClient(
        wallet_address="9SgXmCxFLkMLdBk8ZK4MK1qLooQuxEtKXSmELKxKbk7g"
    )
    assert client.wallet_address == "9SgXmCxFLkMLdBk8ZK4MK1qLooQuxEtKXSmELKxKbk7g"
    assert client.can_pay == False


def test_get_info_free():
    """Test free endpoint"""
    client = OracleSentinelClient(
        wallet_address="9SgXmCxFLkMLdBk8ZK4MK1qLooQuxEtKXSmELKxKbk7g"
    )
    info = client.get_info()
    assert info['version'] == 'v1'


def test_holder_gets_free_access():
    """Test that $OSAI holder gets free access"""
    client = OracleSentinelClient(
        wallet_address="9SgXmCxFLkMLdBk8ZK4MK1qLooQuxEtKXSmELKxKbk7g"
    )
    signals = client.get_bulk_signals()
    assert 'count' in signals
    assert 'signals' in signals


def test_non_holder_gets_402():
    """Test that non-holder gets PaymentRequiredError"""
    client = OracleSentinelClient(
        wallet_address="11111111111111111111111111111111",
        auto_pay=False
    )
    with pytest.raises(PaymentRequiredError):
        client.get_bulk_signals()
