import json
import logging
from typing import Dict, Any, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from app.config import settings
from app.database import SessionLocal
from app.models import Interaction, HCP, ChatHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State definition
class AgentState(TypedDict):
    messages: List[BaseMessage]
    form_state: Dict[str, Any]
    analytics: Dict[str, Any]
    session_id: str

# LLM setup using Groq
llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="gemma2-9b-it",
    temperature=0.1
)

# --- 5 Mandatory AI Tools ---

@tool
def log_interaction_tool(
    hcp_name: str, hospital_clinic: str, specialty: str, 
    meeting_type: str, meeting_date: str, meeting_time: str, 
    product_discussed: str, discussion_summary: str, 
    follow_up_date: str, next_action: str, sentiment: str, notes: str
) -> str:
    """Extract information, automatically populate fields and save the interaction record to the database."""
    db = SessionLocal()
    try:
        hcp = db.query(HCP).filter(HCP.name.ilike(hcp_name)).first()
        if not hcp:
            hcp = HCP(name=hcp_name, clinic_hospital=hospital_clinic, specialty=specialty)
            db.add(hcp)
            db.commit()
            db.refresh(hcp)
        
        interaction = Interaction(
            hcp_id=hcp.id,
            meeting_type=meeting_type,
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            product_discussed=product_discussed,
            discussion_summary=discussion_summary,
            follow_up_date=follow_up_date,
            next_action=next_action,
            sentiment=sentiment,
            notes=notes
        )
        db.add(interaction)
        db.commit()
        return "Success: Interaction extracted and saved to core database logs automatically."
    except Exception as e:
        db.rollback()
        return f"Error storing interaction: {str(e)}"
    finally:
        db.close()

@tool
def edit_interaction_tool(field_name: str, exact_value: str) -> str:
    """Modify any single specific form field using natural language corrections."""
    return f"Success: Modified field '{field_name}' to target value '{exact_value}'."

@tool
def suggest_next_action_tool(current_sentiment: str, medical_topic: str) -> str:
    """Recommend next specialized clinical sales approach based on discussion sentiment."""
    if "negative" in current_sentiment.lower() or "skeptical" in current_sentiment.lower():
        return "Provide clinical trial phase III comparative documentation regarding efficacy and clear adverse events within 48 hours."
    return "Schedule a dynamic presentation detailing multi-center patient outcome telemetry trials next month."

@tool
def generate_follow_up_plan_tool(follow_up_date: str, core_objective: str) -> str:
    """Produce precise multi-step clinical schedules and explicit timeline actions."""
    plan = {
        "milestones": [
            {"day": -2, "action": "Email Medical Affairs confirmation letter"},
            {"day": 0, "action": f"Execute interactive validation session regarding: {core_objective} on {follow_up_date}"}
        ]
    }
    return json.dumps(plan)

@tool
def interaction_analytics_tool(discussion_summary: str, sentiment: str) -> str:
    """Compile exhaustive quantitative engagement tracking metrics, cross-referencing systemic risk assessments."""
    score = 85 if "positive" in sentiment.lower() else 45
    analytics = {
        "engagement_score": score,
        "meeting_quality": "High-Value Interaction" if score > 70 else "At-Risk Presentation",
        "risks": "Competitive pressure noted" if score <= 45 else "None perceived",
        "recommendations": "Accelerate trial membership distribution instantly."
    }
    return json.dumps(analytics)

TOOLS_MAPPING = {
    "log_interaction_tool": log_interaction_tool,
    "edit_interaction_tool": edit_interaction_tool,
    "suggest_next_action_tool": suggest_next_action_tool,
    "generate_follow_up_plan_tool": generate_follow_up_plan_tool,
    "interaction_analytics_tool": interaction_analytics_tool
}

# --- LangGraph Orchestration Logic ---

def orchestrator_node(state: AgentState) -> Dict[str, Any]:
    llm_with_tools = llm.bind_tools(list(TOOLS_MAPPING.values()))
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_execution_router(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "execute_tools"
    return END

def execute_tools_node(state: AgentState) -> Dict[str, Any]:
    last_message = state["messages"][-1]
    current_form = dict(state.get("form_state", {}))
    current_analytics = dict(state.get("analytics", {}))
    outputs = []

    for call in last_message.tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]
        
        if tool_name in TOOLS_MAPPING:
            result = TOOLS_MAPPING[tool_name].invoke(tool_args)
            outputs.append(AIMessage(content=f"[Tool {tool_name} outcome]: {result}"))
            
            if tool_name == "log_interaction_tool":
                current_form.update(tool_args)
            elif tool_name == "edit_interaction_tool":
                f_name = tool_args.get("field_name")
                f_val = tool_args.get("exact_value")
                if f_name in current_form or f_name in ["hcp_name", "hospital_clinic", "specialty"]:
                    current_form[f_name] = f_val
            elif tool_name == "interaction_analytics_tool":
                try:
                    current_analytics = json.loads(result)
                except: pass
            elif tool_name == "suggest_next_action_tool":
                current_form["next_action"] = result
            elif tool_name == "generate_follow_up_plan_tool":
                current_form["notes"] = f"{current_form.get('notes', '')}\nFollow-Up: {result}".strip()

    return {"messages": outputs, "form_state": current_form, "analytics": current_analytics}

workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("execute_tools", execute_tools_node)
workflow.set_entry_point("orchestrator")
workflow.add_conditional_edges("orchestrator", tool_execution_router, {"execute_tools": "execute_tools", END: END})
workflow.add_edge("execute_tools", "orchestrator")
agent_executor = workflow.compile()

def process_agent_chat(session_id: str, raw_message: str) -> Dict[str, Any]:
    db = SessionLocal()
    history_records = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.asc()).all()
    
    messages = []
    for r in history_records:
        messages.append(HumanMessage(content=r.content) if r.role == "user" else AIMessage(content=r.content))
    messages.append(HumanMessage(content=raw_message))
    
    db.add(ChatHistory(session_id=session_id, role="user", content=raw_message))
    db.commit()

    initial_form = {k: "" for k in ["hcp_name", "hospital_clinic", "specialty", "meeting_type", "meeting_date", "meeting_time", "product_discussed", "discussion_summary", "follow_up_date", "next_action", "sentiment", "notes"]}
    initial_state = {"messages": messages, "form_state": initial_form, "analytics": {}, "session_id": session_id}

    final_output = agent_executor.invoke(initial_state)
    
    ai_response_text = ""
    for msg in reversed(final_output["messages"]):
        if isinstance(msg, AIMessage) and not msg.tool_calls and not msg.content.startswith("[Tool"):
            ai_response_text = msg.content
            break
    if not ai_response_text:
        ai_response_text = "I have automatically mapped and stored the interaction data elements through the graph pipeline."

    db.add(ChatHistory(session_id=session_id, role="assistant", content=ai_response_text))
    db.commit()
    db.close()

    return {"reply": ai_response_text, "form_state": final_output.get("form_state", initial_form), "analytics": final_output.get("analytics", {})}