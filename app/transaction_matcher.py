import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, List

from .models import TransactionHistoryEntry


def extract_amount(text: str) -> Optional[float]:
    patterns = [
        r"(\d[\d,]*)\s*(?:taka|tk|bdt|৳|টাকা)",
        r"(?:taka|tk|bdt|৳|টাকা)\s*(\d[\d,]*)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                pass
    # fallback: first standalone number >= 10
    nums = re.findall(r"\b(\d[\d,]*)\b", text)
    for n in nums:
        v = float(n.replace(",", ""))
        if v >= 10:
            return v
    return None


def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _time_hint_ok(complaint: str, tx_dt: Optional[datetime]) -> bool:
    if tx_dt is None:
        return True
    now = datetime.now(timezone.utc)
    cl = complaint.lower()

    if "today" in cl or "আজ" in complaint:
        return tx_dt.date() == now.date()
    if "yesterday" in cl or "গতকাল" in complaint:
        return tx_dt.date() == (now - timedelta(days=1)).date()

    # hour hints like "2pm", "14:00"
    for m in re.finditer(r"(\d{1,2})(?::\d{2})?\s*(am|pm)", cl):
        hour = int(m.group(1))
        suffix = m.group(2)
        if suffix == "pm" and hour != 12:
            hour += 12
        elif suffix == "am" and hour == 12:
            hour = 0
        if abs(tx_dt.hour - hour) <= 1:
            return True

    return True  # no restrictive time hint found


def match_transactions(
    complaint: str,
    history: List[TransactionHistoryEntry],
) -> Tuple[Optional[str], str, List[str]]:
    """
    Returns (relevant_transaction_id, evidence_verdict, reason_codes).
    Pure rule-based pre-filter; LLM makes the final decision when available.
    """
    if not history:
        return None, "insufficient_data", ["no_transaction_history"]

    cl = complaint.lower()
    amount = extract_amount(complaint)

    scored: List[Tuple[int, TransactionHistoryEntry, List[str]]] = []

    for tx in history:
        score = 0
        reasons: List[str] = []
        tx_dt = _parse_ts(tx.timestamp)

        # amount match (strongest signal)
        if amount is not None and abs(tx.amount - amount) < 1:
            score += 10
            reasons.append("amount_match")

        # type keyword hints
        if tx.type == "transfer" and any(k in cl for k in ["sent", "send", "transfer", "পাঠিয়েছি", "পাঠিয়েছ"]):
            score += 3
        if tx.type == "payment" and any(k in cl for k in ["paid", "pay", "payment", "recharge", "bill"]):
            score += 3
        if tx.type == "cash_in" and any(k in cl for k in ["cash in", "cash-in", "deposit", "ক্যাশ ইন"]):
            score += 3
        if tx.type == "settlement" and "settlement" in cl:
            score += 3

        # status alignment
        if tx.status == "failed" and any(k in cl for k in ["failed", "not completed", "unsuccessful", "error"]):
            score += 5
            reasons.append("status_failed_match")
        if tx.status == "pending" and any(k in cl for k in ["not received", "not reflected", "আসেনি", "pending"]):
            score += 4
            reasons.append("status_pending_match")

        # rough time alignment
        if not _time_hint_ok(complaint, tx_dt):
            score -= 5

        if score > 0:
            scored.append((score, tx, reasons))

    if not scored:
        return None, "insufficient_data", ["no_matching_transaction"]

    scored.sort(key=lambda x: x[0], reverse=True)

    # ambiguous: two candidates with identical top score
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None, "insufficient_data", ["ambiguous_match"]

    best_score, best_tx, best_reasons = scored[0]

    # inconsistency: "wrong transfer" but same counterparty used before
    is_wrong_transfer_claim = any(k in cl for k in ["wrong", "mistake", "ভুল", "wrong number"])
    if is_wrong_transfer_claim:
        repeat_count = sum(1 for tx in history if tx.counterparty == best_tx.counterparty)
        if repeat_count >= 3:
            return best_tx.transaction_id, "inconsistent", best_reasons + ["established_recipient_pattern"]

    verdict = "consistent" if best_score >= 5 else "insufficient_data"
    return best_tx.transaction_id, verdict, best_reasons


# ---------------------------------------------------------------------------
# Rule-based case classifier used by the pure-Python fallback
# ---------------------------------------------------------------------------

PHISHING_KW = [
    "otp", "pin", "password", "passcode", "blocked if", "will be blocked",
    "called me", "sms asking", "asking for my", "verification code",
    "account will be", "share it", "প্রদান করুন", "পিন", "ওটিপি",
]
WRONG_TRANSFER_KW = ["wrong number", "wrong person", "wrong recipient", "ভুল নম্বর", "ভুলে", "wrong transfer"]
DUPLICATE_KW = ["duplicate", "twice", "double", "charged twice", "deducted twice", "দুইবার", "দুবার"]
FAILED_KW = ["failed", "not completed", "unsuccessful", "app showed failed", "showed error"]
REFUND_KW = ["refund", "return my money", "money back", "get my money", "রিফান্ড", "ফেরত"]
SETTLEMENT_KW = ["settlement", "not settled", "settle"]
AGENT_KW = ["cash in", "cash-in", "agent", "ক্যাশ ইন", "এজেন্ট", "deposit"]
INJECTION_KW = [
    "ignore previous", "ignore your", "forget your rules", "you are now",
    "pretend", "disregard", "new instruction", "override", "act as",
]


def classify_complaint(complaint: str) -> Tuple[str, str, str, bool]:
    """Returns (case_type, department, severity, human_review_required)."""
    cl = complaint.lower()

    if any(k in cl for k in PHISHING_KW):
        return "phishing_or_social_engineering", "fraud_risk", "critical", True
    if any(k in cl for k in DUPLICATE_KW):
        return "duplicate_payment", "payments_ops", "high", True
    if any(k in cl for k in WRONG_TRANSFER_KW):
        return "wrong_transfer", "dispute_resolution", "high", True
    if any(k in cl for k in FAILED_KW):
        return "payment_failed", "payments_ops", "high", False
    if any(k in cl for k in AGENT_KW):
        return "agent_cash_in_issue", "agent_operations", "high", True
    if any(k in cl for k in SETTLEMENT_KW):
        return "merchant_settlement_delay", "merchant_operations", "medium", False
    if any(k in cl for k in REFUND_KW):
        return "refund_request", "customer_support", "low", False

    return "other", "customer_support", "low", False


_REPLY_TEMPLATES = {
    "wrong_transfer": (
        "We have noted your concern about {tx_ref}. Please do not share your PIN or OTP with anyone. "
        "Our dispute team will review the case and contact you through official support channels."
    ),
    "payment_failed": (
        "We have noted that {tx_ref} may have caused an unexpected balance deduction. "
        "Our payments team will review the case and any eligible amount will be returned through official channels. "
        "Please do not share your PIN or OTP with anyone."
    ),
    "refund_request": (
        "Thank you for reaching out. Refund eligibility depends on the applicable policy. "
        "Our team will review your request and guide you accordingly. "
        "Please do not share your PIN or OTP with anyone."
    ),
    "duplicate_payment": (
        "We have noted the possible duplicate charge related to {tx_ref}. "
        "Our payments team will verify and any eligible amount will be returned through official channels. "
        "Please do not share your PIN or OTP with anyone."
    ),
    "merchant_settlement_delay": (
        "We have noted your concern about {tx_ref}. "
        "Our merchant operations team will check the batch status and update you through official channels."
    ),
    "agent_cash_in_issue": (
        "We have noted your concern about {tx_ref}. "
        "Our agent operations team will investigate and resolve this through official support channels. "
        "Please do not share your PIN or OTP with anyone."
    ),
    "phishing_or_social_engineering": (
        "Thank you for reaching out before sharing any information. "
        "We never ask for your PIN, OTP, or password under any circumstances. "
        "Please do not share these with anyone, even if they claim to be from us. "
        "Our fraud team has been notified of this incident."
    ),
    "other": (
        "Thank you for reaching out. To assist you better, please share the transaction ID, "
        "the amount involved, and a brief description of the issue. "
        "Please do not share your PIN or OTP with anyone."
    ),
}

_ACTION_TEMPLATES = {
    "wrong_transfer": "Verify {tx_ref} details with the customer and initiate the wrong-transfer dispute workflow per policy.",
    "payment_failed": "Investigate {tx_ref} ledger status. If balance was deducted on a failed payment, initiate the automatic reversal flow within standard SLA.",
    "refund_request": "Inform customer of refund eligibility per policy. If merchant-related, guide them to contact the merchant directly.",
    "duplicate_payment": "Verify with payments_ops whether two charges were processed. If confirmed duplicate, initiate reversal per policy.",
    "merchant_settlement_delay": "Route to merchant_operations to verify settlement batch status and communicate revised ETA.",
    "agent_cash_in_issue": "Investigate {tx_ref} status with agent operations. Confirm settlement and resolve within the standard cash-in SLA.",
    "phishing_or_social_engineering": "Escalate to fraud_risk team immediately. Log the reported number/contact for fraud pattern analysis.",
    "other": "Reply to customer asking for specific details: transaction ID, amount, what went wrong, and approximate time.",
}

_SUMMARY_TEMPLATES = {
    "wrong_transfer": "Customer reports {tx_ref} ({amount_ref}) was sent to an unintended recipient.",
    "payment_failed": "Customer reports {tx_ref} ({amount_ref}) failed but balance may have been deducted.",
    "refund_request": "Customer requests a refund for {tx_ref} ({amount_ref}).",
    "duplicate_payment": "Customer reports a duplicate charge of {amount_ref}. Multiple transactions with same amount detected.",
    "merchant_settlement_delay": "Merchant reports settlement delay for {tx_ref} ({amount_ref}).",
    "agent_cash_in_issue": "Customer reports {tx_ref} ({amount_ref}) cash-in not reflected in balance.",
    "phishing_or_social_engineering": "Customer reports a suspicious contact requesting credentials. Likely phishing or social engineering.",
    "other": "Customer reports an issue without sufficient detail to classify precisely.",
}


def build_rule_based_response(
    ticket_id: str,
    complaint: str,
    history: List[TransactionHistoryEntry],
) -> dict:
    cl = complaint.lower()
    tx_id, verdict, reasons = match_transactions(complaint, history)

    if any(k in cl for k in INJECTION_KW):
        reasons.append("prompt_injection_attempt")

    case_type, department, severity, human_review = classify_complaint(complaint)

    matched_tx = next((tx for tx in history if tx.transaction_id == tx_id), None)
    tx_ref = f"transaction {tx_id}" if tx_id else "the reported transaction"
    amount_ref = f"{matched_tx.amount} BDT" if matched_tx else "the reported amount"

    def render(tmpl: str) -> str:
        return tmpl.format(tx_ref=tx_ref, amount_ref=amount_ref)

    if case_type == "other" and not tx_id:
        verdict = "insufficient_data"

    return {
        "ticket_id": ticket_id,
        "relevant_transaction_id": tx_id,
        "evidence_verdict": verdict,
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": render(_SUMMARY_TEMPLATES[case_type]),
        "recommended_next_action": render(_ACTION_TEMPLATES[case_type]),
        "customer_reply": render(_REPLY_TEMPLATES[case_type]),
        "human_review_required": human_review,
        "confidence": 0.5,
        "reason_codes": ["rule_based_fallback"] + reasons,
    }
