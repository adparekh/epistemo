"""
Snapshot operations utilities for BrightData API.
"""

import time
import requests
from typing import List, Dict, Any, Optional

from services.base_service import BaseService

class SnapshotOperations(BaseService):
    """Operations for managing BrightData snapshots."""
    
    def poll_snapshot_status(self, snapshot_id: str) -> bool:
        """Poll snapshot status until completion or timeout."""
        progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        headers = {"Authorization": f"Bearer {self.settings.brightdata_api_key}"}
        
        for attempt in range(self.settings.max_poll_attempts):
            try:
                print(f"⏳ Checking snapshot progress... (attempt {attempt + 1}/{self.settings.max_poll_attempts})")
                
                response = requests.get(progress_url, headers=headers)
                response.raise_for_status()
                
                progress_data = response.json()
                status = progress_data.get("status")
                
                if status == "ready":
                    print("✅ Snapshot completed!")
                    return True
                elif status == "failed":
                    print("❌ Snapshot failed")
                    return False
                elif status == "canceled":
                    print("❌ Snapshot cancelled")
                    return False
                elif status == "running":
                    print("🔄 Still processing...")
                    time.sleep(self.settings.poll_delay)
                else:
                    print(f"❓ Unknown status: {status}")
                    time.sleep(self.settings.poll_delay)
            
            except Exception as e:
                print(f"❓ Error checking status: {e}")
                time.sleep(self.settings.poll_delay)
        
        print("⏰ Timeout waiting for snapshot completion")
        return False
    
    def download_snapshot(self, snapshot_id: str, format: str = "json") -> Optional[List[Dict[str, Any]]]:
        """Download snapshot data."""
        download_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format={format}"
        headers = {"Authorization": f"Bearer {self.settings.brightdata_api_key}"}
        
        try:
            print("📥 Downloading snapshot data...")
            
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"🎉 Successfully downloaded {len(data) if isinstance(data, list) else 1} items")
            
            return data
        except Exception as e:
            print(f"❌ Error downloading snapshot: {e}")
            return None
    
    def trigger_and_download_snapshot(
        self, 
        trigger_url: str, 
        params: Dict[str, Any], 
        data: List[Dict[str, Any]], 
        operation_name: str = "operation"
    ) -> Optional[List[Dict[str, Any]]]:
        """Trigger snapshot creation and download results."""
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.settings.brightdata_api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(trigger_url, headers=headers, params=params, json=data)
            response.raise_for_status()
            trigger_result = response.json()
        except Exception as e:
            print(f"Failed to trigger {operation_name}: {e}")
            return None
        
        snapshot_id = trigger_result.get("snapshot_id")
        if not snapshot_id:
            print(f"No snapshot ID received for {operation_name}")
            return None
        
        # Poll for completion
        if not self.poll_snapshot_status(snapshot_id):
            return None
        
        # Download results
        return self.download_snapshot(snapshot_id)