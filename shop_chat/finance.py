from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopChatRequest, ShopChatResponse, BaseShopAgent
from repositories.finance import FinanceRepository
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from models.finance import TransactionType
from sqlalchemy.orm import Session

router = APIRouter(prefix="/shop/finance", tags=["Shop Finance"])

class FinanceAgent(BaseShopAgent):
    def __init__(self, shop_id: int, db: Session):
        super().__init__(shop_id)
        self.finance_repository = FinanceRepository(db)

    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
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

    async def _handle_check_balance(self, request: ShopChatRequest) -> ShopChatResponse:
        balance = self.finance_repository.get_shop_balance(self.shop_id)
        return self._create_response(
            f"Số dư tài khoản hiện tại của bạn là: {balance:,.0f} VNĐ"
        )

    async def _handle_transaction_history(self, request: ShopChatRequest) -> ShopChatResponse:
        # Default to last 30 days if no date range specified
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        transactions = self.finance_repository.get_shop_transactions(
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

    async def _handle_financial_report(self, request: ShopChatRequest) -> ShopChatResponse:
        # Default to last 30 days if no date range specified
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.finance_repository.get_shop_summary(
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

    async def _handle_withdrawal(self, request: ShopChatRequest) -> ShopChatResponse:
        balance = self.finance_repository.get_shop_balance(self.shop_id)
        return self._create_response(
            f"Để rút tiền, vui lòng cung cấp:\n"
            f"1. Số tiền muốn rút (số dư hiện tại: {balance:,.0f} VNĐ)\n"
            f"2. Thông tin tài khoản ngân hàng nhận tiền"
        )

class Finance:
    def __init__(self, db: Session):
        self.db = db
        self.agent = FinanceAgent(shop_id=1, db=db)  # Pass db to FinanceAgent
        self.finance_repository = FinanceRepository(db)

    async def get_total_revenue(self) -> float:
        """Get total revenue"""
        try:
            summary = await self.finance_repository.get_shop_summary(self.agent.shop_id)
            return summary['income']
        except Exception as e:
            logger.error(f"Error getting total revenue: {str(e)}")
            return 0.0

    async def get_balance(self) -> float:
        """Get current balance"""
        try:
            return await self.finance_repository.get_shop_balance(self.agent.shop_id)
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return 0.0

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a finance management request"""
        try:
            response = await self.agent.process_request(ShopChatRequest(**request))
            return response.dict()
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

# Add router endpoints
@router.get("/")
async def get_financial_data():
    """Get shop financial data"""
    return {"message": "Get financial data endpoint"} 