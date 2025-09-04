"""
Search service for handling different search engines and Reddit operations.
"""

from typing import Dict, List, Any
from core.state import ResearchState
from services.base_service import BaseService
from services.web_operations import WebOperations

class SearchService(BaseService):
    """Service for handling search operations."""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.web_ops = WebOperations(settings)
    
    def google_search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform Google search."""
        user_question = state.get("user_question", "")
        print(f"Searching Google for: {user_question}")
        
        results = self.web_ops.serp_search(user_question, engine="google")
        return {"google_results": results}
    
    def bing_search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform Bing search."""
        user_question = state.get("user_question", "")
        print(f"Searching Bing for: {user_question}")
        
        results = self.web_ops.serp_search(user_question, engine="bing")
        return {"bing_results": results}
    
    def reddit_search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform Reddit search."""
        user_question = state.get("user_question", "")
        print(f"Searching Reddit for: {user_question}")
        
        results = self.web_ops.reddit_search_api(user_question)
        return {"reddit_results": results}
    
    def retrieve_reddit_posts(self, state: ResearchState) -> Dict[str, Any]:
        """Retrieve detailed Reddit post data."""
        print("Getting reddit post comments")
        
        selected_urls = state.get("selected_reddit_URLs", [])
        
        if not selected_urls:
            return {"reddit_post_data": []}
        
        print(f"Processing {len(selected_urls)} Reddit URLs")
        
        reddit_post_data = self.web_ops.reddit_post_retrieval(selected_urls)
        
        if reddit_post_data:
            print(f"Successfully retrieved {len(reddit_post_data)} posts")
        else:
            print("Failed to get post data")
            reddit_post_data = []
        
        return {"reddit_post_data": reddit_post_data}