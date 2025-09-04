"""
Base service class for common functionality.
"""

from abc import ABC
from config.settings import Settings

class BaseService(ABC):
    """Base service class with common functionality."""
    
    def __init__(self, settings: Settings):
        self.settings = settings