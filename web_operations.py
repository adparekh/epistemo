import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus
from snapshot_operations import poll_snapshot_status, download_snapshot

load_dotenv()

def _make_api_request(URL, **kwargs):
    API_KEY = os.getenv("BRIGHTDATA_API_KEY")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(URL, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None
    except Exception as e:
        print(f"Unknown error: {e}")
        return None
    
def serp_search(query, engine="google"):
    if engine == "google":
        base_URL = "https://www.google.com/search"
    elif engine == "bing":
        base_URL = "https://www.bing.com/search"
    else:
        raise ValueError(f"Unknown engine {engine}")
    
    URL = "https://api.brightdata.com/request"

    payload = {
        "zone": "ai_agent",
        "url": f"{base_URL}?q={quote_plus(query)}&brd_json=1",
        "format": "raw"
    }

    full_response = _make_api_request(URL, json=payload)
    if not full_response:
        return None
    
    extracted_data = {
        "knowledge": full_response.get("knowledge", {}),
        "organic": full_response.get("organic", [])
    }

    return extracted_data

def _trigger_and_download_snapshot(trigger_URL, params, data, operation_name="operation"):
    trigger_result = _make_api_request(trigger_URL, params=params, json=data)
    if not trigger_result:
        return None
    
    snapshot_id = trigger_result.get("snapshot_id")
    if not snapshot_id:
        return None
    
    if not poll_snapshot_status(snapshot_id):
        return None
    
    raw_data = download_snapshot(snapshot_id)

    return raw_data
    

def reddit_search_api(keyword, date="All time", sort_by="Hot", num_of_posts=30):
    trigger_URL = "https://api.brightdata.com/datasets/v3/trigger"
    DATASET_ID = os.getenv("POSTS_DATASET_ID")

    params = {
        "dataset_id" : DATASET_ID,
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "keyword"
    }

    data = [
        {
            "keyword": keyword,
            "date": date,
            "sort_by": sort_by,
            "num_of_posts": num_of_posts
        }
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_URL, params, data, operation_name="reddit"
    )

    if not raw_data:
        return None
    
    # print("reddit posts keyword data:")
    # print(raw_data)
    
    parsed_data = []
    for post in raw_data:
        parsed_post = {
            "title": post.get("title", ""),
            "url": post.get("url", ""),
            "description": post.get("description", "")
        }

        parsed_data.append(parsed_post)
    
    return { "parsed_posts" : parsed_data, "total_found": len(parsed_data)}

def reddit_post_retrieval(URLs, days_back=10, load_all_replies=False, comment_limit=""):
    if not URLs:
        return None
    
    trigger_URL = "https://api.brightdata.com/datasets/v3/trigger"
    DATASET_ID = os.getenv("COMMENTS_DATASET_ID")

    params = {
        "dataset_id" : DATASET_ID,
        "include_errors": "true"
    }
    
    data = [
        {
            "url": URL,
            "days_back": days_back,
            "load_all_replies" : load_all_replies,
            "comment_limit" : comment_limit
        }
        for URL in URLs
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_URL, params, data, operation_name="reddit comments"
    )

    if not raw_data:
        return None
    
    # print(raw_data)
    
    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            "comment_id": comment.get("comment_id"),
            "content": comment.get("comment"),
            "date": comment.get("date_posted"),
        }
        parsed_comments.append(parsed_comment)

    return {"comments": parsed_comments, "total_retrieved": len(parsed_comments)}