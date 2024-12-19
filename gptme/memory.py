from datetime import datetime
from dataclasses import dataclass
from typing import Generator, List
import re
from gptme.logmanager import get_conversations, Log
from ragatouille import RAGPretrainedModel

@dataclass
class ThinkingAction:
    conversation_id: str
    timestamp: datetime
    thinking: str
    action: str
    message_index: int

    def to_searchable_text(self) -> str:
        """Convert thinking/action pair to searchable text format"""
        return f"<thinking>{self.thinking}\n<action>{self.action}</action>"

class ThoughtSearcher:
    def __init__(self):
        self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        self._thought_actions: List[ThinkingAction] | None = None
        self._encoded = False

    @property
    def thought_actions(self) -> List[ThinkingAction]:
        """Lazy load and cache thinking/action pairs"""
        if self._thought_actions is None:
            self._thought_actions = get_thought_action_pairs()
        return self._thought_actions

    def encode_thoughts(self):
        """Encode all thinking/action pairs for search"""
        if self._encoded:
            return
            
        texts = [ta.to_searchable_text() for ta in self.thought_actions]
        self.rag.encode(
            texts,
            document_metadatas=[{"index": i} for i in range(len(texts))]
        )
        self._encoded = True

    def search(self, query: str, k: int = 3) -> List[tuple[ThinkingAction, float]]:
        """Search for thinking/action pairs relevant to query
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of tuples containing ThinkingAction objects and their similarity scores
        """
        self.encode_thoughts()
        results = self.rag.search_encoded_docs(query, k=k)
        
        # Map search results back to ThinkingAction objects with scores
        matches = []
        for result in results:
            idx = result["document_metadata"]["index"]
            score = result["score"]
            matches.append((self.thought_actions[idx], score))
        return sorted(matches, key=lambda x: x[1], reverse=True)

def extract_thinking_action(content: str) -> tuple[str, str] | None:
    """Extract thinking tag content and subsequent action from a message."""
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, re.DOTALL)
    if not thinking_match:
        return None
        
    action_match = re.search(r'```(.*?)```', content[thinking_match.end():], re.DOTALL)
    if not action_match:
        return None
        
    return thinking_match.group(1).strip(), action_match.group(1).strip()

def get_thinking_actions() -> Generator[ThinkingAction, None, None]:
    """Get all thinking+action pairs from all conversations."""
    for conv in get_conversations():
        log = Log.read_jsonl(conv.path)
        
        for i, msg in enumerate(log):
            if '<thinking>' not in msg.content:
                continue
                
            result = extract_thinking_action(msg.content)
            if not result:
                continue
                
            thinking, action = result
            yield ThinkingAction(
                conversation_id=conv.name,
                timestamp=msg.timestamp,
                thinking=thinking,
                action=action,
                message_index=i
            )

def get_thought_action_pairs(limit: int | None = None) -> list[ThinkingAction]:
    """Get all thinking/action pairs sorted by timestamp
    
    Args:
        limit: Optional limit on number of results to return
    
    Returns:
        List of ThinkingAction objects containing thinking tag content
        and subsequent actions
    """
    results = list(get_thinking_actions())
    results.sort(key=lambda x: x.timestamp)
    
    if limit:
        results = results[:limit]
        
    return results

def main():
    searcher = ThoughtSearcher()
    results = searcher.search("<thinking>I should write a patch to the file</thinking>")
    print(results)

if __name__ == "__main__":
    main()
