from dotenv import load_dotenv
from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from web_operations import serp_search, reddit_search_api, reddit_post_retrieval
from prompts import (
    get_reddit_URL_analysis_messages,
    get_bing_analysis_messages,
    get_google_analysis_messages,
    get_reddit_analysis_messages,
    get_synthesis_messages,
)

load_dotenv()

llm = init_chat_model("gpt-4o")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: str | None
    google_results: str | None
    bing_results: str | None
    reddit_results: str | None
    selected_reddit_URLs: list[str] | None
    reddit_post_data: list | None
    google_analysis: str | None
    bing_analysis: str | None
    reddit_analysis: str | None
    final_answer: str | None

class RedditURLAnalysis(BaseModel):
    selected_URLs: List[str] = Field(description="List of Reddit URLs that contain valuable information for answering the user's question.")
    

def google_search(state: State):
    user_question = state.get("user_question", "")
    print(f"Searching Google for: {user_question}")

    google_results = serp_search(user_question, engine="google")

    return {"google_results": google_results}

def bing_search(state: State):
    user_question = state.get("user_question", "")
    print(f"Searching Bing for: {user_question}")

    bing_results = serp_search(user_question, engine="bing")

    return {"bing_results": bing_results}

def reddit_search(state: State):
    user_question = state.get("user_question", "")
    print(f"Searching Reddit for: {user_question}")

    reddit_results = reddit_search_api(user_question)

    return {"reddit_results": reddit_results}

def analyze_reddit_posts(state: State):
    user_question = state.get("user_question", "")
    reddit_results = state.get("reddit_results", "")

    if not reddit_results:
        return {"selected_reddit_URLs": []}
    
    structured_llm = llm.with_structured_output(RedditURLAnalysis)
    messages = get_reddit_URL_analysis_messages(user_question, reddit_results)
    try:
        analysis = structured_llm.invoke(messages)
        selected_URLS = analysis.selected_URLs

        # print("Selected URLs:")
        # for i, URL in enumerate(selected_URLS):
        #     print(f"    {i + 1}. {URL}")
    except Exception as e:
        print(e)
        selected_URLS = []

    return {"selected_reddit_URLs": selected_URLS}

def retrieve_reddit_posts(state: State):
    print("Getting reddit post comments")

    selected_URLs = state.get("selected_reddit_URLs", [])

    if not selected_URLs:
        return {"reddit_post_data": []}
    
    print(f"Processing {len(selected_URLs)} Reddit URLs")

    reddit_post_data = reddit_post_retrieval(selected_URLs)

    if reddit_post_data:
        print(f"Successfully retrieved {len(reddit_post_data)} posts")
    else:
        print("Failed to get post data")
        reddit_post_data = []

    # print(reddit_post_data)

    return {"reddit_post_data": reddit_post_data}

def analyze_google_results(state: State):
    print("Analyzing Google Search Results")

    user_question = state.get("user_question", "")
    google_results = state.get("google_results", "")

    messages = get_google_analysis_messages(user_question, google_results)
    google_analysis = llm.invoke(messages)
    
    return {"google_analysis": google_analysis.content}

def analyze_bing_results(state: State):
    print("Analyzing Bing Search Results")

    user_question = state.get("user_question", "")
    bing_results = state.get("bing_results", "")

    messages = get_bing_analysis_messages(user_question, bing_results)
    bing_analysis = llm.invoke(messages)

    return {"bing_analysis": bing_analysis}

def analyze_reddit_results(state: State):
    print("Analyzing Reddit Search Results")

    user_question = state.get("user_question", "")
    reddit_results = state.get("reddit_results", "")
    reddit_post_data = state.get("reddit_post_data", "")

    messages = get_reddit_analysis_messages(user_question, reddit_results, reddit_post_data)
    reddit_analysis = llm.invoke(messages)

    return {"reddit_analysis": reddit_analysis.content}

def synthesize_analyses(state: State):
    print("Combine all results together")

    user_question = state.get("user_question", "")
    google_analysis = state.get("google_analysis", "")
    bing_analysis = state.get("bing_analysis", "")
    reddit_analysis = state.get("reddit_analysis", "")

    messages = get_synthesis_messages(user_question, google_analysis, bing_analysis, reddit_analysis)
    final_answer = llm.invoke(messages)

    return {"final_answer": final_answer.content, "messages": [{"role": "assistant", "content": final_answer.content}]}

graph_builder = StateGraph(State)

graph_builder.add_node("google_search", google_search)
graph_builder.add_node("bing_search", bing_search)
graph_builder.add_node("reddit_search", reddit_search)
graph_builder.add_node("analyze_reddit_posts", analyze_reddit_posts)
graph_builder.add_node("retrieve_reddit_posts", retrieve_reddit_posts)
graph_builder.add_node("analyze_google_results", analyze_google_results)
graph_builder.add_node("analyze_bing_results", analyze_bing_results)
graph_builder.add_node("analyze_reddit_results", analyze_reddit_results)
graph_builder.add_node("synthesize_analyses", synthesize_analyses)

graph_builder.add_edge(START, "google_search")
graph_builder.add_edge(START, "bing_search")
graph_builder.add_edge(START, "reddit_search")

graph_builder.add_edge("google_search", "analyze_reddit_posts")
graph_builder.add_edge("bing_search", "analyze_reddit_posts")
graph_builder.add_edge("reddit_search", "analyze_reddit_posts")
graph_builder.add_edge("analyze_reddit_posts", "retrieve_reddit_posts")

graph_builder.add_edge("retrieve_reddit_posts", "analyze_google_results")
graph_builder.add_edge("retrieve_reddit_posts", "analyze_bing_results")
graph_builder.add_edge("retrieve_reddit_posts", "analyze_reddit_results")

graph_builder.add_edge("analyze_google_results", "synthesize_analyses")
graph_builder.add_edge("analyze_bing_results", "synthesize_analyses")
graph_builder.add_edge("analyze_reddit_results", "synthesize_analyses")

graph_builder.add_edge("synthesize_analyses", END)

graph = graph_builder.compile()

def run_chatbot():
    print("Multi-Source Research Agent")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() == "exit":
            print("Bye")
            break

        state = {
            "messages": [{"role": "user", "content": user_input}],
            "user_question": user_input,
            "google_results": None,
            "bing_results": None,
            "reddit_results": None,
            "selected_reddit_URLs": None,
            "reddit_post_data": None,
            "google_analysis": None,
            "bing_analysis": None,
            "reddit_analysis": None,
            "final_answer": None,
        }

        print("\nStarting parallel research process...")
        print("Launching Google, Bing, and Reddit searched...\n")
        final_state = graph.invoke(state)

        if final_state.get("final_answer"):
            print(f"\nFinal Answer:\n{final_state.get('final_answer')}\n")
        else:
            print("No Final Answer")

        print("-" * 80)

if __name__ == "__main__":
    run_chatbot()

