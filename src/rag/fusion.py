"""RRF: Reciprocal Rank Fusion — merging ranked lists by summing
1/(k + rank) per document, with k = 60 (see CONTEXT.md)."""

RRF_K = 60


def rrf_fuse(ranked_lists, k=RRF_K, top_n=None):
    """Fuse ranked lists of hashable document ids into one ranking.

    Each list is best-first; a document's score is the sum of
    1/(k + rank) over every list it appears in. Ties keep first-seen
    order. With top_n given, the fused list is cut to that length.
    """
    scores = {}
    order = []
    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked, start=1):
            if doc not in scores:
                scores[doc] = 0.0
                order.append(doc)
            scores[doc] += 1.0 / (k + rank)
    fused = sorted(order, key=lambda doc: -scores[doc])
    return fused[:top_n] if top_n is not None else fused
