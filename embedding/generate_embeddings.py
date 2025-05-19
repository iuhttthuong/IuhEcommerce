import numpy as np
from env import env
import os
import time
from google.genai import types
from google import genai
from loguru import logger

# List of API keys
API_KEYS = [
    env.GEMINI_API_KEY_1,
    env.GEMINI_API_KEY_2,
    env.GEMINI_API_KEY_3,
    env.GEMINI_API_KEY_4,
    env.GEMINI_API_KEY_5
]

# Track API key usage
api_key_usage = {key: {"count": 0, "last_used": 0} for key in API_KEYS}
RATE_LIMIT = 60  # requests per minute
COOLDOWN = 60  # seconds to wait after hitting rate limit

def get_available_api_key():
    """Get an available API key that hasn't hit rate limit"""
    current_time = time.time()
    
    # Check each API key
    for key in API_KEYS:
        usage = api_key_usage[key]
        
        # If key hasn't been used in the last minute, reset count
        if current_time - usage["last_used"] > 60:
            usage["count"] = 0
            
        # If key hasn't hit rate limit, use it
        if usage["count"] < RATE_LIMIT:
            return key
            
    # If all keys are rate limited, wait for cooldown
    logger.warning("All API keys are rate limited. Waiting for cooldown...")
    time.sleep(COOLDOWN)
    return API_KEYS[0]  # Return first key after cooldown

def generate_embedding(text: str, retry_limit=3):
    if not text.strip():
        return np.zeros(3072).tolist()  # Return empty vector if text is empty
    
    retry_count = 0
    while retry_count < retry_limit:
        try:
            # Get available API key
            api_key = get_available_api_key()
            client = genai.Client(api_key=api_key)
            
            # Update usage tracking
            api_key_usage[api_key]["count"] += 1
            api_key_usage[api_key]["last_used"] = time.time()
            
            # Call the API to generate embeddings
            result = client.models.embed_content(
                model="gemini-embedding-exp-03-07",
                contents=text,
                config={"task_type": "RETRIEVAL_DOCUMENT"}
            )
            
            # Check if embeddings are returned
            if result and result.embeddings:
                return result.embeddings[0].values
            else:
                logger.warning(f"No embeddings returned for text: {text[:100]}...")
                return np.zeros(3072).tolist()
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            retry_count += 1
            if retry_count < retry_limit:
                logger.info(f"Retrying... Attempt {retry_count}/{retry_limit}")
                time.sleep(2 ** retry_count)  # Exponential backoff
            continue
    
    logger.error("All retry attempts failed.")
    return np.zeros(3072).tolist()

def query_embedding(text: str, retry_limit=3):
    if not text.strip():
        return np.zeros(3072).tolist()  # Return empty vector if text is empty
    
    retry_count = 0
    while retry_count < retry_limit:
        try:
            # Get available API key
            api_key = get_available_api_key()
            client = genai.Client(api_key=api_key)
            
            # Update usage tracking
            api_key_usage[api_key]["count"] += 1
            api_key_usage[api_key]["last_used"] = time.time()
            
            # Call the API to generate embeddings
            result = client.models.embed_content(
                model="gemini-embedding-exp-03-07",
                contents=text,
                config={"task_type": "RETRIEVAL_QUERY"}
            )
            
            # Check if embeddings are returned
            if result and result.embeddings:
                return result.embeddings[0].values
            else:
                logger.warning(f"No embeddings returned for query: {text[:100]}...")
                return np.zeros(3072).tolist()
                
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            retry_count += 1
            if retry_count < retry_limit:
                logger.info(f"Retrying... Attempt {retry_count}/{retry_limit}")
                time.sleep(2 ** retry_count)  # Exponential backoff
            continue
    
    logger.error("All retry attempts failed.")
    return np.zeros(3072).tolist()