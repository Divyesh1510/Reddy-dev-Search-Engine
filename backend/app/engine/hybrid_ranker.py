from typing import List, Dict, Any
from app.config import RRF_K, WEIGHT_LEXICAL, WEIGHT_SEMANTIC

class HybridRanker:
    def __init__(
        self,
        rrf_k: int = RRF_K,
        weight_lexical: float = WEIGHT_LEXICAL,
        weight_semantic: float = WEIGHT_SEMANTIC
    ):
        self.rrf_k = rrf_k
        self.weight_lexical = weight_lexical
        self.weight_semantic = weight_semantic

    def fuse_ranks(
        self,
        lexical_results: List[Dict[str, Any]],
        semantic_results: List[Dict[str, Any]],
        top_k: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF) with weights:
        RRF_Score(d) = w_lex * (1 / (k + r_lex(d))) + w_sem * (1 / (k + r_sem(d)))
        """
        scores: Dict[str, float] = {}
        items_map: Dict[str, Dict[str, Any]] = {}
        lex_rank_map: Dict[str, int] = {}
        sem_rank_map: Dict[str, int] = {}

        # 1. Process Lexical Results (already sorted by BM25 ascending / relevance)
        for rank, item in enumerate(lexical_results, start=1):
            cid = item["chunk_id"]
            rrf_lex = self.weight_lexical * (1.0 / (self.rrf_k + rank))
            scores[cid] = scores.get(cid, 0.0) + rrf_lex
            lex_rank_map[cid] = rank
            if cid not in items_map:
                items_map[cid] = item.copy()

        # 2. Process Semantic Results (already sorted by similarity descending)
        for rank, item in enumerate(semantic_results, start=1):
            cid = item["chunk_id"]
            rrf_sem = self.weight_semantic * (1.0 / (self.rrf_k + rank))
            scores[cid] = scores.get(cid, 0.0) + rrf_sem
            sem_rank_map[cid] = rank
            if cid not in items_map:
                items_map[cid] = item.copy()
            else:
                # If lexical snippet didn't have highlight mark, or semantic has better snippet
                if "<mark>" not in items_map[cid].get("snippet", "") and item.get("snippet"):
                    items_map[cid]["snippet"] = item["snippet"]

        # 3. Sort by combined RRF score descending
        sorted_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        ranked_results: List[Dict[str, Any]] = []
        for cid in sorted_chunk_ids[:top_k]:
            res = items_map[cid]
            res["score"] = round(scores[cid], 5)
            res["lexical_rank"] = lex_rank_map.get(cid)
            res["semantic_rank"] = sem_rank_map.get(cid)
            ranked_results.append(res)

        return ranked_results

hybrid_ranker = HybridRanker()
