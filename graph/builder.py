from langgraph.graph import START, END, StateGraph
from research_agent.schemas.state import InterviewState, ResearchGraphState
from research_agent.nodes.analysts import create_analysts, human_feedback
from research_agent.nodes.interview import (
    generate_question,
    search_web,
    search_wikipedia,
    generate_answer,
    save_interview,
    write_section,
)
from research_agent.nodes.report import (
    conduct_interview,
    write_introduction,
    write_conclusion,
    finalize_report,
)
from research_agent.nodes.router import route_messages, initiate_all_interviews

#BUILD INTERVIEW SUBGRAPH

interview_builder = StateGraph(InterviewState)
interview_builder.add_node("ask_question", generate_question)
interview_builder.add_node("search_web", search_web)
interview_builder.add_node("search_wikipedia", search_wikipedia)
interview_builder.add_node("answer_question", generate_answer)
interview_builder.add_node("save_interview", save_interview)
interview_builder.add_node("write_section", write_section)

interview_builder.add_edge(START, "ask_question")
interview_builder.add_edge("ask_question", "search_web")
interview_builder.add_edge("ask_question", "search_wikipedia")
interview_builder.add_edge("search_web", "answer_question")
interview_builder.add_edge("search_wikipedia", "answer_question")
interview_builder.add_conditional_edges(
    "answer_question", route_messages, ["ask_question", "save_interview"]
)
interview_builder.add_edge("save_interview", "write_section")
interview_builder.add_edge("write_section", END)

interview_graph = interview_builder.compile().with_config(run_name="Conduct Interviews")


#BUILD OUTER RESEARCH GRAPH

research_builder = StateGraph(ResearchGraphState)

research_builder.add_node("create_analysts", create_analysts)
research_builder.add_node("human_feedback", human_feedback)
research_builder.add_node("conduct_interview", conduct_interview)
research_builder.add_node("write_introduction", write_introduction)
research_builder.add_node("write_conclusion", write_conclusion)
research_builder.add_node("finalize_report", finalize_report)

research_builder.add_edge(START, "create_analysts")
research_builder.add_edge("create_analysts", "human_feedback")

research_builder.add_conditional_edges(
    "human_feedback",
    initiate_all_interviews,
    ["create_analysts", "conduct_interview"],
)

research_builder.add_edge("conduct_interview", "write_introduction")
research_builder.add_edge("write_introduction", "write_conclusion")
research_builder.add_edge("write_conclusion", "finalize_report")
research_builder.add_edge("finalize_report", END)

graph = research_builder.compile()
