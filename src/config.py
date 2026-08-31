# Configuration for Company Knowledge Base Assistant

# Document directory - update this to point to your company documentation
DOCUMENTS_DIR = "./docs"

# Chunking configuration
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# FAISS index paths (relative to src directory)
FAISS_INDEX_PATH = "index.faiss"
CHUNKS_PATH = "chunks.pkl"

# LM Studio configuration (OpenAI-compatible API)
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
CHAT_MODEL = "openai/gpt-oss-20b"        # final RAG answer
TOOL_DECISION_MODEL = "qwen3-0.6b-mlx"   # MCP-tool decision / Keyword Extraction
CHAT_TIMEOUT = 120                       # seconds, final answer
TOOL_DECISION_TIMEOUT = 10               # seconds, tool decision / Keyword Extraction

# RAG retrieval configuration
TOP_K = 5
