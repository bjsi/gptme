from datetime import datetime
from dataclasses import dataclass
from typing import Generator, List
import re
from gptme.logmanager import get_conversations, Log

@dataclass
class PlanActionOutcome:
    conversation_id: str
    timestamp: datetime
    planning: str
    action: str
    outcome: str | None
    score: float | None
    message_index: int
    outcome_index: int | None

    def to_searchable_text(self) -> str:
        """Convert planning/action/outcome to searchable text format"""
        text = f"<planning>{self.planning}\n<action>{self.action}</action>"
        if self.outcome:
            text += f"\n<outcome><score>{self.score}</score>{self.outcome}</outcome>"
        return text

class ThoughtSearcher:
    def __init__(self):
        from ragatouille import RAGPretrainedModel # slow
        self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        self._plan_actions: List[PlanActionOutcome] | None = None
        self._encoded = False

    # def create_index(self):
    #    self.rag.index(
    #     collection=[full_document], 
    #     document_ids=['miyazaki'],
    #     document_metadatas=[{"entity": "person", "source": "wikipedia"}],
    #     index_name="Miyazaki", 
    #     max_document_length=180, 
    #     split_documents=True)

    @property
    def plan_actions(self) -> List[PlanActionOutcome]:
        """Lazy load and cache planning/action/outcome triplets"""
        if self._plan_actions is None:
            self._plan_actions = get_plan_action_outcome_triples()
        return self._plan_actions

    def encode_thoughts(self):
        """Encode all planning/action/outcome triplets for search"""
        if self._encoded:
            return
            
        texts = [pa.to_searchable_text() for pa in self.plan_actions]
        self.rag.encode(
            texts,
            document_metadatas=[{"index": i} for i in range(len(texts))]
        )
        self._encoded = True

    def search(self, query: str, k: int = 3) -> List[tuple[PlanActionOutcome, float]]:
        """Search for planning/action/outcome triplets relevant to query
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of tuples containing PlanActionOutcome objects and their similarity scores
        """
        self.encode_thoughts()
        results = self.rag.search_encoded_docs(query, k=k)
        
        # Map search results back to PlanActionOutcome objects with scores
        matches = []
        for result in results:
            idx = result["document_metadata"]["index"]
            score = result["score"]
            matches.append((self.plan_actions[idx], score))
        return sorted(matches, key=lambda x: x[1], reverse=True)

def extract_plan_action(content: str) -> tuple[str, str] | None:
    """Extract planning and action content from a message."""
    planning_match = re.search(r'<planning>(.*?)</planning>', content, re.DOTALL)
    if not planning_match:
        return None
        
    action_match = re.search(r'```(.*?)```', content[planning_match.end():], re.DOTALL)
    if not action_match:
        return None
        
    return (
        planning_match.group(1).strip(),
        action_match.group(1).strip()
    )

def extract_outcome(content: str) -> tuple[str, float] | None:
    """Extract outcome content and score from a message.
    
    Returns:
        Tuple of (outcome text, score) or None if no match
    """
    outcome_match = re.search(r'<outcome>(.*?)</outcome>', content, re.DOTALL)
    if not outcome_match: 
        return None
        
    outcome = outcome_match.group(1).strip()
    
    # Extract score - expecting a float between -1 and 1
    score_match = re.search(r'<score>(-?\d*\.?\d+)</score>', outcome)
    if not score_match:
        return None
    
    try:
        score = float(score_match.group(1))
        if score < -1 or score > 1:
            return None
    except ValueError:
        return None
        
    # The reflection should be everything after the score
    outcome_text = outcome[score_match.end():].strip()
    if not outcome_text:
        return None
        
    return (outcome_text, score)

def get_plan_actions() -> Generator[PlanActionOutcome, None, None]:
    """Get all planning+action pairs and their subsequent outcomes from conversations."""
    for conv in get_conversations():
        log = Log.read_jsonl(conv.path)
        messages = list(log)  # Convert to list to allow looking ahead
        
        last_plan_action = None
        
        for i, msg in enumerate(messages):
            # Check for outcome first
            if '<outcome>' in msg.content:
                outcome_data = extract_outcome(msg.content)
                if outcome_data and last_plan_action:
                    outcome_text, score = outcome_data
                    # Update the last plan action with this outcome
                    last_plan_action = PlanActionOutcome(
                        conversation_id=last_plan_action.conversation_id,
                        timestamp=last_plan_action.timestamp,
                        planning=last_plan_action.planning,
                        action=last_plan_action.action,
                        outcome=outcome_text,
                        score=score,
                        message_index=last_plan_action.message_index,
                        outcome_index=i
                    )
                    yield last_plan_action
                    last_plan_action = None
                continue
                
            # Look for planning/action pairs
            if '<planning>' not in msg.content:
                continue
                
            result = extract_plan_action(msg.content)
            if not result:
                continue
                
            planning, action = result
            
            # Create new PlanActionOutcome without outcome
            last_plan_action = PlanActionOutcome(
                conversation_id=conv.name,
                timestamp=msg.timestamp,
                planning=planning,
                action=action,
                outcome=None,
                score=None,
                message_index=i,
                outcome_index=None
            )
            
        # Yield the last plan action if it exists and has no outcome
        if last_plan_action:
            yield last_plan_action

def get_plan_action_outcome_triples(limit: int | None = None) -> list[PlanActionOutcome]:
    """Get all planning/action/outcome triplets sorted by timestamp
    
    Args:
        limit: Optional limit on number of results to return
    
    Returns:
        List of PlanActionOutcome objects containing planning, action
        and outcome content
    """
    results = list(get_plan_actions())
    results.sort(key=lambda x: x.timestamp)
    
    if limit:
        results = results[:limit]
        
    return results

if __name__ == "__main__":
    xs = get_plan_action_outcome_triples()
    for x in xs:
        print("PLAN:", x.planning)
        print("ACTION:", x.action)
        print("OUTCOME:", x.outcome)
        print("SCORE:", x.score)
        print("---")
    # searcher = ThoughtSearcher()
    # xs = searcher.search("success", 1)
    # for x, score in xs:
    #     print("PLAN:", x.planning)
    #     print("ACTION:", x.action)
    #     print("OUTCOME:", x.outcome)
    #     print("SCORE:", score)
    #     print("---")
    # print()
    # print()
    # print()
    # print()
    # print()

    # xs = searcher.search("failure", 1)
    # for x, score in xs:
    #     print("PLAN:", x.planning)
    #     print("ACTION:", x.action)
    #     print("OUTCOME:", x.outcome)
    #     print("SCORE:", score)
    #     print("---")    
