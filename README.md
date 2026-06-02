# Research Agent

This folder contains the implementation of a research agent built with LangGraph. The agent is designed to perform iterative research by generating analyst perspectives, conducting interviews (via web search and Wikipedia), and synthesizing a comprehensive report.

## Directory Structure

```
research_agent/
├── agent.py              # Entry point that exports the compiled graph
├── config.py             # Configuration: API keys, LLM, and search tool initialization
├── .gitignore            # Git ignore rules
├── .env                  # Environment variables (API keys)
├── README.md             # This file
├── graph/
│   └── builder.py        # Defines and compiles the StateGraph (interview subgraph and outer research graph)
├── nodes/
│   ├── analysts.py       # Node for creating analysts and handling human feedback
│   ├── interview.py      # Nodes for the interview process: question generation, searching, answering, saving interviews, writing sections
│   ├── report.py         # Nodes for report writing: conducting interview (subgraph call), introduction, conclusion, finalization
│   └── router.py         # Routing logic for the interview subgraph and interview initiation
├── schemas/
│   └── state.py          # State schemas: InterviewState and ResearchGraphState
├── prompts/
│   ├── analyst_prompts.py   # Prompts for analyst creation
│   ├── interview_prompts.py # Prompts for question generation, answering, etc.
│   └── report_prompts.py    # Prompts for report sections (intro, conclusion, etc.)
```

## Key Components

### agent.py
- Imports and exports the compiled graph from `graph.builder`.
- Serves as the main entry point for the agent.

### config.py
- Loads environment variables from `.env` using `python-dotenv`.
- Initializes the LLM (`ChatOpenAI` with model "gpt-4o-mini" and temperature 0).
- Initializes the Tavily search tool for web search.

### graph/builder.py
- Constructs two interconnected StateGraphs:
  1. **Interview Subgraph** (`interview_builder`): Handles a single interview cycle (ask question → search web/Wikipedia → generate answer → save interview → write section).
  2. **Outer Research Graph** (`research_builder`): Manages the overall research workflow:
     - Create analysts → Human feedback → (if approved) Conduct interviews (via the subgraph) → Write introduction → Write conclusion → Finalize report.
- Uses conditional edges for routing based on agent decisions.

### nodes/
- **analysts.py**: Contains `create_analysts` (generates analyst perspectives) and `human_feedback` (simulates human approval).
- **interview.py**: Implements the interview process nodes:
  - `generate_question`: Creates questions based on analyst instructions.
  - `search_web` / `search_wikipedia`: Performs searches.
  - `generate_answer`: Formulates answers from search results.
  - `save_interview`: Stores interview results.
  - `write_section`: Writes a report section from an interview.
- **report.py**: Handles report compilation:
  - `conduct_interview`: Invokes the interview subgraph for all analysts.
  - `write_introduction` / `write_conclusion`: Writes report bookends.
  - `finalize_report`: Combines sections into a final report.
- **router.py**: Defines routing functions:
  - `route_messages`: Decides whether to continue interviewing or save based on answers.
  - `initiate_all_interviews`: Launches interviews for all analysts after human feedback.

### schemas/state.py
- Defines the state structures:
  - `InterviewState`: Tracks the state of a single interview (question, search results, answers, etc.).
  - `ResearchGraphState`: Tracks the overall research state (analysts, interviews, report sections, final report).

### prompts/
- Contains prompt templates used by the nodes:
  - `analyst_prompts.py`: Prompts for generating analyst personas.
  - `interview_prompts.py`: Prompts for question generation, searching, and answer formulation.
  - `report_prompts.py`: Prompts for writing report sections (introduction, conclusion, etc.).

## Workflow Overview

1. **Analyst Creation**: The agent generates a list of analyst personas based on the research topic.
2. **Human Feedback**: (Simulated) Review of analysts; if approved, proceed; otherwise, regenerate analysts.
3. **Interview Phase**: For each analyst:
   - Generate an interview question.
   - Search the web and Wikipedia for information.
   - Generate an answer from the search results.
   - Save the interview transcript.
   - Write a report section based on the interview.
4. **Report Synthesis**: Combine all sections into a report with an introduction, body (from interviews), and conclusion.
5. **Finalization**: Output the completed research report.

## Configuration

- Adjust the LLM model or temperature in `config.py`.
- Modify search behavior (e.g., max results) in the TavilySearch initialization.
- Set API keys in the `.env` file (OPENAI_API_KEY, TAVILY_API_KEY).

## Usage

To use this research agent, import the graph from `agent.py` and invoke it with an initial state containing the research topic. See the project's main documentation or examples for integration details.

## Development

Follow the existing code structure and conventions when adding new features or modifying the agent.
