"""
Web operations service for API interactions.
"""

import requests
from urllib.parse import quote_plus
from typing import Dict, List, Any, Optional

from services.base_service import BaseService
from utils.snapshot_operations import SnapshotOperations

class WebOperations(BaseService):
    """Service for web API operations."""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.snapshot_ops = SnapshotOperations(settings)
    
    def _make_api_request(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated API request to BrightData."""
        headers = {
            "Authorization": f"Bearer {self.settings.brightdata_api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            return None
        except Exception as e:
            print(f"Unknown error: {e}")
            return None
    
    def serp_search(self, query: str, engine: str = "google") -> Optional[Dict[str, Any]]:
        """Perform SERP search using specified engine."""
        if engine == "google":
            base_url = "https://www.google.com/search"
        elif engine == "bing":
            base_url = "https://www.bing.com/search"
        else:
            raise ValueError(f"Unknown engine: {engine}")
        
        api_url = "https://api.brightdata.com/request"
        payload = {
            "zone": "ai_agent",
            "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
            "format": "raw"
        }
        
        full_response = self._make_api_request(api_url, json=payload)
        if not full_response:
            return None
        
        return {
            "knowledge": full_response.get("knowledge", {}),
            "organic": full_response.get("organic", [])
        }
    
    def reddit_search_api(
        self, 
        keyword: str, 
        date: str = "All time", 
        sort_by: str = "Hot",
        num_of_posts: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Search Reddit posts by keyword."""
        trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
        
        params = {
            "dataset_id": self.settings.posts_dataset_id,
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "keyword"
        }
        
        data = [{
            "keyword": keyword,
            "date": date,
            "sort_by": sort_by,
            "num_of_posts": num_of_posts or self.settings.default_reddit_posts
        }]
        
        raw_data = self.snapshot_ops.trigger_and_download_snapshot(
            trigger_url, params, data, "reddit search"
        )
        
        if not raw_data:
            return None
        
        parsed_data = []
        for post in raw_data:
            parsed_post = {
                "title": post.get("title", ""),
                "url": post.get("url", ""),
                "description": post.get("description", "")
            }
            parsed_data.append(parsed_post)
        
        return {
            "parsed_posts": parsed_data, 
            "total_found": len(parsed_data)
        }
    
    def reddit_post_retrieval(
        self, 
        urls: List[str],
        days_back: Optional[int] = None,
        load_all_replies: Optional[bool] = None,
        comment_limit: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve Reddit post comments."""
        if not urls:
            return None
        
        trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
        
        params = {
            "dataset_id": self.settings.comments_dataset_id,
            "include_errors": "true"
        }
        
        data = []
        for url in urls:
            data.append({
                "url": url,
                "days_back": days_back or self.settings.default_days_back,
                "load_all_replies": load_all_replies or self.settings.default_load_all_replies,
                "comment_limit": comment_limit or self.settings.default_comment_limit
            })
        
        raw_data = self.snapshot_ops.trigger_and_download_snapshot(
            trigger_url, params, data, "reddit comments"
        )
        
        if not raw_data:
            return None
        
        parsed_comments = []
        for comment in raw_data:
            parsed_comment = {
                "comment_id": comment.get("comment_id"),
                "content": comment.get("comment"),
                "date": comment.get("date_posted"),
            }
            parsed_comments.append(parsed_comment)
        
        return {
            "comments": parsed_comments, 
            "total_retrieved": len(parsed_comments)
        }