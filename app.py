import streamlit as st
import requests

st.set_page_config(page_title="Research Agent", layout="wide")

API_URL = "http://localhost:8000/research"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_researching" not in st.session_state:
    st.session_state.is_researching = False

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    Epistemo is a research agent searches multiple sources to provide comprehensive answers:
    
    **Search Sources:**
    - 🌐 Google Search
    - 🔍 Bing Search  
    - 🔴 Reddit Discussions
    
    **Process:**
    1. Parallel searches across all sources  
    2. AI-powered analysis of results  
    3. Reddit post deep-dive  
    4. Synthesis into final answer
    """)
    
    st.header("🔧 Settings")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("💬 Epistemo: A Research Agent")

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input at bottom
if question := st.chat_input("Ask your research question...", disabled=st.session_state.is_researching):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": question})

    # Show it immediately
    with st.chat_message("user"):
        st.markdown(question)

    # Placeholder for "Generating Answer..."
    placeholder = st.empty()

    # Set researching state
    st.session_state.is_researching = True
    placeholder.info("⏳ Generating Answer...")

    try:
        # Call FastAPI
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            data = response.json()
            final_answer = data.get("answer", "⚠️ No final answer generated")

            # Save assistant reply
            st.session_state.messages.append({"role": "assistant", "content": final_answer})

            # Replace placeholder with final answer
            placeholder.empty()  # remove "Generating Answer..."
            with st.chat_message("assistant"):
                st.markdown(final_answer)
        else:
            error_msg = f"❌ Request failed: {response.status_code}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            placeholder.empty()
            with st.chat_message("assistant"):
                st.markdown(error_msg)
    finally:
        st.session_state.is_researching = False
