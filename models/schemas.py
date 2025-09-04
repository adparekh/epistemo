"""
Data schemas and models for the research agent.
"""

from typing import List
from pydantic import BaseModel, Field

class RedditURLAnalysis(BaseModel):
    """Schema for Reddit URL analysis results."""
    selected_URLs: List[str] = Field(
        description="List of Reddit URLs that contain valuable information for answering the user's question."
    )