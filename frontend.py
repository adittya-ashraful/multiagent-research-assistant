import time
import streamlit as st
from langgraph_sdk import get_sync_client

# Initialize the LangGraph API client
# We connect to localhost:2024 where `langgraph dev` or `langgraph up` is running
client = get_sync_client(url="http://localhost:2024")

st.set_page_config(page_title="Multi-Agent Research Assistant", page_icon="🔬", layout="wide")
st.title("🔬 Multi-Agent Research Assistant")
st.caption("Powered by LangGraph API + GPT-4o-mini")

# Initialize session state variables
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_waiting_for_feedback" not in st.session_state:
    st.session_state.is_waiting_for_feedback = False

# Function to fetch and update messages from the API state
def update_messages_from_state():
    if not st.session_state.thread_id:
        return
    state = client.threads.get_state(st.session_state.thread_id)
    state_messages = state["values"].get("messages", [])
    
    ui_messages = []
    for m in state_messages:
        role = "user" if m["type"] == "human" else "assistant"
        # We only show messages that have content
        if m.get("content"):
            ui_messages.append({"role": role, "content": m["content"]})
    
    st.session_state.messages = ui_messages

# Render the chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def run_agent_with_input(user_msg=None, resume_data=None):
    with st.spinner("Agent is working..."):
        # Create a new thread if one doesn't exist
        if not st.session_state.thread_id:
            thread = client.threads.create()
            st.session_state.thread_id = thread["thread_id"]
        
        thread_id = st.session_state.thread_id
        
        try:
            # Check if we are resuming from an interrupt (Human-in-the-Loop)
            if resume_data is not None:
                run = client.runs.create(
                    thread_id,
                    assistant_id="research_agent",
                    command={"resume": resume_data}
                )
                st.session_state.is_waiting_for_feedback = False
            else:
                # Start a new run with the user's topic
                run = client.runs.create(
                    thread_id,
                    assistant_id="research_agent",
                    input={"messages": [{"type": "human", "content": user_msg}]}
                )
            
            run_id = run["run_id"]
            
            # Poll the API until the run completes or is interrupted
            while True:
                run_status = client.runs.get(thread_id, run_id)
                status = run_status["status"]
                
                if status in ["success", "error", "failed", "interrupted"]:
                    # The run finished. Check if it's paused due to an interrupt.
                    state = client.threads.get_state(thread_id)
                    has_interrupt = any(len(t.get("interrupts", [])) > 0 for t in state.get("tasks", []))
                    
                    if has_interrupt or (state.get("next") and "human_feedback" in state.get("next")):
                        st.session_state.is_waiting_for_feedback = True
                    else:
                        st.session_state.is_waiting_for_feedback = False
                    break
                
                time.sleep(1) # Wait before polling again

            # Update the chat history from the state
            update_messages_from_state()
            
            # Rerun to update the UI with new messages
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Determine the appropriate placeholder text based on the agent's state
if st.session_state.is_waiting_for_feedback:
    prompt_text = "Provide feedback to change the persona, or type 'continue'..."
    if st.button("👍 Continue with these Analysts", type="primary"):
        st.session_state.messages.append({"role": "user", "content": "continue"})
        run_agent_with_input(resume_data="continue")
else:
    prompt_text = "Enter your research topic..."

# Chat input
if user_input := st.chat_input(prompt_text):
    # Display the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if st.session_state.is_waiting_for_feedback:
        run_agent_with_input(resume_data=user_input)
    else:
        run_agent_with_input(user_msg=user_input)
