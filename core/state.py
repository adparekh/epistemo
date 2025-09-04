"""
State management for the research agent graph.
"""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    """State container for the research graph."""
    messages: Annotated[list, add_messages]
    user_question: Optional[str]
    google_results: Optional[str]
    bing_results: Optional[str]
    reddit_results: Optional[str]
    selected_reddit_URLs: Optional[List[str]]
    reddit_post_data: Optional[List[Dict[str, Any]]]
    google_analysis: Optional[str]
    bing_analysis: Optional[str]
    reddit_analysis: Optional[str]
    final_answer: Optional[str]