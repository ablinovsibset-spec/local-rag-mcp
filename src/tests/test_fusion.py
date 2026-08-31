from rag.fusion import rrf_fuse


def test_doc_in_both_lists_outranks_doc_in_one():
    fused = rrf_fuse([["a", "b"], ["b", "c", "d"]])
    assert fused[0] == "b"  # rank 2 + rank 1 beats any single-list score
    assert set(fused) == {"a", "b", "c", "d"}


def test_disjoint_lists_interleave_by_rank():
    fused = rrf_fuse([[1, 2, 3], [4, 5, 6]])
    assert len(fused) == 6
    # 1 and 4 (both rank 1) lead, ahead of 2 and 5 (both rank 2)
    assert set(fused[:2]) == {1, 4}
    assert set(fused[2:4]) == {2, 5}
    assert set(fused[4:]) == {3, 6}


def test_single_list_preserved():
    assert rrf_fuse([["x", "y", "z"]]) == ["x", "y", "z"]


def test_empty_leg_contributes_nothing():
    assert rrf_fuse([["x", "y"], []]) == ["x", "y"]
    assert rrf_fuse([[], ["x", "y"]]) == ["x", "y"]


def test_all_empty_legs_return_empty():
    assert rrf_fuse([[], []]) == []


def test_top_n_cuts_the_fused_list():
    docs = [str(i) for i in range(30)]
    fused = rrf_fuse([docs, list(reversed(docs))], top_n=5)
    assert len(fused) == 5


def test_depth_handling_deep_ranks_score_less():
    # a at rank 20 in one list vs b at rank 20 in BOTH lists: b must win
    long_list = [f"doc{i}" for i in range(20)]
    fused = rrf_fuse([long_list, list(reversed(long_list))])
    # doc19 (rank 20 in list1, rank 1 in list2) and doc0 (rank 1 + rank 20)
    # both score 1/60 + 1/80; mid docs (rank 10 + rank 11) score 2x ~1/70
    assert fused[0] in ("doc0", "doc19")
    assert "doc0" in fused[:4] and "doc19" in fused[:4]


def test_k_constant_is_60_by_default():
    # with k=60: rank1 score 1/61; two-list winner for equal ranks
    import rag.fusion as fusion

    assert fusion.RRF_K == 60


def test_document_ids_may_be_tuples():
    fused = rrf_fuse([[("a.md", 0), ("b.md", 1)], [("b.md", 1), ("c.md", 2)]])
    assert fused[0] == ("b.md", 1)
