import requests
import json
import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Load environment variables
load_dotenv()

# Console for pretty printing
console = Console()

# API URL
API_URL = "http://localhost:8000"  # Update with your FastAPI server URL

# Test chat ID - replace with a valid ID from your database if needed
TEST_CHAT_ID = 1

async def test_orchestrator(message):
    """Test the orchestrator agent with a message"""
    url = f"{API_URL}/orchestrator/orchestrator/process"
    payload = {
        "chat_id": TEST_CHAT_ID,
        "message": message
    }
    
    console.print(f"\n[bold blue]User:[/bold blue] {message}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Display result in a panel
        console.print(Panel(
            f"[bold green]Agent Response:[/bold green] {result['content']}\n\n"
            f"[bold yellow]Source Agent:[/bold yellow] {result['source_agent']}\n"
            f"[bold yellow]Intent:[/bold yellow] {result['intent']}\n"
            f"[bold yellow]Confidence:[/bold yellow] {result['confidence']:.2f}",
            title="Orchestrator Response",
            border_style="green"
        ))
        return result
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None

async def test_qdrant_agent(message):
    """Test the Qdrant agent directly"""
    url = f"{API_URL}/qdrant_agent/chatbot/chatbot"
    payload = {
        "chat_id": TEST_CHAT_ID,
        "message": message
    }
    
    console.print(f"\n[bold blue]User (Qdrant):[/bold blue] {message}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        console.print(Panel(
            f"[bold green]Qdrant Response:[/bold green] {result['content']}",
            title="Qdrant Agent Response",
            border_style="cyan"
        ))
        return result
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None

async def test_recommendation_agent(message, user_id=None):
    """Test the recommendation agent directly"""
    url = f"{API_URL}/recommendation/recommendation/recommend"
    payload = {
        "chat_id": TEST_CHAT_ID,
        "user_id": user_id,
        "message": message,
        "context": {
            "recent_views": [1, 2, 3],
            "recent_searches": ["laptop", "smartphone"]
        }
    }
    
    console.print(f"\n[bold blue]User (Recommendation):[/bold blue] {message}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Display recommendations in a table
        table = Table(title="Recommended Products")
        table.add_column("Name", style="cyan")
        table.add_column("Price", style="green")
        
        for product in result.get('recommendations', [])[:5]:
            table.add_row(
                product.get('name', 'Unknown'), 
                f"{product.get('price', 0):,} VND"
            )
        
        console.print(Panel(
            f"[bold green]Recommendation Response:[/bold green] {result['content']}",
            title=f"Recommendation Agent ({result.get('recommendation_type', 'unknown')})",
            border_style="magenta"
        ))
        
        if result.get('recommendations'):
            console.print(table)
            
        return result
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None

async def test_product_info_agent(message, product_id=None):
    """Test the product info agent directly"""
    url = f"{API_URL}/product_info/product-info/info"
    payload = {
        "chat_id": TEST_CHAT_ID,
        "message": message,
        "product_id": product_id
    }
    
    console.print(f"\n[bold blue]User (Product Info):[/bold blue] {message}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        console.print(Panel(
            f"[bold green]Product Info Response:[/bold green] {result['content']}",
            title=f"Product Info Agent ({result.get('query_type', 'unknown')})",
            border_style="yellow"
        ))
        return result
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None

async def test_get_product_by_id(product_id):
    """Test getting product info by ID directly"""
    url = f"{API_URL}/productsget_info/{product_id}"
    
    console.print(f"\n[bold blue]Getting product info for ID:[/bold blue] {product_id}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        
        # Create a table to display product info
        table = Table(title=f"Product Info (ID: {product_id})")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in result.items():
            table.add_row(str(key), str(value))
        
        console.print(table)
        return result
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None

async def run_chat_tests():
    """Run a series of tests for the chat functionality"""
    console.print(Panel("Starting Chat Tests", style="bold blue"))
    
    # Test orchestrator with different types of queries
    test_queries = [
        "Tôi đang tìm kiếm một cuốn sách có tên nhà giả kim",
        # "iPhone 13 có những màu nào?",
        # "Gợi ý cho tôi một vài sản phẩm tương tự như Samsung Galaxy S23",
        "So sánh giúp tôi iPhone và Samsung",
        "điều kiện hoàn tiền là gì?"
        "Tình trạng đơn hàng của tôi"
    ]
    
    for query in test_queries:
        await test_orchestrator(query)
        await asyncio.sleep(1)  # Prevent rate limiting
    
    # Test Qdrant agent directly
    qdrant_queries = [
        "Có chính sách bảo hành cho sản phẩm điện tử không?",
        "Tìm cho tôi một chiếc điện thoại tốt dưới 10 triệu"
    ]
    
    for query in qdrant_queries:
        await test_qdrant_agent(query)
        await asyncio.sleep(1)  # Prevent rate limiting
    
    # Test recommendation agent directly
    recommendation_queries = [
        "Gợi ý cho tôi cuốn sách giống nhà giả kim nhất",
        "Tôi thích các sản phẩm nước lau sàn, có đề xuất gì cho tôi không?"
    ]
    
    for query in recommendation_queries:
        await test_recommendation_agent(query, user_id=1)
        await asyncio.sleep(1)  # Prevent rate limiting
    
    # Test product info agent directly
    product_info_queries = [
        "Cho tôi thông tin về sáp thơm glade",
        "10 cuộn giấy pulppy có giá bao nhiêu?"
    ]
    
    for query in product_info_queries:
        await test_product_info_agent(query)
        await asyncio.sleep(1)  # Prevent rate limiting


def interactive_chat():
    """Start an interactive chat session with the orchestrator"""
    console.print(Panel(
        "Bắt đầu phiên trò chuyện tương tác với AI. Gõ 'exit' để thoát.",
        title="Interactive Chat",
        border_style="green"
    ))
    
    while True:
        user_input = console.input("[bold blue]Bạn: [/bold blue]")
        
        if user_input.lower() in ['exit', 'quit', 'thoát']:
            console.print("[yellow]Kết thúc phiên chat.[/yellow]")
            break
            
        asyncio.run(test_orchestrator(user_input))

if __name__ == "__main__":
    console.print(Panel(
        "Chọn chế độ test:\n"
        "1. Chạy tất cả các test\n"
        "2. Chat tương tác với AI\n"
        "3. Lấy thông tin sản phẩm theo ID\n",
        title="Chat Test Menu",
        border_style="blue"
    ))
    
    choice = console.input("[bold]Lựa chọn của bạn: [/bold]")
    
    if choice == "1":
        asyncio.run(run_chat_tests())
    elif choice == "2":
        interactive_chat()
    elif choice == "3":
        product_id = console.input("[bold]Nhập ID sản phẩm: [/bold]")
        asyncio.run(test_get_product_by_id(product_id))
    else:
        console.print("[bold red]Lựa chọn không hợp lệ![/bold red]") 