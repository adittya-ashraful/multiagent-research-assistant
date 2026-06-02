from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Send
from research_agent.schemas.state import InterviewState, ResearchGraphState

def route_messages(state: InterviewState, name: str = "expert"):
    """Route between question and answer based on turn count."""
    messages = state["messages"]
    max_num_turns = state.get("max_num_turns", 2)

    # Count the number of expert answers
    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    # End if expert has answered more than max turns
    if num_responses >= max_num_turns:
        return "save_interview"
    return "ask_question"


def initiate_all_interviews(state: ResearchGraphState):
    """Routing function: if HITL feedback exists and is not 'continue', loop back; otherwise fan-out interviews via Send()."""
    feedback = state.get("human_analyst_feedback") or ""
    
    # Normalize feedback to check for 'continue'
    normalized_feedback = str(feedback).lower().strip().replace("'", "").replace('"', "")
    
    if normalized_feedback and "continue" not in normalized_feedback:
        return "create_analysts"

    topic = state["topic"]
    return [
        Send(
            "conduct_interview",
            {
                "analyst": analyst,
                "messages": [
                    HumanMessage(
                        content=f"So you said you were writing an article on {topic}?"
                    )
                ],
                "max_num_turns": 2,
            },
        )
        for analyst in state["analysts"]
    ]
