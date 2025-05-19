import os
from typing import List, Dict, Any, Optional
import openai
from qdrant_client import QdrantClient
from env import env
from embedding.generate_embeddings import query_embedding
from embedding.main import COLLECTIONS
from typing import List, Dict, Any, Optional
import json
import re

# Configure OpenAI API
openai.api_key = env.OPENAI_API_KEY

# Connect to Qdrant
qdrant = QdrantClient(f"http://localhost:{env.QD_PORT}")

def retrieve_relevant_context(query_text: str, limit_per_collection: int = 3, score_threshold: float = 0.6) -> str:
    """
    Retrieve relevant context from different collections based on query text
    """
    try:
        # Generate query embedding
        query_vector = query_embedding(query_text)
        
        contexts = []
        
        # Search products with lower threshold to capture more results
        product_results = qdrant.search(
            collection_name=COLLECTIONS["products"],
            query_vector={"default": query_vector},
            limit=limit_per_collection + 2,  # Get more results to ensure we find relevant matches
            with_payload=True,
            score_threshold=score_threshold  # Lower threshold to include more matches
        )
        
        # Check if product is specifically mentioned by name
        product_name_match = None
        for product in product_results:
            product_name = product.payload.get('name', '')
            # Using regex to find product name regardless of case or diacritics
            if product_name and re.search(re.escape(product_name), query_text, re.IGNORECASE):
                product_name_match = product
                break
                
        # If we have an exact name match, prioritize it
        if product_name_match:
            contexts.append(f"PRODUCT INFORMATION (EXACT MATCH):\n{product_name_match.payload.get('text_content', '')}")
            
        # Add remaining products
        for product in product_results:
            if product != product_name_match:  # Skip if it's the exact match we already added
                contexts.append(f"PRODUCT INFORMATION:\n{product.payload.get('text_content', '')}")
        
        # Search FAQs
        faq_results = qdrant.search(
            collection_name=COLLECTIONS["faqs"],
            query_vector={"default": query_vector},
            limit=limit_per_collection,
            with_payload=True
        )
        
        for faq in faq_results:
            contexts.append(f"FAQ INFORMATION:\n{faq.payload.get('text_content', '')}")
        
        # Search categories (for category-related questions)
        category_results = qdrant.search(
            collection_name=COLLECTIONS["categories"],
            query_vector={"default": query_vector},
            limit=1,  # We don't need many categories
            with_payload=True
        )
        
        for category in category_results:
            contexts.append(f"CATEGORY INFORMATION:\n{category.payload.get('text_content', '')}")
        
        # Join all contexts
        all_context = "\n\n".join(contexts)
        return all_context
    
    except Exception as e:
        print(f"⚠️ Error retrieving context: {e}")
        return ""

def chat_completion_with_context(user_message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Generate a chat completion with OpenAI, using relevant context
    """
    if chat_history is None:
        chat_history = []
    
    try:
        # Retrieve relevant context
        context = retrieve_relevant_context(user_message)
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": f"""You are a helpful e-commerce assistant for a Vietnamese online shop.
             Answer the user's questions based on the following context. 
             If you don't know the answer based on the provided context, say so politely.
             Context: {context}"""}
        ]
        
        # Add chat history
        messages.extend(chat_history)
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # or any preferred model
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and return the response
        assistant_message = response.choices[0].message.content
        
        return {
            "response": assistant_message,
            "total_tokens": response.usage.total_tokens
        }
    
    except Exception as e:
        print(f"⚠️ Error generating chat completion: {e}")
        return {
            "response": "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn.",
            "total_tokens": 0
        }

def save_chat_history(session_id: str, user_id: int, messages: List[Dict[str, str]]) -> bool:
    """
    Save chat history to database
    """
    try:
        # Save chat history to database (placeholder)
        # In a real implementation, you would save this to your database
        print(f"Saving chat history for session {session_id}, user {user_id}")
        return True
    except Exception as e:
        print(f"⚠️ Error saving chat history: {e}")
        return False

def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """
    Get chat history from database
    """
    try:
        # Get chat history from database (placeholder)
        # In a real implementation, you would retrieve this from your database
        print(f"Getting chat history for session {session_id}")
        return []
    except Exception as e:
        print(f"⚠️ Error getting chat history: {e}")
        return []

def generate_product_recommendations_from_chat(chat_text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Generate product recommendations based on chat context
    """
    try:
        # Generate query embedding from chat text
        query_vector = query_embedding(chat_text)
        
        # Search for relevant products
        product_results = qdrant.search(
            collection_name=COLLECTIONS["products"],
            query_vector={"default": query_vector},
            limit=limit,
            with_payload=True
        )
        
        # Convert to simple format
        recommendations = []
        for product in product_results:
            recommendations.append({
                "product_id": product.id,
                "score": product.score,
                "name": product.payload.get("name", ""),
                "price": product.payload.get("price", 0),
                "short_description": product.payload.get("short_description", ""),
                "rating_average": product.payload.get("rating_average", 0),
            })
        
        return recommendations
    
    except Exception as e:
        print(f"⚠️ Error generating product recommendations from chat: {e}")
        return [] 