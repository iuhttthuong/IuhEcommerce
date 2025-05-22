from typing import Dict, Any
from loguru import logger
from models.chats import ChatMessageCreate
from embedding.chatbot import retrieve_relevant_context, chat_completion_with_context
from embedding.main import COLLECTIONS
from services.search import SearchServices

class PolicyService:
    @staticmethod
    def process_message(payload: ChatMessageCreate) -> Dict[str, Any]:
        """
        Process a policy-related message and return relevant information.
        """
        try:
            # print("😒👍👍😒😒❤️🤣😁😉😎payload.content", payload.content)
            # Get relevant context from the message
            context = retrieve_relevant_context(payload.content)
            # print("😒👍👍😒😒❤️🤣😁😉😎context", context)
            # Search for policy-related information
            search_results = SearchServices.search(
                payload=payload.content,
                collection_name=COLLECTIONS["faqs"],
                limit=3
            )
            
            # Generate response using chat completion with context
            response = chat_completion_with_context(payload.content, context)
            
            return {
                "response": response.get("response", "I couldn't find relevant policy information."),
                "policy_info": search_results.get("results", []),
                "context": context
            }
        except Exception as e:
            logger.error(f"Error processing policy message: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your policy-related request.",
                "policy_info": [],
                "context": []
            }

    @staticmethod
    def get_policy_info(query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Get policy information based on a query.
        """
        try:
            search_results = SearchServices.search(
                payload=query,
                collection_name=COLLECTIONS["faqs"],
                limit=limit
            )
            return search_results
        except Exception as e:
            logger.error(f"Error getting policy info: {str(e)}")
            return {"results": []} 