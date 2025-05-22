from typing import Dict, Any, Optional
from loguru import logger
from models.chats import ChatMessageCreate
from embedding.chatbot import retrieve_relevant_context, chat_completion_with_context
from embedding.main import COLLECTIONS
from services.search import SearchServices
from services.qdrant import QdrantService
from services.policy import PolicyService

class ManagerService:
    @staticmethod
    def process_message(payload: ChatMessageCreate) -> Dict[str, Any]:
        """
        Process a message and coordinate between different agents to provide a response.
        """
        try:
            # Get relevant context from the message
            context = retrieve_relevant_context(payload.content)
            
            # Determine the type of query and route to appropriate service
            query_type = ManagerService._determine_query_type(payload.content)
            
            if query_type == "product":
                # Use QdrantService for product-related queries
                result = QdrantService.process_message(payload)
            elif query_type == "policy":
                # Use PolicyService for policy-related queries
                result = PolicyService.process_message(payload)
            else:
                # Use general search for other queries
                search_results = SearchServices.search(
                    query=payload.content,
                    collection_name=COLLECTIONS["faqs"],
                    limit=3
                )
                response = chat_completion_with_context(payload.content, context)
                result = {
                    "response": response.get("response", "I couldn't find relevant information."),
                    "search_results": search_results,
                    "context": context
                }
            
            return result
        except Exception as e:
            logger.error(f"Error processing message in manager: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "error": str(e)
            }

    @staticmethod
    def _determine_query_type(content: str) -> str:
        """
        Determine the type of query based on its content.
        """
        content_lower = content.lower()
        
        # Keywords for product-related queries
        product_keywords = [
            "sản phẩm", "mua", "giá", "hàng", "sale", "khuyến mãi",
            "tìm kiếm", "so sánh", "đánh giá", "review"
        ]
        
        # Keywords for policy-related queries
        policy_keywords = [
            "chính sách", "điều khoản", "quy định", "bảo hành",
            "đổi trả", "vận chuyển", "thanh toán", "hoàn tiền"
        ]
        
        # Check for product-related keywords
        if any(keyword in content_lower for keyword in product_keywords):
            return "product"
        
        # Check for policy-related keywords
        if any(keyword in content_lower for keyword in policy_keywords):
            return "policy"
        
        # Default to general query
        return "general" 