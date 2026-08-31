# Configuration for Company Knowledge Base Assistant

# Document directory - update this to point to your company documentation
DOCUMENTS_DIR = "./docs"

# Chunking configuration
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

# Embedding model (LM Studio embeddings endpoint).
# Multilingual (100+ languages incl. Russian). nomic-bert-moe architecture —
# the engine path that pools correctly; XLM-R/e5 BERT GGUFs served by this
# LM Studio build produce degenerate similarity (see benchmark notes).
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v2-moe"
EMBEDDING_TIMEOUT = 60                     # seconds, embedding requests

# FAISS index paths (relative to src directory)
FAISS_INDEX_PATH = "index.faiss"
CHUNKS_PATH = "chunks.pkl"
FTS_INDEX_PATH = "fts_index.db"

# LM Studio configuration (OpenAI-compatible API)
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
CHAT_MODEL = "openai/gpt-oss-20b"        # final RAG answer
TOOL_DECISION_MODEL = "qwen3-0.6b-mlx"   # MCP-tool decision / Keyword Extraction
CHAT_TIMEOUT = 120                       # seconds, final answer
TOOL_DECISION_TIMEOUT = 10               # seconds, tool decision / Keyword Extraction

# RAG retrieval configuration
TOP_K = 5
