"""
Analysis service for processing search results and generating insights.
"""

from typing import Dict, Any, List
from core.state import ResearchState
from models.schemas import RedditURLAnalysis
from utils.prompts import PromptManager
import streamlit as st

class AnalysisService:
    """Service for analyzing search results and generating insights."""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt_manager = PromptManager()
        self.logger = st.session_state.get("logger")
    
    def analyze_reddit_posts(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze Reddit posts to select relevant URLs."""
        if self.logger:
            self.logger.info("🔍 Analyzing Reddit posts for relevant URLs...")
        
        user_question = state.get("user_question", "")
        reddit_results = state.get("reddit_results", "")
        
        if not reddit_results:
            if self.logger:
                self.logger.info("No Reddit results to analyze")
            return {"selected_reddit_URLs": []}
        
        structured_llm = self.llm.with_structured_output(RedditURLAnalysis)
        messages = self.prompt_manager.get_reddit_url_analysis_messages(
            user_question, reddit_results
        )
        
        try:
            analysis = structured_llm.invoke(messages)
            selected_urls = analysis.selected_URLs
            
            if self.logger:
                self.logger.success(f"Selected {len(selected_urls)} Reddit URLs for detailed analysis")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error analyzing Reddit posts: {e}")
            selected_urls = []
        
        return {"selected_reddit_URLs": selected_urls}
    
    def analyze_google_results(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze Google search results."""
        if self.logger:
            self.logger.info("🌐 Analyzing Google search results...")
        
        user_question = state.get("user_question", "")
        google_results = state.get("google_results", "")
        
        messages = self.prompt_manager.get_google_analysis_messages(
            user_question, google_results
        )
        analysis = self.llm.invoke(messages)
        
        if self.logger:
            self.logger.success("Google analysis completed")
        
        return {"google_analysis": analysis.content}
    
    def analyze_bing_results(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze Bing search results."""
        if self.logger:
            self.logger.info("🔍 Analyzing Bing search results...")
        
        user_question = state.get("user_question", "")
        bing_results = state.get("bing_results", "")
        
        messages = self.prompt_manager.get_bing_analysis_messages(
            user_question, bing_results
        )
        analysis = self.llm.invoke(messages)
        
        if self.logger:
            self.logger.success("Bing analysis completed")
        
        return {"bing_analysis": analysis.content}
    
    def analyze_reddit_results(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze Reddit search results and post data."""
        if self.logger:
            self.logger.info("🔴 Analyzing Reddit discussions...")
        
        user_question = state.get("user_question", "")
        reddit_results = state.get("reddit_results", "")
        reddit_post_data = state.get("reddit_post_data", "")
        
        messages = self.prompt_manager.get_reddit_analysis_messages(
            user_question, reddit_results, reddit_post_data
        )
        analysis = self.llm.invoke(messages)
        
        if self.logger:
            self.logger.success("Reddit analysis completed")
        
        return {"reddit_analysis": analysis.content}
    
    def synthesize_analyses(self, state: ResearchState) -> Dict[str, Any]:
        """Synthesize all analyses into a final answer."""
        if self.logger:
            self.logger.info("🔄 Synthesizing insights from all sources...")
        
        user_question = state.get("user_question", "")
        google_analysis = state.get("google_analysis", "")
        bing_analysis = state.get("bing_analysis", "")
        reddit_analysis = state.get("reddit_analysis", "")
        
        messages = self.prompt_manager.get_synthesis_messages(
            user_question, google_analysis, bing_analysis, reddit_analysis
        )
        final_answer = self.llm.invoke(messages)
        
        if self.logger:
            self.logger.success("Final synthesis completed!")
        
        return {
            "final_answer": final_answer.content,
            "messages": [{"role": "assistant", "content": final_answer.content}]
        }