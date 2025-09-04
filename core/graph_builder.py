"""
Graph builder for the research agent workflow.
"""

from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

from config.settings import Settings
from core.state import ResearchState
from services.search_service import SearchService
from services.analysis_service import AnalysisService

class ResearchGraphBuilder:
    """Builds and configures the research workflow graph."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = init_chat_model(settings.model_name)
        self.search_service = SearchService(settings)
        self.analysis_service = AnalysisService(self.llm)
    
    def build(self) -> StateGraph:
        """Build and compile the research graph."""
        graph_builder = StateGraph(ResearchState)
        
        # Add nodes
        self._add_search_nodes(graph_builder)
        self._add_analysis_nodes(graph_builder)
        
        # Add edges
        self._add_edges(graph_builder)
        
        return graph_builder.compile()
    
    def _add_search_nodes(self, builder: StateGraph):
        """Add search-related nodes to the graph."""
        builder.add_node("google_search", self.search_service.google_search)
        builder.add_node("bing_search", self.search_service.bing_search)
        builder.add_node("reddit_search", self.search_service.reddit_search)
        builder.add_node("analyze_reddit_posts", self.analysis_service.analyze_reddit_posts)
        builder.add_node("retrieve_reddit_posts", self.search_service.retrieve_reddit_posts)
    
    def _add_analysis_nodes(self, builder: StateGraph):
        """Add analysis-related nodes to the graph."""
        builder.add_node("analyze_google_results", self.analysis_service.analyze_google_results)
        builder.add_node("analyze_bing_results", self.analysis_service.analyze_bing_results)
        builder.add_node("analyze_reddit_results", self.analysis_service.analyze_reddit_results)
        builder.add_node("synthesize_analyses", self.analysis_service.synthesize_analyses)
    
    def _add_edges(self, builder: StateGraph):
        """Add edges to define the workflow."""
        # Initial parallel searches
        builder.add_edge(START, "google_search")
        builder.add_edge(START, "bing_search")
        builder.add_edge(START, "reddit_search")
        
        # Reddit post analysis and retrieval
        builder.add_edge("google_search", "analyze_reddit_posts")
        builder.add_edge("bing_search", "analyze_reddit_posts")
        builder.add_edge("reddit_search", "analyze_reddit_posts")
        builder.add_edge("analyze_reddit_posts", "retrieve_reddit_posts")
        
        # Parallel result analysis
        builder.add_edge("retrieve_reddit_posts", "analyze_google_results")
        builder.add_edge("retrieve_reddit_posts", "analyze_bing_results")
        builder.add_edge("retrieve_reddit_posts", "analyze_reddit_results")
        
        # Final synthesis
        builder.add_edge("analyze_google_results", "synthesize_analyses")
        builder.add_edge("analyze_bing_results", "synthesize_analyses")
        builder.add_edge("analyze_reddit_results", "synthesize_analyses")
        
        builder.add_edge("synthesize_analyses", END)