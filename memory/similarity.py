# sandys_law_a7do/memory/similarity.py

def similarity_score(a: dict, b: dict) -> float:
    """
    Simple structural similarity between feature dicts.
    """
    if not a or not b:
        return 0.0

    shared = 0
    for k in a:
        if k in b and a[k] == b[k]:
            shared += 1

    return shared / max(len(a), len(b))
