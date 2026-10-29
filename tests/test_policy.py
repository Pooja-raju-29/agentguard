from decimal import Decimal

import pytest

from agentguard import DecisionReason, Policy, TransactionRequest, check_transaction


@pytest.fixture
def policy() -> Policy:
    return Policy(
        max_transaction="50",
        daily_limit="200",
        allowed_recipients=["0xABC", "0xDEF"],
    )


def test_allows_a_valid_transaction(policy: Policy) -> None:
    decision = check_transaction(TransactionRequest("35", "0xABC", "100"), policy)

    assert decision.allowed is True
    assert decision.reason_code is DecisionReason.ALLOWED


def test_denies_an_amount_above_the_per_transaction_limit(policy: Policy) -> None:
    decision = check_transaction(TransactionRequest("50.01", "0xABC", "100"), policy)

    assert decision.allowed is False
    assert decision.reason_code is DecisionReason.AMOUNT_EXCEEDS_MAXIMUM


def test_denies_a_transaction_that_would_exceed_the_daily_limit(policy: Policy) -> None:
    decision = check_transaction(TransactionRequest("35", "0xABC", "170"), policy)

    assert decision.allowed is False
    assert decision.reason_code is DecisionReason.DAILY_LIMIT_EXCEEDED


def test_denies_a_recipient_outside_the_allowlist(policy: Policy) -> None:
    decision = check_transaction(TransactionRequest("35", "0xNOT_ALLOWED", "100"), policy)

    assert decision.allowed is False
    assert decision.reason_code is DecisionReason.RECIPIENT_NOT_ALLOWED


def test_uses_a_deterministic_reason_when_multiple_rules_fail(policy: Policy) -> None:
    decision = check_transaction(TransactionRequest("75", "0xNOT_ALLOWED", "190"), policy)

    assert decision.allowed is False
    assert decision.reason_code is DecisionReason.AMOUNT_EXCEEDS_MAXIMUM


def test_recipient_comparison_is_case_insensitive(policy: Policy) -> None:
    decision = check_transaction(TransactionRequest("35", "0xabc", "100"), policy)

    assert decision.allowed is True


@pytest.mark.parametrize(
    ("amount", "daily_spent"),
    [("0", "0"), ("-1", "0"), ("1", "-1")],
)
def test_rejects_invalid_transaction_amounts(amount: str, daily_spent: str) -> None:
    with pytest.raises(ValueError):
        TransactionRequest(amount, "0xABC", daily_spent)


def test_uses_decimal_not_float_for_amounts(policy: Policy) -> None:
    decision = check_transaction(
        TransactionRequest(Decimal("0.1") + Decimal("0.2"), "0xABC", "0"), policy
    )

    assert decision.allowed is True

###checking max limit 
def test_transaction_at_maximum(policy):
    request = TransactionRequest("50", "0xABC", "100")
    decision = check_transaction(request, policy)
    assert decision.allowed is True
    assert decision.reason_code == DecisionReason.ALLOWED

##checking daily limit
def test_transaction_at_daily_limit(policy):
    request = TransactionRequest("30", "0xABC", "170")
    decision = check_transaction(request, policy)
    assert decision.allowed is True
    assert decision.reason_code == DecisionReason.ALLOWED

def test_transaction_below_maximum(policy):
    request = TransactionRequest("49.99", "0xABC", "100")

    decision = check_transaction(request, policy)

    assert decision.allowed is True
    assert decision.reason_code == DecisionReason.ALLOWED

def test_empty_allowlist_denies_transaction():
    policy = Policy(
        max_transaction="50",
        daily_limit="200",
        allowed_recipients=[]
    )

    request = TransactionRequest("30", "0xABC", "100")

    decision = check_transaction(request, policy)

    assert decision.allowed is False
    assert decision.reason_code == DecisionReason.RECIPIENT_NOT_ALLOWED

def test_empty_recipient_is_rejected():
    with pytest.raises(ValueError):
        TransactionRequest("30", "", "100")

def test_negative_max_transaction_is_rejected():
    with pytest.raises(ValueError):
        Policy(
            max_transaction="-50",
            daily_limit="200",
            allowed_recipients=["0xABC"]
        )

def test_negative_daily_limit_is_rejected():
    with pytest.raises(ValueError):
        Policy(
            max_transaction="50",
            daily_limit="-200",
            allowed_recipients=["0xABC"]
        )

def test_invalid_decimal_amount_is_rejected():
    with pytest.raises(ValueError):
        TransactionRequest("abc", "0xABC", "100")