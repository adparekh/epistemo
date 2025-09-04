"""
Configuration settings for the research agent.
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    """Application configuration settings."""
    
    # API Configuration
    brightdata_api_key: str = None
    posts_dataset_id: str = None
    comments_dataset_id: str = None
    
    # LLM Configuration
    model_name: str = "gpt-4o"
    
    # Search Configuration
    default_reddit_posts: int = 30
    default_days_back: int = 10
    default_load_all_replies: bool = False
    default_comment_limit: str = ""
    
    # Polling Configuration
    max_poll_attempts: int = 60
    poll_delay: int = 5
    
    def __post_init__(self):
        """Load environment variables after initialization."""
        self.brightdata_api_key = os.getenv("BRIGHTDATA_API_KEY")
        self.posts_dataset_id = os.getenv("POSTS_DATASET_ID")
        self.comments_dataset_id = os.getenv("COMMENTS_DATASET_ID")