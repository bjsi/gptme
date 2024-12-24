import contextlib
from datetime import datetime
from dataclasses import dataclass
import os
from typing import Generator, List
import re
from gptme.logmanager import get_conversations, Log
import warnings

from gptme.tools import init_tools
from gptme.tools.base import ToolUse

@dataclass
class PlanActionOutcome:
    conversation_id: str
    timestamp: datetime
    planning: str
    action: ToolUse
    outcome: str | None
    score: float | None
    message_index: int
    outcome_index: int | None

    def to_searchable_text(self) -> str:
        """Convert planning/action/outcome to searchable text format"""
        text = f"# Planning\n{self.planning}"
        return text
    
    def to_action_outcome_text(self, format: str = "markdown", redact = False) -> str:
        """Convert planning/action/outcome to concise text format"""
        action_lines = self.action.content.split("\n")
        action_line = action_lines[0].strip() + "\n"
        tool = self.action.tool
        # note - hide patch content to avoid confusion
        if tool == "patch": action_line = ""
        args = self.action.args

        # logic here is to improve generalization
        if redact:
            redact_replacement = 'xxxxx'
            # Redact content within quotes in action_line
            action_line = re.sub(r'[\'"].*?[\'"]', f"'{redact_replacement}'", action_line)
            action_line = re.sub(r'`.*?`', f"`{redact_replacement}`", action_line)
            # Redact content within quotes in outcome
            outcome_text = re.sub(r'[\'"].*?[\'"]', f"'{redact_replacement}'", self.outcome) if self.outcome else None
            outcome_text = re.sub(r'`.*?`', f"`{redact_replacement}`", outcome_text) if outcome_text else None
        else:
            outcome_text = self.outcome

        action_formatted = ""
        # note - not including <tool-use> tag to avoid confusing the model into thinking it just ran a tool
        if format == "markdown":
            action_formatted = f"Action:\n```{tool}{' ' + ' '.join(args) if args else ''}\n{action_line}\n```"
        elif format == "xml": 
            action_formatted = f"Action:\n<{tool}{f" args='{' '.join(args)}'" if args else ''}>\n{action_line}</{tool}>"
        return f"{action_formatted}\nOutcome: {outcome_text} (score: {self.score})"

class ThoughtSearcher:
    def __init__(self, tool_format = "markdown"):
        self.index_name = "thought_search"
        self._plan_actions: List[PlanActionOutcome] | None = None
        self._encoded = False
        self.load_model()
        self.tool_format = tool_format

    def load_model(self):
        warnings.filterwarnings('ignore')
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            from ragatouille import RAGPretrainedModel # slow
            if self.index_exists():
                self.rag = RAGPretrainedModel.from_index(self.index_path(), verbose=-1)
            else:
                self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0", verbose=-1)
        warnings.resetwarnings()

    def index_path(self) -> str:
        return f".ragatouille/colbert/indexes/{self.index_name}"

    def index_exists(self) -> bool:
        return os.path.exists(self.index_path())

    def create_index(self, if_not_exists: bool = True):
        """Create a persistent index of all planning/action/outcome triplets"""
        if if_not_exists and self.index_exists():
            self.rag.from_index(self.index_path())
            return
        
        texts = [pa.to_searchable_text() for pa in self.plan_actions]
        
        # Create metadata for each document to map back to PlanActionOutcome objects
        metadatas = [
            {
                "index": i,
                "conversation_id": pa.conversation_id,
                "timestamp": pa.timestamp.isoformat(),
                "message_index": pa.message_index,
                "outcome_index": pa.outcome_index
            } 
            for i, pa in enumerate(self.plan_actions)
        ]

        # Create the index
        warnings.filterwarnings('ignore')
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            self.rag.index(
                collection=texts,
                document_ids=[str(i) for i in range(len(texts))],
                document_metadatas=metadatas,
                index_name=self.index_name,
                max_document_length=512,  # Adjust based on your typical document length
                split_documents=False  # Keep documents whole since we're already splitting them
            )
        warnings.resetwarnings()
        self._encoded = True

    @property
    def plan_actions(self) -> List[PlanActionOutcome]:
        """Lazy load and cache planning/action/outcome triplets"""
        if self._plan_actions is None:
            self._plan_actions = get_plan_action_outcome_triples(tool_format=self.tool_format)
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
        """Search for planning/action/outcome triplets relevant to query"""
        warnings.filterwarnings('ignore')
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            # Try to use existing index, fall back to in-memory if not available
            try:
                results = self.rag.search(query, k=k, index_name=self.index_name)
            except (ValueError, FileNotFoundError):
                # Fall back to in-memory search if index doesn't exist
                self.encode_thoughts()
                results = self.rag.search_encoded_docs(query, k=k)
        warnings.resetwarnings()
        
        # Map search results back to PlanActionOutcome objects with scores
        matches = []
        for result in results:
            idx = result["document_metadata"]["index"]
            score = result["score"]
            matches.append((self.plan_actions[idx], score))
        return sorted(matches, key=lambda x: x[1], reverse=True)

def extract_plan_action(content: str) -> tuple[str, ToolUse] | None:
    """Extract planning and action content from a message."""
    planning_match = re.search(r'<planning>(.*?)</planning>', content, re.DOTALL)
    if not planning_match: return None
    action_match = next(ToolUse.iter_from_content(content), None)
    if not action_match: return None
    return (
        planning_match.group(1).strip(),
        action_match,
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
    score_match = re.search(r'<score>.*?(-?\d*\.?\d+).*?</score>', outcome)
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

def get_plan_actions(tool_format = "markdown") -> Generator[PlanActionOutcome, None, None]:
    """Get all planning+action pairs and their subsequent outcomes from conversations."""
    init_tools() # otherwise tool use parsing will fail
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
                
            # Look for planning/action pairs
            if '<planning>' in msg.content:
                result = extract_plan_action(msg.content)
                if not result: continue
                
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

def get_plan_action_outcome_triples(limit: int | None = None, tool_format: str = "markdown") -> list[PlanActionOutcome]:
    init_tools() # otherwise tool use parsing will fail 
    results = list(get_plan_actions(tool_format))
    results.sort(key=lambda x: x.timestamp)
    if limit: results = results[:limit]
    return results

_searcher: ThoughtSearcher | None = None

def search_memory(query: str, k: int = 5, tool_format = "markdown") -> List[tuple[PlanActionOutcome, float]]:
    global _searcher
    if _searcher is None:
        _searcher = ThoughtSearcher(tool_format=tool_format)
        _searcher.create_index()
    return _searcher.search(query, k)

if __name__ == "__main__":
    init_tools()
    xs = get_plan_action_outcome_triples(limit=10)
    for x in xs:
        print(x.to_action_outcome_text(redact=True, format="xml"))
