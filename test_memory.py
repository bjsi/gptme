from gptme.memory import ThoughtSearcher

def main():
    # Initialize searcher
    searcher = ThoughtSearcher()
    
    # Example searches
    queries = [
        "file operations",
        "error handling",
        "git commands",
    ]
    
    for query in queries:
        print(f"\nSearching for: {query}")
        results = searcher.search(query, k=2)
        
        for r in results:
            print("\n---")
            print(f"Conversation: {r.conversation_id}")
            print(f"Message #: {r.message_index}")
            print(f"Timestamp: {r.timestamp}")
            print(f"Thinking: {r.thinking}")
            print(f"Action: {r.action}")

if __name__ == "__main__":
    main()

