from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    session_id: str
    message: str

class InteractionFormState(BaseModel):
    hcp_name: Optional[str] = ""
    hospital_clinic: Optional[str] = ""
    specialty: Optional[str] = ""
    meeting_type: Optional[str] = ""
    meeting_date: Optional[str] = ""
    meeting_time: Optional[str] = ""
    product_discussed: Optional[str] = ""
    discussion_summary: Optional[str] = ""
    follow_up_date: Optional[str] = ""
    next_action: Optional[str] = ""
    sentiment: Optional[str] = ""
    notes: Optional[str] = ""

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    form_state: InteractionFormState
    analytics: Optional[Dict[str, Any]] = None