from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from config.settings import Settings
from core.graph_builder import ResearchGraphBuilder
from core.state import ResearchState

load_dotenv()

app = FastAPI(title="Multi-Source Research Agent API")

# Build graph once at startup
settings = Settings()
graph_builder = ResearchGraphBuilder(settings)
research_graph = graph_builder.build()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: Optional[str] = None
    error: Optional[str] = None

@app.post("/research", response_model=QueryResponse)
def research(query: QueryRequest):
    try:
        # Prepare initial state
        initial_state: ResearchState = {
            "messages": [{"role": "user", "content": query.question}],
            "user_question": query.question,
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

        # Run research synchronously
        final_state = research_graph.invoke(initial_state)
        return QueryResponse(answer=final_state.get("final_answer"))

    except Exception as e:
        return QueryResponse(error=str(e))