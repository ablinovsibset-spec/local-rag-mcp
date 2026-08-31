# Local RAG MCP

Local RAG assistant over a Russian-language company knowledge base, with MCP tools, hybrid retrieval, and locally hosted LLMs.

## Language

**Retrieval**

**Keyword Extraction**:
The pre-retrieval step where the small LLM distills a comma-separated list of key terms from the user's original query. Falls back to the original query on any failure.
_Avoid_: Query Expansion, keyword generation, query rewriting

**Hybrid Search**:
Retrieval that runs Vector Search and Full-Text Search in parallel and fuses their rankings into one list.
_Avoid_: hybrid fusion pipeline, combined search

**Vector Search**:
Retrieval by cosine similarity between the query embedding and chunk embeddings.
_Avoid_: semantic search, similarity search

**Full-Text Search (FTS)**:
Lexical retrieval (BM25) over chunk texts, matching exact terms from the query and extracted keywords.
_Avoid_: BM25 search, keyword search

**RRF**:
Reciprocal Rank Fusion — merging ranked lists by summing `1/(k + rank)` per document, with k = 60.
_Avoid_: reciprocal fusion, rank merging
