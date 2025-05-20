from typing import List, Dict, Any
from loguru import logger
from embedding.main import COLLECTIONS
from embedding.chatbot import retrieve_relevant_context, chat_completion_with_context
from embedding.recommendation import get_text_based_recommendations, get_similar_products
from models.chats import ChatMessageCreate

class QdrantService:
    @staticmethod
    def search_products(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for products using text-based recommendations.
        """
        try:
            results = get_text_based_recommendations(query, limit)
            return results
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []

    @staticmethod
    def process_message(payload: ChatMessageCreate) -> Dict[str, Any]:
        """
        Process a chat message and return relevant product recommendations.
        """
        try:
            # Get relevant context from the message
            context = retrieve_relevant_context(payload.content)
            
            # Get product recommendations
            recommendations = get_text_based_recommendations(payload.content, limit=5)
            
            # Generate response using chat completion
            response = chat_completion_with_context(payload.content, context)
            
            return {
                "response": response.get("response", "I couldn't find relevant information."),
                "recommendations": recommendations,
                "context": context
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "recommendations": [],
                "context": []
            }

    @staticmethod
    def get_similar_products(product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get similar products based on a product ID.
        """
        try:
            return get_similar_products(product_id, limit)
        except Exception as e:
            logger.error(f"Error getting similar products: {str(e)}")
            return [] 