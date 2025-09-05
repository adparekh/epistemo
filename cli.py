"""
Multi-Source Research Agent - Main Entry Point
"""

from dotenv import load_dotenv
from config.settings import Settings
from core.graph_builder import ResearchGraphBuilder
from cli.interface import ChatInterface

def main():
    """Main entry point for the research agent."""
    load_dotenv()
    
    # Initialize settings
    settings = Settings()
    
    # Build the research graph
    graph_builder = ResearchGraphBuilder(settings)
    graph = graph_builder.build()
    
    # Start the chat interface
    interface = ChatInterface(graph)
    interface.run()

if __name__ == "__main__":
    main()