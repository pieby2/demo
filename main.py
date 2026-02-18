import argparse
import sys
import time
import numpy as np

# Internal imports
from data.messages import get_all_messages, get_categories
from embeddings.embedding_service import EmbeddingService
from utils.similarity import find_top_k

# Colors for CLI
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[96m"
RESET = "\033[0m"

def get_color_for_score(score):
    if score >= 0.7:
        return GREEN
    elif score >= 0.45:
        return YELLOW
    return RED

def main():
    # 1. Setup argparse
    parser = argparse.ArgumentParser(description="Find similar messages using cosine similarity.")
    parser.add_argument("query", nargs="?", help="The text to search for")
    parser.add_argument("--top", "-k", type=int, default=3, help="How many results to show (default: 3)")
    parser.add_argument("--category", "-c", type=str, choices=get_categories(), help="Filter by category")
    parser.add_argument("--add", help="Add a temp message to the DB selection")
    parser.add_argument("--add-category", help="Category for the new message")
    
    args = parser.parse_args()

    # 2. Load model & data
    print("Initializing...")
    service = EmbeddingService()
    messages = get_all_messages()

    # Bonus: Add dynamic message
    if args.add:
        cat = args.add_category or "custom"
        messages.append({"text": args.add, "category": cat})
        print(f"Added temporary message: '{args.add}' ({cat})")

    # Embed all messages
    print(f"Embedding {len(messages)} messages...", end=" ")
    all_texts = [m["text"] for m in messages]
    # This might take a second on first run
    msg_embeddings = service.embed_texts(all_texts)
    print("Done.\n")

    # 3. Get User Input
    query_text = args.query
    if not query_text:
        # Interactive mode
        try:
            print("-" * 50)
            query_text = input("Enter your message: ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            sys.exit(0)

    if not query_text:
        print("Empty query. Exiting.")
        sys.exit(1)

    # 4. Search
    start_ts = time.time()
    query_vec = service.embed_text(query_text)
    
    results = find_top_k(
        query_vec, 
        msg_embeddings, 
        messages, 
        k=args.top, 
        category=args.category
    )
    
    duration = time.time() - start_ts

    # 5. Output
    print(f"\nTop {len(results)} matches for: '{query_text}'")
    print("-" * 50)
    
    if not results:
        print("No matches found.")
    
    for i, res in enumerate(results, 1):
        score_val = res['score'] * 100
        color = get_color_for_score(res['score'])
        
        print(f"{i}. [{color}{score_val:.1f}%{RESET}] [{BLUE}{res['category']}{RESET}] {res['text']}")
        
    print("-" * 50)
    print(f"Time taken: {duration:.4f} sec\n")

if __name__ == "__main__":
    main()
