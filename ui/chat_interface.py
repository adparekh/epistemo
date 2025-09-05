"""
Streamlit chat interface component.
"""

import streamlit as st
import threading
from typing import Dict, Any
from datetime import datetime

from core.state import ResearchState
from utils.logger import StreamlitLogger

class ChatInterface:
    """Streamlit chat interface for the research agent."""
    
    def __init__(self, graph, logger: StreamlitLogger):
        self.graph = graph
        self.logger = logger
    
    def render(self):
        """Render the chat interface."""
        # Display chat history
        self._display_chat_history()
        
        # Chat input
        self._render_chat_input()
    
    def _display_chat_history(self):
        """Display the conversation history."""
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message["role"] == "user":
                        st.markdown(message["content"])
                    else:
                        # Assistant message with research status
                        if "status" in message:
                            if message["status"] == "researching":
                                st.info("🔄 Researching your question across multiple sources...")
                            elif message["status"] == "complete":
                                st.success("✅ Research complete!")
                        
                        if "content" in message:
                            st.markdown(message["content"])
    
    def _render_chat_input(self):
        """Render the chat input field."""
        # Disable input during research
        disabled = st.session_state.get("is_researching", False)
        
        if prompt := st.chat_input("Ask me anything...", disabled=disabled):
            self._handle_user_input(prompt)
    
    def _handle_user_input(self, user_input: str):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Show researching status
        st.session_state.messages.append({
            "role": "assistant",
            "status": "researching"
        })
        st.session_state.is_researching = True

        # Synchronous call — just like CLI
        try:
            initial_state = self._create_initial_state(user_input)
            final_state = self.graph.invoke(initial_state)

            # Remove researching status
            st.session_state.messages = [
                msg for msg in st.session_state.messages
                if msg.get("status") != "researching"
            ]

            final_answer = final_state.get("final_answer")
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer or "No answer generated",
                "status": "complete"
            })
        
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {e}",
                "status": "error"
            })
        
        finally:
            st.session_state.is_researching = False
            st.rerun()

    
    def _perform_research(self, user_input: str):
        """Perform research and update the chat."""
        try:
            # Create initial state
            initial_state = self._create_initial_state(user_input)
            
            # Log research start
            self.logger.info(f"Starting research for: {user_input}")
            self.logger.info("Launching parallel searches across Google, Bing, and Reddit...")
            
            # Execute the research graph
            final_state = self.graph.invoke(initial_state)
            
            # Remove the "researching" status message
            st.session_state.messages = [msg for msg in st.session_state.messages 
                                       if msg.get("status") != "researching"]
            
            # Add final answer
            final_answer = final_state.get("final_answer")
            if final_answer:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "status": "complete",
                    "timestamp": datetime.now()
                })
                self.logger.success("Research completed successfully!")
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I apologize, but I couldn't generate a comprehensive answer. Please try rephrasing your question.",
                    "status": "error",
                    "timestamp": datetime.now()
                })
                self.logger.error("Failed to generate final answer")
        
        except Exception as e:
            # Remove the "researching" status message
            st.session_state.messages = [msg for msg in st.session_state.messages 
                                       if msg.get("status") != "researching"]
            
            # Add error message
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"An error occurred during research: {str(e)}",
                "status": "error",
                "timestamp": datetime.now()
            })
            self.logger.error(f"Research error: {str(e)}")
        
        finally:
            # Reset researching state
            st.session_state.is_researching = False
            st.rerun()
    
    def _create_initial_state(self, user_input: str) -> ResearchState:
        """Create the initial state for the research graph."""
        return {
            "messages": [{"role": "user", "content": user_input}],
            "user_question": user_input,
            "google_results": None,
            "bing_results": None,
            "reddit_results": None,
            "selected_reddit_URLs": None,
            "reddit_post_data": None,
            "google_analysis": None,
            "bing_analysis": None,
            "reddit_analysis": None,
            "final_answer": None,
        }