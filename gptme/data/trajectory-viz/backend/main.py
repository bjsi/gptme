from fastapi import FastAPI, Query
from typing import Optional, List
from pydantic import BaseModel
import requests
import uvicorn

from gptme.memory import get_plan_action_outcome_triples, PlanActionOutcome, search_memory


app = FastAPI(
    title="LLM Code Agent Trajectory Visualizer",
    version="1.0",
)

# In-memory RAG settings; you can store these in a config or DB.
RAG_SETTINGS = {
    "score_threshold": 0.8,
    "k": 5,
}

class RAGSettings(BaseModel):
    score_threshold: float
    k: int

@app.get("/api/rag-settings")
def get_rag_settings():
    """Get the current RAG settings."""
    return RAG_SETTINGS

@app.post("/api/rag-settings")
def update_rag_settings(settings: RAGSettings):
    """Update the RAG settings."""
    RAG_SETTINGS["score_threshold"] = settings.score_threshold
    RAG_SETTINGS["k"] = settings.k
    return {"message": "RAG settings updated successfully."}

@app.get("/api/trajectories")
def get_trajectories(
    query: Optional[str] = Query(None),
    score_min: float = Query(0.0),
    score_max: float = Query(1.0),
):
    """
    Retrieve trajectory data from PlanActionOutcome objects.
    
    - query: search in plan/action/outcome (simple substring filter).
    - score_min, score_max: filter steps by their score.
    """
    # 1) Fetch all PlanActionOutcome triplets
    paos: List[PlanActionOutcome] = get_plan_action_outcome_triples()

    # 2) Optionally filter by query (simple substring match).
    if query:
        qlower = query.lower()
        def matches_query(pao: PlanActionOutcome) -> bool:
            text_block = (
                (pao.planning or "") + " " +
                (pao.action.content if pao.action else "") + " " +
                (pao.outcome or "")
            ).lower()
            return qlower in text_block
        paos = [p for p in paos if matches_query(p)]

    # 3) Filter by score range
    def in_score_range(pao: PlanActionOutcome) -> bool:
        # Some plan actions may have None as score
        if pao.score is None:
            return False
        return (pao.score >= score_min) and (pao.score <= score_max)
    paos = [p for p in paos if in_score_range(p)]

    # 4) Group by conversation_id (which we treat as "trajectory ID")
    #    So each conversation becomes one trajectory with multiple steps.
    trajectories_map = {}
    for pao in paos:
        tid = pao.conversation_id
        if tid not in trajectories_map:
            trajectories_map[tid] = {
                "id": tid,
                "steps": []
            }
        trajectories_map[tid]["steps"].append({
            "timestamp": pao.timestamp.isoformat(),
            "plan": pao.planning,
            "action": pao.action.content if pao.action else "",
            "outcome": pao.outcome,
            "score": pao.score,
        })

    # 5) Convert the map to a list for the response
    trajectories_list = list(trajectories_map.values())

    return trajectories_list

# ------------------------------------------------------
# Example: If you want an endpoint that does RAG-based search
# ------------------------------------------------------
@app.get("/api/trajectories/rag-search")
def rag_search_trajectories(query: str, k: int = 5):
    """
    Demonstrates RAG-based search. Returns top-K matching steps.
    Note: This is optional if you only want the naive substring match.
    """
    results = search_memory(query, k=k)
    # results is List[tuple[PlanActionOutcome, float]]
    out = []
    for pao, score in results:
        out.append({
            "conversation_id": pao.conversation_id,
            "timestamp": pao.timestamp.isoformat(),
            "plan": pao.planning,
            "action": pao.action.content if pao.action else "",
            "outcome": pao.outcome,
            "score": pao.score,
            "search_score": score,
        })
    return out

# To run the server: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)