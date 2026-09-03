import os
import subprocess
import sys
import textwrap
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent


def test_importing_retrieval_modules_is_side_effect_free():
    """Import must not load models, touch FAISS indexes, or fetch encodings."""
    code = textwrap.dedent(
        """
        import importlib.abc
        import sys
        import time

        BLOCKED = {"sentence_transformers", "tiktoken"}

        class Blocker(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                root = fullname.split(".")[0]
                if root in BLOCKED:
                    raise AssertionError(
                        f"import-time use of heavy dependency: {fullname}"
                    )
                return None

        sys.meta_path.insert(0, Blocker())

        import faiss

        def _boom(*args, **kwargs):
            raise AssertionError("FAISS index touched at import time")

        faiss.read_index = _boom
        faiss.write_index = _boom

        start = time.time()
        import rag.embed
        import rag.chunk
        import rag.query
        import rag.build_index
        elapsed = time.time() - start

        import rag.chunk as c
        import rag.query as q

        assert q.index is None, "FAISS index loaded at import time"
        assert q.chunks == [], "chunks loaded at import time"
        assert c.encoder is None, "tokenizer loaded at import time"
        assert elapsed < 5, f"import took {elapsed:.2f}s"
        print("OK")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(SRC_DIR),
        capture_output=True,
        text=True,
        env=dict(os.environ, PYTHONPATH=""),
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("OK")
