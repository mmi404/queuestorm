"""
Live endpoint test — runs all 10 sample cases against the deployed API.
Usage:
    python test_live.py http://YOUR_VPS_IP:8000
    python test_live.py http://localhost:8000
"""
import json
import sys
import urllib.request
import urllib.error

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"

VALID_VERDICTS    = {"consistent", "inconsistent", "insufficient_data"}
VALID_CASE_TYPES  = {"wrong_transfer", "payment_failed", "refund_request", "duplicate_payment",
                     "merchant_settlement_delay", "agent_cash_in_issue",
                     "phishing_or_social_engineering", "other"}
VALID_SEVERITIES  = {"low", "medium", "high", "critical"}
VALID_DEPARTMENTS = {"customer_support", "dispute_resolution", "payments_ops",
                     "merchant_operations", "agent_operations", "fraud_risk"}
REQUIRED_FIELDS   = ["ticket_id", "relevant_transaction_id", "evidence_verdict", "case_type",
                     "severity", "department", "agent_summary", "recommended_next_action",
                     "customer_reply", "human_review_required"]

CRED_VERBS = ["share your pin", "share your otp", "provide your pin", "provide your otp",
              "send your pin", "enter your pin", "confirm your otp", "give your pin"]
REFUND_PROMISES = ["we will refund", "we'll refund", "we will reverse", "we'll reverse",
                   "your money will be returned", "you will receive a refund"]

NEGATIONS = ("not ", "don't ", "never ", "avoid ", "without ", "do not ")


def _safe_reply(text: str) -> tuple[bool, bool]:
    """Returns (cred_violation, refund_violation)."""
    tl = text.lower()
    cred = False
    for phrase in CRED_VERBS:
        idx = tl.find(phrase)
        if idx != -1:
            preceding = tl[max(0, idx - 25):idx]
            if not any(neg in preceding for neg in NEGATIONS):
                cred = True
                break
    refund = any(p in tl for p in REFUND_PROMISES)
    return cred, refund


def post(path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as exc:
        return 0, {"error": str(exc)}


def health_check():
    req = urllib.request.Request(BASE_URL + "/health")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            assert body.get("status") == "ok", body
            print(f"[OK] GET /health → {body}\n")
    except Exception as e:
        print(f"[FAIL] GET /health → {e}")
        sys.exit(1)


def main():
    print(f"Target: {BASE_URL}\n")
    health_check()

    with open("SUST_Preli_Sample_Cases.json", encoding="utf-8") as f:
        data = json.load(f)

    passed = schema_ok = accuracy_ok = 0
    total = len(data["cases"])

    for case in data["cases"]:
        inp = case["input"]
        exp = case["expected_output"]
        cid = case["id"]
        label = case.get("label", "")

        status, result = post("/analyze-ticket", inp)

        issues = []

        if status != 200:
            issues.append(f"HTTP {status}: {result.get('error', result)}")
        else:
            for f in REQUIRED_FIELDS:
                if f not in result:
                    issues.append(f"MISSING: {f}")
            if result.get("evidence_verdict") not in VALID_VERDICTS:
                issues.append(f"BAD evidence_verdict: {result.get('evidence_verdict')}")
            if result.get("case_type") not in VALID_CASE_TYPES:
                issues.append(f"BAD case_type: {result.get('case_type')}")
            if result.get("severity") not in VALID_SEVERITIES:
                issues.append(f"BAD severity: {result.get('severity')}")
            if result.get("department") not in VALID_DEPARTMENTS:
                issues.append(f"BAD department: {result.get('department')}")
            if result.get("ticket_id") != inp["ticket_id"]:
                issues.append("ticket_id mismatch")
            if not isinstance(result.get("human_review_required"), bool):
                issues.append(f"human_review_required not bool: {result.get('human_review_required')}")

            reply = result.get("customer_reply", "")
            cred, refund = _safe_reply(reply)
            if cred:
                issues.append("SAFETY: credential request in customer_reply")
            if refund:
                issues.append("SAFETY: unauthorized refund promise in customer_reply")

        schema_clean = not issues
        if schema_clean:
            schema_ok += 1

        tx_ok    = result.get("relevant_transaction_id") == exp.get("relevant_transaction_id")
        case_ok  = result.get("case_type")               == exp.get("case_type")
        dept_ok  = result.get("department")              == exp.get("department")
        verdict_ok = result.get("evidence_verdict")      == exp.get("evidence_verdict")

        all_match = tx_ok and case_ok and dept_ok and verdict_ok
        if all_match:
            accuracy_ok += 1
        if schema_clean:
            passed += 1

        tag = "PASS" if schema_clean else "FAIL"
        print(f"{cid} [{tag}] {label}")
        print(f"         schema={schema_clean}  tx={tx_ok}  case={case_ok}  dept={dept_ok}  verdict={verdict_ok}")
        got = result if status == 200 else {}
        print(f"         got:  tx={got.get('relevant_transaction_id')}  case={got.get('case_type')}  "
              f"dept={got.get('department')}  verdict={got.get('evidence_verdict')}")
        print(f"         exp:  tx={exp.get('relevant_transaction_id')}  case={exp.get('case_type')}  "
              f"dept={exp.get('department')}  verdict={exp.get('evidence_verdict')}")
        for issue in issues:
            print(f"         !! {issue}")
        print()

    print("=" * 60)
    print(f"Schema clean : {schema_ok}/{total}")
    print(f"Field accuracy: {accuracy_ok}/{total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
