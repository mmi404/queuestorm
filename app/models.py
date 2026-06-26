from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any


class TransactionHistoryEntry(BaseModel):
    transaction_id: str
    timestamp: str
    type: str
    amount: float
    counterparty: str
    status: str


MAX_COMPLAINT_CHARS = 2000
MAX_HISTORY_ENTRIES = 20


class TicketRequest(BaseModel):
    ticket_id: str = Field(max_length=64)
    complaint: str = Field(min_length=1, max_length=MAX_COMPLAINT_CHARS)
    language: Optional[str] = Field(default=None, max_length=16)
    channel: Optional[str] = Field(default=None, max_length=64)
    user_type: Optional[str] = Field(default=None, max_length=64)
    campaign_context: Optional[str] = Field(default=None, max_length=256)
    transaction_history: Optional[List[TransactionHistoryEntry]] = Field(default_factory=list)
    metadata: Optional[Any] = None

    @field_validator("transaction_history", mode="before")
    @classmethod
    def coerce_null_history(cls, v):
        return v if v is not None else []

    @field_validator("transaction_history", mode="after")
    @classmethod
    def cap_history_entries(cls, v):
        if v and len(v) > MAX_HISTORY_ENTRIES:
            raise ValueError(
                f"transaction_history may contain at most {MAX_HISTORY_ENTRIES} entries"
            )
        return v


class TicketResponse(BaseModel):
    ticket_id: str
    relevant_transaction_id: Optional[str] = None
    evidence_verdict: str
    case_type: str
    severity: str
    department: str
    agent_summary: str
    recommended_next_action: str
    customer_reply: str
    human_review_required: bool
    confidence: Optional[float] = None
    reason_codes: Optional[List[str]] = None
