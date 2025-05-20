from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.finance import FinanceRepository
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .base import BaseShopAgent, ShopAgentRequest, ShopAgentResponse
from models.finance import TransactionType

router = APIRouter(prefix="/shop/finance", tags=["Shop Finance"])

class FinanceAgent(BaseShopAgent):
    def __init__(self, shop_id: int):
        super().__init__(shop_id, "finance")
        self.finance_repository = FinanceRepository()

    async def process(self, request: ShopAgentRequest) -> ShopAgentResponse:
        message = request.message.lower()
        
        if "số dư" in message or "tài khoản" in message:
            return await self._handle_check_balance(request)
        elif "giao dịch" in message or "lịch sử" in message:
            return await self._handle_transaction_history(request)
        elif "báo cáo" in message or "thống kê" in message:
            return await self._handle_financial_report(request)
        elif "rút tiền" in message:
            return await self._handle_withdrawal(request)
        else:
            return self._create_response(
                "Tôi có thể giúp bạn quản lý tài chính. "
                "Bạn có thể:\n"
                "- Kiểm tra số dư tài khoản\n"
                "- Xem lịch sử giao dịch\n"
                "- Xem báo cáo tài chính\n"
                "- Thực hiện rút tiền\n"
                "Bạn muốn thực hiện thao tác nào?"
            )

    async def _handle_check_balance(self, request: ShopAgentRequest) -> ShopAgentResponse:
        balance = self.finance_repository.get_shop_balance(self.db, self.shop_id)
        return self._create_response(
            f"Số dư tài khoản hiện tại của bạn là: {balance:,.0f} VNĐ"
        )

    async def _handle_transaction_history(self, request: ShopAgentRequest) -> ShopAgentResponse:
        # Default to last 30 days if no date range specified
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        transactions = self.finance_repository.get_shop_transactions(
            self.db,
            self.shop_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not transactions:
            return self._create_response(
                "Không có giao dịch nào trong khoảng thời gian này."
            )
        
        response = "Lịch sử giao dịch gần đây:\n"
        for trans in transactions[:10]:  # Show last 10 transactions
            response += f"- {trans.transaction_date.strftime('%d/%m/%Y')}: "
            response += f"{trans.type.value} - {trans.amount:,.0f} VNĐ"
            if trans.description:
                response += f" ({trans.description})"
            response += "\n"
            
        return self._create_response(response)

    async def _handle_financial_report(self, request: ShopAgentRequest) -> ShopAgentResponse:
        # Default to last 30 days if no date range specified
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.finance_repository.get_shop_summary(
            self.db,
            self.shop_id,
            start_date=start_date,
            end_date=end_date
        )
        
        response = "Báo cáo tài chính:\n"
        response += f"Tổng thu: {summary['income']:,.0f} VNĐ\n"
        response += f"Tổng chi: {summary['expense']:,.0f} VNĐ\n"
        response += f"Hoàn tiền: {summary['refund']:,.0f} VNĐ\n"
        response += f"Rút tiền: {summary['withdrawal']:,.0f} VNĐ\n"
        response += f"Nạp tiền: {summary['deposit']:,.0f} VNĐ\n"
        response += f"Số dư: {(summary['income'] - summary['expense']):,.0f} VNĐ"
        
        return self._create_response(response)

    async def _handle_withdrawal(self, request: ShopAgentRequest) -> ShopAgentResponse:
        balance = self.finance_repository.get_shop_balance(self.db, self.shop_id)
        return self._create_response(
            f"Để rút tiền, vui lòng cung cấp:\n"
            f"1. Số tiền muốn rút (số dư hiện tại: {balance:,.0f} VNĐ)\n"
            f"2. Thông tin tài khoản ngân hàng nhận tiền"
        )

# Add router endpoints
@router.get("/")
async def get_financial_data():
    """Get shop financial data"""
    return {"message": "Get financial data endpoint"} 