# Local RAG/MCP Knowledge Base Assistant

# 📋 The Problem

- **Growing Documentation**: Knowledge scattered across files
- **Information Retrieval**: Hard to find answers without keywords
- **Privacy Concerns**: Cloud solutions may not comply with policies

```
Users → Search → Answer = 😫
```

# ✨ The Solution

A **local, intelligent Q&A system** using:

- **RAG**: Semantic search over documentation
- **MCP**: Dynamic document access
- **Local LLM**: Privacy-preserving answers (LM Studio)

# ✨ Key Benefits

- ✅ Privacy-first (runs locally)
- ✅ No API costs
- ✅ Fast semantic search
- ✅ Intelligent document access
- ✅ Complete data control

# 🏗️ Architecture - Top Level

```
┌──────────────────────┐
│   User Interface     │ (CLI)
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  [RAG]       [MCP]
   Query      Tools
     │           │
     └─────┬─────┘
           ▼
    [LM Studio LLM]
```

# 🏗️ Architecture - Storage

```
┌────────────────┐
│  FAISS Index   │ Vector Database
│  + MCP Tools   │
└────────┬───────┘
         │
    ┌────▼─────┐
    │   docs/  │
    │directory │
    └──────────┘
```

# 🔍 RAG Pipeline

1. Document Loading → Read .md, .txt, .pdf, .docx
2. Chunking → Split into 700-char chunks
3. Embedding → LM Studio embeddings (multilingual)
4. Indexing → Build FAISS vector index
5. Query → Hybrid Search: Keyword Extraction, then Vector Search +
   Full-Text Search in parallel, fused with RRF, top 5 chunks
6. Prompt Building → Create context-aware prompt
7. LLM Generation → Get answer from model

# 🔍 Why FAISS?

- Fast vector similarity search
- Lightweight and memory-efficient
- No external dependencies
- Perfect for local deployments
- Millions of vectors supported

# 🔧 MCP - Model Context Protocol

MCP provides **standardized interface** for LLM tool access:

```python
read_document(file_path)
list_documents()
search_documents(query)
```

# 🔧 MCP Benefits

- Tool Use by LLM
- Real-time document access
- Standardized interface
- Easy to extend
- Local tool execution

# 💻 Tech Stack

```
Language:      Python 3.10+
Vector DB:     FAISS
Full-Text:     SQLite FTS5 (bm25, RU/EN Snowball stemming via PyStemmer)
Embeddings:    nomic-embed-text-v2-moe (LM Studio, multilingual)
LLM:           LM Studio (OpenAI-compatible API): gpt-oss-20b answers, qwen3-0.6b-mlx assists
MCP:           FastMCP
```

# 📊 Retrieval Benchmark

Three arms over the real corpus (258 chunks, 12 Russian queries drafted from
corpus content; file-level relevance labels — agent-drafted, pending human review).
Rerun with one command: `python main.py benchmark` (requires a built index and
LM Studio serving the embedding models).

| Arm | recall@5 | precision@5 | latency (ms/query) |
|-----|----------|-------------|--------------------|
| Vector (nomic-v1.5, English-focused) | 0.47 | 0.17 | 12 |
| Vector (nomic-v2-moe, multilingual) | 0.92 | 0.35 | 19 |
| Hybrid (multilingual + FTS + RRF) | 0.92 | 0.31 | 1896 |

(Representative run; hybrid recall varies ±0.04 run-to-run with the
Keyword Extraction LLM, occasionally hitting its 10s timeout and degrading
to the original query.)

Reading the table:

- **Multilingual embeddings are the big win**: recall@5 doubles (0.47 → 0.92)
  over the English-focused baseline — the stand-in for the original
  `all-MiniLM-L6-v2`, which LM Studio cannot serve.
- **Hybrid Search holds the recall** and adds lexical hits for rare terms,
  abbreviations, and exact file/command names (visible in live queries such
  as `migration_policy` or `flask-limiter`), at the cost of some precision
  (FTS adds lexically-matching neighbors) and latency — the Keyword
  Extraction LLM call dominates the ~1.9s.
- **Model note**: the spec planned `multilingual-e5-small`, but no e5 build
  could be served correctly through this LM Studio's embeddings endpoint
  (XLM-R "BERT" GGUFs produce degenerate similarity; the MLX backend
  rejects BERT). The multilingual nomic-v2-moe runs on the engine path that
  pools correctly and is a config-constant swap
  (`EMBEDDING_MODEL` in `src/config.py`).

# 📁 Project Structure

```
src/
├── config.py           Configuration
├── main.py             CLI entry point
├── assistant.py        Main orchestrator
├── rag/
│   ├── ingest.py      Load documents
│   ├── chunk.py       Split text
│   ├── embed.py       Generate embeddings
│   ├── build_index.py Build FAISS index
│   └── query.py       Retrieve & generate
├── mcp/
│   ├── server.py      MCP tool definitions
│   └── client.py      MCP client wrapper
└── docs/              Documentation
```

# 🚀 Index Building (Setup)

