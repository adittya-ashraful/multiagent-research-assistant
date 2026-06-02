from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt
from research_agent.config import llm
from research_agent.schemas.state import Perspectives, ResearchGraphState
from research_agent.prompts.analyst_prompts import analyst_instructions

def create_analysts(state: ResearchGraphState):
    """Create analysts node — uses structured LLM output to generate analyst personas."""
    # Extract topic from messages if not set
    topic = state.get("topic", "")
    if not topic and state["messages"]:
        last_human_message = [m for m in state["messages"] if isinstance(m, HumanMessage)]
        if last_human_message:
            topic = last_human_message[-1].content
            
    max_analysts = state.get("max_analysts", 3)
    human_analyst_feedback = state.get("human_analyst_feedback", "")

    structured_llm = llm.with_structured_output(Perspectives)

    system_message = analyst_instructions.format(
        topic=topic,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts,
    )

    result = structured_llm.invoke(
        [
            SystemMessage(content=system_message),
            HumanMessage(content="Generate the set of analysts."),
        ]
    )

    analysts_list = getattr(result, "analysts", None) or result.get("analysts", [])
    
    # Format generated analysts as an AIMessage to be visible in the Chat UI
    analysts_text = "Here are the analysts I have generated based on your topic:\n\n"
    for analyst in analysts_list:
        analysts_text += f"- **{analyst.name}** ({analyst.role} at {analyst.affiliation}): {analyst.description}\n"
    analysts_text += "\nWould you like to refine these analysts? If yes, provide your feedback. If you are satisfied, please type 'continue' to start the interviews."
    
    return {"analysts": analysts_list, "topic": topic, "messages": [AIMessage(content=analysts_text, name="analyst_generator")]}


def human_feedback(state: ResearchGraphState):
    """Human review node: uses interrupt() to pause execution and collect feedback."""
    payload = {
        "topic": state.get("topic"),
        "analysts": [
            {
                "name": a.name,
                "role": a.role,
                "affiliation": a.affiliation,
                "description": a.description,
            }
            for a in state.get("analysts", [])
        ],
        "prompt": "Please review the analysts above. Provide feedback to refine them, or type 'continue' to approve.",
    }
    # Using interrupt to halt execution. The user can resume with feedback string via LangGraph Studio
    human_value = interrupt(payload)
    
    # Check if we got back a human message (from UI chat) or a string (from API/Command resume)
    if isinstance(human_value, str):
        feedback = human_value
    elif isinstance(human_value, dict):
        # Extract the string if the API wrapped it in a dict
        if "resume" in human_value:
            feedback = str(human_value["resume"])
        elif "data" in human_value:
            feedback = str(human_value["data"])
        else:
            # Fallback for dict
            feedback = str(list(human_value.values())[0]) if human_value else ""
    else:
        # Fallback if UI passes something else, e.g., we can just consider there's no feedback
        feedback = str(human_value) if human_value else ""
        
    return {"human_analyst_feedback": feedback}
