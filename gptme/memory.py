from datetime import datetime
from dataclasses import dataclass
from typing import Generator, List
import re
from gptme.logmanager import get_conversations, Log

@dataclass
class PlanActionReflect:
    conversation_id: str
    timestamp: datetime
    planning: str
    action: str
    reflection: str | None
    message_index: int
    reflection_index: int | None

    def to_searchable_text(self) -> str:
        """Convert planning/action/reflection to searchable text format"""
        text = f"<planning>{self.planning}\n<action>{self.action}</action>"
        if self.reflection:
            text += f"\n<reflection>{self.reflection}</reflection>"
        return text

class ThoughtSearcher:
    def __init__(self):
        from ragatouille import RAGPretrainedModel # slow
        self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        self._plan_actions: List[PlanActionReflect] | None = None
        self._encoded = False

    @property
    def plan_actions(self) -> List[PlanActionReflect]:
        """Lazy load and cache planning/action/reflection triplets"""
        if self._plan_actions is None:
            self._plan_actions = get_plan_action_reflection_triples()
        return self._plan_actions

    def encode_thoughts(self):
        """Encode all planning/action/reflection triplets for search"""
        if self._encoded:
            return
            
        texts = [pa.to_searchable_text() for pa in self.plan_actions]
        self.rag.encode(
            texts,
            document_metadatas=[{"index": i} for i in range(len(texts))]
        )
        self._encoded = True

    def search(self, query: str, k: int = 3) -> List[tuple[PlanActionReflect, float]]:
        """Search for planning/action/reflection triplets relevant to query
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of tuples containing PlanActionReflect objects and their similarity scores
        """
        self.encode_thoughts()
        results = self.rag.search_encoded_docs(query, k=k)
        
        # Map search results back to PlanActionReflect objects with scores
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

def extract_reflection(content: str) -> str | None:
    """Extract reflection content from a message."""
    reflection_match = re.search(r'<reflection>(.*?)</reflection>', content, re.DOTALL)
    if not reflection_match:
        return None
    return reflection_match.group(1).strip()

def get_plan_actions() -> Generator[PlanActionReflect, None, None]:
    """Get all planning+action pairs and their subsequent reflections from conversations."""
    for conv in get_conversations():
        log = Log.read_jsonl(conv.path)
        messages = list(log)  # Convert to list to allow looking ahead
        
        last_plan_action = None
        
        for i, msg in enumerate(messages):
            # Check for reflection first
            if '<reflection>' in msg.content:
                reflection = extract_reflection(msg.content)
                if reflection and last_plan_action:
                    # Update the last plan action with this reflection
                    last_plan_action = PlanActionReflect(
                        conversation_id=last_plan_action.conversation_id,
                        timestamp=last_plan_action.timestamp,
                        planning=last_plan_action.planning,
                        action=last_plan_action.action,
                        reflection=reflection,
                        message_index=last_plan_action.message_index,
                        reflection_index=i
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
            
            # Create new PlanActionReflect without reflection
            last_plan_action = PlanActionReflect(
                conversation_id=conv.name,
                timestamp=msg.timestamp,
                planning=planning,
                action=action,
                reflection=None,
                message_index=i,
                reflection_index=None
            )
            
        # Yield the last plan action if it exists and has no reflection
        if last_plan_action:
            yield last_plan_action

def get_plan_action_reflection_triples(limit: int | None = None) -> list[PlanActionReflect]:
    """Get all planning/action/reflection triplets sorted by timestamp
    
    Args:
        limit: Optional limit on number of results to return
    
    Returns:
        List of PlanActionReflect objects containing planning, action
        and reflection content
    """
    results = list(get_plan_actions())
    results.sort(key=lambda x: x.timestamp)
    
    if limit:
        results = results[:limit]
        
    return results

if __name__ == "__main__":
    searcher = ThoughtSearcher()
    res = searcher.search("<planning>I should write a patch to the file</planning>")
    for x, score in res:
        print("SCORE:", score)
        print("PLAN:", x.planning)
        print("ACTION:", x.action)
        print("REFLECTION:", x.reflection)
        print("---")
