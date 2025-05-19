from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from loguru import logger
from .base import ShopRequest, get_shop_info
from .product_management import ProductManagementAgent
from .inventory import InventoryAgent
from .order import OrderAgent
from .marketing import MarketingAgent
from .analytics import AnalyticsAgent
from .finance import FinanceAgent
from .policy import PolicyAgent
from .customer_service import CustomerServiceAgent

router = APIRouter(prefix="/shop", tags=["Shop"])

async def call_shop_agent(agent, request):
    try:
        if agent == "ProductManagementAgent":
            agent = ProductManagementAgent()
            result = await agent.process_request(request)
        elif agent == "InventoryAgent":
            agent = InventoryAgent()
            result = await agent.process_request(request)
        elif agent == "OrderAgent":
            agent = OrderAgent()
            result = await agent.process_request(request)
        elif agent == "MarketingAgent":
            agent = MarketingAgent()
            result = await agent.process_request(request)
        elif agent == "AnalyticsAgent":
            agent = AnalyticsAgent()
            result = await agent.process_request(request)
        elif agent == "FinanceAgent":
            agent = FinanceAgent()
            result = await agent.process_request(request)
        elif agent == "PolicyAgent":
            agent = PolicyAgent()
            result = await agent.process_request(request)
        elif agent == "CustomerServiceAgent":
            agent = CustomerServiceAgent()
            result = await agent.process_request(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent}")
        
        return result
    except Exception as e:
        logger.error(f"Error in call_shop_agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_shop(request: ShopRequest):
    try:
        message = request.message
        logger.info(f"Shop message: {message}")

        # Get shop info and determine which agent to use
        shop_info = await get_shop_info(message)
        logger.info(f"Shop info response: {shop_info}")

        # Call the appropriate agent
        result = await call_shop_agent(shop_info["agent"], request)
        
        return result

    except Exception as e:
        error_detail = f"Error processing shop request: {str(e)}"
        logger.error(error_detail)
        raise HTTPException(status_code=500, detail=error_detail) 