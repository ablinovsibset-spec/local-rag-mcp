from benchmark import precision_at_k, recall_at_k


def _hit(source):
    return {"source": source, "text": "x", "chunk_id": 0}


def test_recall_counts_file_level_hits():
    hits = [_hit("a/Прокси.md"), _hit("b/Миграции.md"), _hit("c/other.md")]
    relevant = {"Прокси.md", "Миграции.md", "Docker.md"}
    assert recall_at_k(hits, relevant, k=3) == 2 / 3


def test_precision_counts_file_level_hits():
    hits = [_hit("a/Прокси.md"), _hit("b/Миграции.md"), _hit("c/other.md")]
    relevant = {"Прокси.md"}
    assert precision_at_k(hits, relevant, k=3) == 1 / 3


def test_duplicate_files_from_same_document_count_once():
    hits = [_hit("a/Прокси.md"), _hit("a/Прокси.md"), _hit("b/other.md")]
    relevant = {"Прокси.md"}
    assert precision_at_k(hits, relevant, k=3) == 1 / 2
    assert recall_at_k(hits, relevant, k=3) == 1.0


def test_k_cuts_the_hit_list():
    hits = [_hit(f"a/f{i}.md") for i in range(10)]
    relevant = {f"f{i}.md" for i in range(10)}
    assert recall_at_k(hits, relevant, k=5) == 0.5


def test_empty_hits_score_zero():
    assert precision_at_k([], {"x.md"}) == 0.0
    assert recall_at_k([], {"x.md"}) == 0.0
