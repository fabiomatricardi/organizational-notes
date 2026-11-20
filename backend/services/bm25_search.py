"""
Pure Python BM25 search over log entries.
No external dependencies required.
"""
import math
import re
from backend.services.entries import get_all_entries


def tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r'\b[a-z0-9]+\b', text)
    return [t for t in tokens if len(t) > 1]


def bm25_search(query: str, entries: list[dict], top_k: int = 10) -> list[dict]:
    if not entries or not query.strip():
        return []

    k1 = 1.5
    b = 0.75

    doc_texts = []
    for entry in entries:
        parts = [entry.get("activity", "")]
        if entry.get("follow_up"):
            parts.append(entry["follow_up"])
        doc_texts.append(" ".join(parts))

    tokenized_docs = [tokenize(text) for text in doc_texts]
    doc_count = len(tokenized_docs)
    avg_dl = sum(len(d) for d in tokenized_docs) / doc_count if doc_count else 1

    df = {}
    for doc in tokenized_docs:
        seen = set()
        for token in doc:
            if token not in seen:
                df[token] = df.get(token, 0) + 1
                seen.add(token)

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    scores = []
    for i, doc in enumerate(tokenized_docs):
        dl = len(doc)
        score = 0.0
        tf_map = {}
        for token in doc:
            tf_map[token] = tf_map.get(token, 0) + 1

        for qt in query_tokens:
            if qt not in tf_map:
                continue
            tf = tf_map[qt]
            doc_freq = df.get(qt, 0)
            idf = math.log((doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avg_dl)))
            score += idf * tf_norm

        if score > 0:
            scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    results = []
    for idx, score in scores[:top_k]:
        entry = dict(entries[idx])
        entry["score"] = round(score, 4)
        results.append(entry)

    return results


async def search_entries(query: str, top_k: int = 10) -> list[dict]:
    entries = await get_all_entries(limit=5000)
    return bm25_search(query, entries, top_k)
