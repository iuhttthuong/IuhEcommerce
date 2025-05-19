import time
import psycopg2
from fastapi import APIRouter
import numpy as np
from env import env
from db import Session
from openai import OpenAI

api_key = env.OPENAI_API_KEY
client = OpenAI(api_key=api_key)

response = client.embeddings.create(
input="adasadas",
model="text-embedding-3-small"
)
print(response.data[0].embedding)