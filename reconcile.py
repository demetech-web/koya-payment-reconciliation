#!/usr/bin/env python3
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
latest_by_txn = {}

with (BASE_DIR / "payments.jsonl").open(encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]
        timestamp = event.get("ts", "")
        previous = latest_by_txn.get(txn_id)

        if previous is None or timestamp >= previous.get("ts", ""):
            latest_by_txn[txn_id] = event

successful_events = [
    event for event in latest_by_txn.values()
    if event.get("status") == "success"
]
count = len(successful_events)

total = Decimal("0")
for event in successful_events:
    amount = str(event["amount"]).replace(",", "")
    total += Decimal(amount)

with (BASE_DIR / "expected.txt").open(encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
    print("Something in the data isn't being handled the way the README describes.")
else:
    rounded_total = total.quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{rounded_total}")
