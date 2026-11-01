# Starter issue draft — reject non-finite decimal inputs

**Suggested title:** Reject `NaN` and infinite decimal values in policy input

**Suggested labels:** `good first issue`, `tests`, `security`

## Why this matters

AgentGuard accepts monetary values as `Decimal` values or decimal strings.
`Decimal("NaN")` and `Decimal("Infinity")` are valid Decimal constructions,
but are not meaningful amounts or policy limits. They should be rejected at
input validation with the same clear `ValueError` style used for other invalid
input.

## Scope

Update the decimal-input validation in `src/agentguard/policy.py`. Do not
change rule order, decision reason codes, or the public constructor signatures.
Do not add wallet, blockchain, API, or network functionality.

## Acceptance criteria

- `Policy` rejects `NaN`, `sNaN`, `Infinity`, and `-Infinity` for both limits.
- `TransactionRequest` rejects those values for `amount` and `daily_spent`.
- Each rejection raises `ValueError` with a useful message naming the field.
- Ordinary finite decimal strings and `Decimal` instances keep their current
  behaviour.
- Tests cover at least one non-finite value for every affected input field.
- `python -m pytest` passes.

## Likely files

- `src/agentguard/policy.py`
- `tests/test_policy.py`

## Definition of done

One focused pull request, no new dependencies, updated tests, and a short PR
description stating that the change remains simulation-only.

## Estimated effort

Approximately 2–4 hours for a first contributor, including setup, tests, and
the pull-request description.
