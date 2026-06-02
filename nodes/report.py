from langchain_core.messages import AIMessage, HumanMessage
from research_agent.config import llm
from research_agent.schemas.state import ResearchGraphState, InterviewState
from research_agent.prompts.report_prompts import report_writer_instructions

# We'll need to import the interview graph, but to avoid circular imports 
# we might need to be careful. However, nodes usually don't import graphs.
# The graph builder imports nodes.
# But `conduct_interview` node CALLS the interview graph.
# I'll import it inside the function or pass it in.
# Let's import it inside the function for now, or from graph.builder later.

def conduct_interview(state: InterviewState):
    """Run the interview subgraph for a single analyst."""
    from research_agent.graph.builder import interview_graph
    
    messages = state["messages"]
    analyst = state["analyst"]
    max_num_turns = state.get("max_num_turns", 2)

    result = interview_graph.invoke(
        {
            "analyst": analyst,
            "messages": messages,
            "max_num_turns": max_num_turns,
        },
        {"configurable": {"thread_id": f"interview-{analyst.name}"}},
    )

    return {"sections": result.get("sections", [])}


def write_introduction(state: ResearchGraphState):
    """Write the report introduction from all gathered sections."""
    sections = state.get("sections", [])
    topic = state["topic"]

    formatted_sections = "\n\n".join(sections)

    intro = llm.invoke(
        [
            HumanMessage(
                content=report_writer_instructions.format(
                    topic=topic,
                    context=formatted_sections,
                    section_type="introduction",
                )
            )
        ]
    )
    return {"introduction": intro.content}


def write_conclusion(state: ResearchGraphState):
    """Write the report conclusion from all gathered sections."""
    sections = state.get("sections", [])
    topic = state["topic"]

    formatted_sections = "\n\n".join(sections)

    conclusion = llm.invoke(
        [
            HumanMessage(
                content=report_writer_instructions.format(
                    topic=topic,
                    context=formatted_sections,
                    section_type="conclusion",
                )
            )
        ]
    )
    return {"conclusion": conclusion.content}


def finalize_report(state: ResearchGraphState):
    """Assemble the final report from introduction, sections, and conclusion."""
    sections = state.get("sections", [])
    introduction = state.get("introduction", "")
    conclusion = state.get("conclusion", "")

    all_sections = "\n\n---\n\n".join(sections)
    final_report = f"""# Research Report

{introduction}

---

{all_sections}

---

{conclusion}"""

    # We append the final report as an AIMessage to display it nicely in the LangGraph Studio UI chat.
    return {"final_report": final_report, "messages": [AIMessage(content=final_report, name="report_writer")]}
