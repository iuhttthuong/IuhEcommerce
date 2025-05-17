from db import Session
from repositories.search import SearchRepository

class SearchServices:
    @staticmethod
    def search(payload: str, collection_name = "product_name_embeddings", limit: int = 5):
        """
        Tìm kiếm sản phẩm trong cơ sở dữ liệu.
        """
        # Tìm kiếm ANN trong collection
        search_result = SearchRepository.semantic_search(payload, collection_name=collection_name, limit=limit)
        return search_result