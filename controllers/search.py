from fastapi import APIRouter, HTTPException
from models.products import Product, ProductModel, ProductCreate
from embedding.generate_embeddings import query_embedding   
from agent.parsing_agent import ParsingAgent
from services.search import SearchServices
from services.products import ProductServices

router = APIRouter(prefix="/search", tags=["search"])
@router.get("/")
def search(query: str, collection_name: str = "product_name_embeddings", limit: int = 5):
    # schema = ParsingAgent.initiate_parsing(query)
    # Schema = str(schema)
    # print("❤️❤️❤️❤️❤️Schema:", Schema)
    results = SearchServices.search(query, collection_name=collection_name, limit=limit)


    return results

