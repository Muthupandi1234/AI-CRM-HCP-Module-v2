from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, InteractionFormState
from app.models import ChatHistory
from app.services.agent import process_agent_chat

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def post_chat_interaction(payload: ChatRequest):
    try:
        outcome = process_agent_chat(session_id=payload.session_id, raw_message=payload.message)
        return ChatResponse(
            session_id=payload.session_id,
            reply=outcome["reply"],
            form_state=InteractionFormState(**outcome["form_state"]),
            analytics=outcome["analytics"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal LangGraph Operational Error: {str(e)}"
        )

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    histories = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.asc()).all()
    return [{"role": h.role, "content": h.content} for h in histories]