```
$ python main.py build-index

1. Load documents
  ↓
2. Split into chunks
  ↓
3. Generate embeddings
  ↓
4. Build FAISS index
  ↓
5. Save files
```

# 🚀 Query Processing (Runtime)

```
User Question
  ↓
Embed question
  ↓
Search FAISS → Top 5 chunks
  ↓
LLM decides: Use MCP tools?
  ↓
Build prompt + context
  ↓
Call LM Studio (gpt-oss-20b)
  ↓
Return answer + sources
```

# ✨ Core Features

- **Semantic Search**: Find by meaning, not keywords
- **Multi-format**: .md, .txt, .pdf, .docx files
- **Source Attribution**: Shows document sources
- **MCP Tools**: LLM can read full documents
- **No External APIs**: Runs locally only
- **Fast Retrieval**: Sub-second search

# ⚙️ Configuration Options

```python
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v2-moe"
CHAT_MODEL = "openai/gpt-oss-20b"
TOOL_DECISION_MODEL = "qwen3-0.6b-mlx"
TOP_K = 5
```

# 🎬 Live Demo - Starting

```bash
$ python main.py
```

Output:
```
🤖 Company Knowledge Base
Ask questions about documentation
Type 'exit' to stop
```

# 🎬 Demo - Query 1

```
❓ What are company values?

🤖 Innovation, integrity, collaboration

📚 Sources:
  • Loan Rangers Team.md
  • Info Security.md
```

# 🎬 Demo - Query 2

```
❓ What documents do we have?

🤖 [Uses MCP list_documents]
  • Loan Rangers Team.md
  • Information Security.md
  • Services.md
```

# 🎬 Demo - Query 3

```
❓ Full security policy?

🤖 [Uses MCP read_document]
[Full document content...]
```

# 🔐 Security - Local vs Cloud

**Cloud**: Data → Internet → Server
- ⚠️ Network transmission
- ⚠️ External storage
- ⚠️ Subscription costs

**Local**: Data → Local System
- ✅ No transmission
- ✅ Local storage only
- ✅ No costs

# 🔐 Implementation Safeguards

- **MCP Sandbox**: Prevents path traversal
- **Local Storage**: Documents stay on device
- **No Telemetry**: No tracking
- **Offline Ready**: Works without internet

# ⚡ Performance Benchmarks

```
Index Building:   ~30s (one-time)
Query Embedding:  ~50ms
FAISS Search:     ~5ms
LLM Generation:   2-5s
Total Cycle:      2-6s
```

# ⚡ Tuning for Speed

```python
# Faster (smaller answer model):
CHAT_MODEL = "qwen3-0.6b-mlx"  # not recommended for answer quality

# Faster retrieval:
TOP_K = 3
CHUNK_SIZE = 500
```

# 🚢 Deployment - Single Machine

```
1. Install LM Studio & Python deps; load the models from src/config.py
2. Copy docs/ to server
3. Build index
4. Run with nohup

$ nohup python main.py > log &
```

# 🚢 Scaling - Option 1: FastAPI

```
[HTTP Clients]			[HTTP Clients + Webllm]
       ↓        						 ↓
   [FastAPI]     				 [FastAPI]
       ↓         					 ↓
[LM Studio + FAISS]      			  [FAISS]
```

# 🚢 Scaling - Option 2: Distributed

```
[Clients] → [Load Balancer]
             ↓
      [Multiple Retrievers]
```

# 🚢 Storage Scaling

```
Docs     Index      Build
10 MB    ~2 MB      ~5s
100 MB   ~20 MB     ~30s
1 GB     ~200 MB    ~5min
```

# 🔮 Phase 2: Enhanced Features

- ☐ Web UI (Streamlit)
- ☐ API endpoints
- ☐ Multi-language support
- ☐ Document versioning
- ☐ Fine-tuned embeddings

# 🔮 Phase 3: Advanced

- ☐ Conversation memory
- ☐ Multi-hop reasoning
- ☐ Metadata filtering
- ☐ Feedback loop
- ☐ Analytics dashboard

# 🔮 Phase 4: Enterprise

- ☐ User authentication
- ☐ Audit logging
- ☐ Role-based access
- ☐ LLM fine-tuning
- ☐ Cost analysis

# 📊 Why This Works

| Aspect | Traditional | Our RAG |
|--------|---|---|
| **Understanding** | Keywords | Semantic |
| **Answers** | Documents | Direct |
| **Privacy** | Cloud | Local |
| **Cost** | Subscription | One-time |
| **Speed** | Slow | Sub-second |

# ✅ What You Have Now

- Local privacy-first knowledge base
- Fast semantic search (FAISS)
- Intelligent tool use (MCP)
- Maintainable Python code
- Foundation for enterprise features

# 🙋 Quick Reference

```bash
# Build index
python main.py build-index

# Run interactively
python main.py

# Check config
cat config.py
```

# 📚 Resources

- **Code**: MobilaName/local-rag-mcp
- **FAISS**: facebook/faiss
- **LM Studio**: lmstudio.ai
- **FastMCP**: github.com/jlowin/fastmcp
- **Transformers**: huggingface.co

**Thank You!**
