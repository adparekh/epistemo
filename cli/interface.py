"""
Command-line interface for the research agent.
"""

from typing import Dict, Any
from core.state import ResearchState

class ChatInterface:
    """Command-line chat interface for the research agent."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def run(self):
        """Run the interactive chat interface."""
        print("Multi-Source Research Agent")
        print("Type 'exit' to quit\n")
        
        while True:
            user_input = input("Ask me anything: ")
            if user_input.lower() == "exit":
                print("Bye")
                break
            
            # Create initial state
            initial_state = self._create_initial_state(user_input)
            
            print("\nStarting parallel research process...")
            print("Launching Google, Bing, and Reddit searches...\n")
            
            try:
                final_state = self.graph.invoke(initial_state)
                self._display_results(final_state)
            except Exception as e:
                print(f"Error during research: {e}")
            
            print("-" * 80)
    
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
    
    def _display_results(self, final_state: Dict[str, Any]):
        """Display the research results."""
        final_answer = final_state.get("final_answer")
        if final_answer:
            print(f"\nFinal Answer:\n{final_answer}\n")
        else:
            print("No Final Answer generated")