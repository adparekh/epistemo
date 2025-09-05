"""
Search service for handling different search engines and Reddit operations.
"""

from typing import Dict, List, Any
from core.state import ResearchState
from services.base_service import BaseService
from services.web_operations import WebOperations
import streamlit as st

class SearchService(BaseService):
    """Service for handling search operations."""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.web_ops = WebOperations(settings)
        self.logger = st.session_state.get("logger")
    
    def google_search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform Google search."""
        user_question = state.get("user_question", "")
        if self.logger:
            self.logger.info(f"🌐 Searching Google for: {user_question}")
        
        results = self.web_ops.serp_search(user_question, engine="google")
        
        if results:
            if self.logger:
                self.logger.success("Google search completed")
        else:
            if self.logger:
                self.logger.warning("Google search returned no results")
        
        return {"google_results": results}
    
    def bing_search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform Bing search."""
        user_question = state.get("user_question", "")
        if self.logger:
            self.logger.info(f"🔍 Searching Bing for: {user_question}")
        
        results = self.web_ops.serp_search(user_question, engine="bing")
        
        if results:
            if self.logger:
                self.logger.success("Bing search completed")
        else:
            if self.logger:
                self.logger.warning("Bing search returned no results")
        
        return {"bing_results": results}
    
    def reddit_search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform Reddit search."""
        user_question = state.get("user_question", "")
        if self.logger:
            self.logger.info(f"🔴 Searching Reddit for: {user_question}")
        
        results = self.web_ops.reddit_search_api(user_question)
        
        if results and results.get("total_found", 0) > 0:
            if self.logger:
                self.logger.success(f"Found {results.get('total_found')} Reddit posts")
        else:
            if self.logger:
                self.logger.warning("Reddit search returned no results")
        
        return {"reddit_results": results}
    
    def retrieve_reddit_posts(self, state: ResearchState) -> Dict[str, Any]:
        """Retrieve detailed Reddit post data."""
        if self.logger:
            self.logger.info("📥 Retrieving Reddit post comments...")
        
        selected_urls = state.get("selected_reddit_URLs", [])
        
        if not selected_urls:
            if self.logger:
                self.logger.info("No Reddit URLs selected for detailed retrieval")
            return {"reddit_post_data": []}
        
        if self.logger:
            self.logger.info(f"Processing {len(selected_urls)} Reddit URLs")
        
        reddit_post_data = self.web_ops.reddit_post_retrieval(selected_urls)
        
        if reddit_post_data and reddit_post_data.get("total_retrieved", 0) > 0:
            if self.logger:
                self.logger.success(f"Retrieved {reddit_post_data.get('total_retrieved')} comments")
        else:
            if self.logger:
                self.logger.warning("Failed to retrieve Reddit post data")
            reddit_post_data = []
        
        return {"reddit_post_data": reddit_post_data}