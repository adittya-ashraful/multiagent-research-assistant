from langchain_core.messages import AIMessage, SystemMessage, get_buffer_string, HumanMessage
from langchain_community.document_loaders import WikipediaLoader
from research_agent.config import llm, tavily_search
from research_agent.schemas.state import InterviewState, SearchQuery
from research_agent.prompts.interview_prompts import (
    question_instructions,
    search_instructions,
    answer_instructions,
    section_writer_instructions,
)

def generate_question(state: InterviewState):
    """Node to generate a question from the analyst persona."""
    analyst = state["analyst"]
    messages = state["messages"]

    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    return {"messages": [question]}


def search_web(state: InterviewState):
    """Retrieve docs from web search using Tavily."""
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions] + state["messages"])

    search_response = tavily_search.invoke(search_query.search_query)
    search_docs = search_response.get("results", [])
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}


def search_wikipedia(state: InterviewState):
    """Retrieve docs from Wikipedia."""
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions] + state["messages"])

    try:
        search_docs = WikipediaLoader(
            query=search_query.search_query, load_max_docs=2
        ).load()
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ]
        )
    except Exception as e:
        formatted_search_docs = f"Wikipedia search failed for query: {search_query.search_query}"
        
    return {"context": [formatted_search_docs]}


def generate_answer(state: InterviewState):
    """Node to generate an expert answer using gathered context."""
    analyst = state["analyst"]
    messages = state["messages"]
    context = state.get("context", [])

    system_message = answer_instructions.format(
        goals=analyst.persona, context=context
    )
    answer = llm.invoke([SystemMessage(content=system_message)] + messages)
    # Name the message as coming from the expert
    answer.name = "expert"

    return {"messages": [answer]}


def save_interview(state: InterviewState):
    """Save the interview by converting messages to a string."""
    messages = state["messages"]
    interview = get_buffer_string(messages)
    return {"interview": interview}


def write_section(state: InterviewState):
    """Write a report section from the interview context."""
    context = state.get("context", [])
    analyst = state["analyst"]

    system_message = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke(
        [
            SystemMessage(content=system_message),
            HumanMessage(
                content=f"Use this source to write your section: {context}"
            ),
        ]
    )

    return {"sections": [section.content]}
