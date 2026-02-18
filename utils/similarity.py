"""
Logic for calculating cosine similarity and finding top matches.
"""

import numpy as np

def cosine_similarity(vec_a, vec_b):
    """
    Standard cosine similarity: (A . B) / (|A| * |B|)
    Returns a float between -1 and 1.
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def find_top_k(query_vec, message_vecs, messages, k=3, category=None):
    """
    Finds the top k messages that match the query vector.
    """
    results = []

    for idx, msg in enumerate(messages):
        # Filter by category if requested
        if category and msg["category"] != category:
            continue

        # Calculate score
        score = cosine_similarity(query_vec, message_vecs[idx])
        
        results.append({
            "text": msg["text"],
            "category": msg["category"],
            "score": score,
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top k
    return results[:k]
