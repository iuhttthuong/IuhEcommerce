from openai import OpenAI
from env import env 
client = OpenAI()

response = client.responses.create(
    model="gpt-4.0-mini",
    tools=[
        {
            "type": "web_search",
            "search_context_size": "low",
        }
    ],
    input="""Khách hàng yêu cầu so sánh giữa nước rửa tay Sunlight và nước xà bông Omo """,
)

print(response.output_text)
