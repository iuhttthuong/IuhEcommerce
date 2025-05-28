from db import Session
from models.customers import Customer, CustomerCreate, UpdateCustomerPayload, CustomerModel
from models.products import Product
from models.orders import Order
from models.reviews import Review
from sqlalchemy.exc import NoResultFound
from loguru import logger
from datetime import datetime
from sqlalchemy import func
from typing import List

class CustomerRepository:
    @staticmethod
    def create(payload: CustomerCreate) -> CustomerModel:
        with Session() as session:
            customer = Customer(**payload.model_dump())
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return CustomerModel.model_validate(customer)

    @staticmethod
    def get_one(customer_id: int) -> CustomerModel:
        with Session() as session:
            customer = session.get(Customer, customer_id)
            if not customer:
                return None
            return CustomerModel.model_validate(customer)
            
    @staticmethod
    def get_by_id(customer_id: int) -> CustomerModel:
        """
        Lấy thông tin khách hàng theo ID, trả về None nếu không tìm thấy
        """
        try:
            with Session() as session:
                customer = session.get(Customer, customer_id)
                if not customer:
                    logger.warning(f"Không tìm thấy khách hàng với ID: {customer_id}")
                    return None
                return CustomerModel.model_validate(customer)
        except Exception as e:
            logger.error(f"Lỗi khi lấy khách hàng với ID {customer_id}: {str(e)}")
            return None

    @staticmethod
    def get_or_create_default_customer():
        """
        Lấy customer với ID=1 hoặc tạo mới nếu không tồn tại
        """
        try:
            # Kiểm tra nếu đã có customer với ID=1
            default_customer = CustomerRepository.get_by_id(1)
            
            # Nếu không tìm thấy, tạo mới
            if not default_customer:
                logger.info("Tạo mới khách hàng mặc định với ID=1")
                # Tạo đúng theo schema của Customer
                new_customer = CustomerCreate(
                    customer_fname="Default",
                    customer_lname="User",
                    customer_mail="default@example.com",
                    customer_address="Default Address",
                    customer_phone="0000000000",
                    customer_dob=datetime.datetime.now(), 
                    customer_gender="other"
                )
                
                with Session() as session:
                    # Tạo customer mới với ID=1
                    customer = Customer(
                        customer_id=1,
                        **new_customer.model_dump()
                    )
                    session.add(customer)
                    try:
                        session.commit()
                        session.refresh(customer)
                        logger.info(f"Đã tạo khách hàng mặc định với ID: {customer.customer_id}")
                        return CustomerModel.model_validate(customer)
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Lỗi khi commit khách hàng mặc định: {str(e)}")
                        # Thử tạo khách hàng với ID khác nếu có lỗi unique constraint
                        try:
                            # Tìm ID lớn nhất hiện tại
                            max_id = session.query(func.max(Customer.customer_id)).scalar() or 0
                            customer = Customer(
                                customer_id=max_id + 1,
                                **new_customer.model_dump()
                            )
                            session.add(customer)
                            session.commit()
                            session.refresh(customer)
                            logger.info(f"Đã tạo khách hàng mặc định với ID: {customer.customer_id}")
                            return CustomerModel.model_validate(customer)
                        except Exception as inner_e:
                            logger.error(f"Không thể tạo khách hàng dù đã thử ID khác: {str(inner_e)}")
                            return None
            
            return default_customer
        except Exception as e:
            logger.error(f"Lỗi khi tạo khách hàng mặc định: {str(e)}")
            return None

    @staticmethod
    def update(customer_id: int, data: UpdateCustomerPayload) -> CustomerModel:
        with Session() as session:
            customer = session.get(Customer, customer_id)
            if not customer:
                return None
                
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(customer, field, value)
            session.commit()
            session.refresh(customer)
            return CustomerModel.model_validate(customer)

    @staticmethod
    def delete(customer_id: int) -> bool:
        try:
            with Session() as session:
                customer = session.get(Customer, customer_id)
                if not customer:
                    return False
                session.delete(customer)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa khách hàng với ID {customer_id}: {str(e)}")
            return False

    @staticmethod
    def check_customer(customer_id: int) -> bool:
        """
        Kiểm tra khách hàng có tồn tại hay không theo customer_id.
        Trả về True nếu tồn tại, False nếu không.
        """
        try:
            with Session() as session:
                customer = session.get(Customer, customer_id)
                return customer is not None
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra khách hàng với ID {customer_id}: {str(e)}")
            return False

    @staticmethod
    def get_by_shop(seller_id: int) -> List[CustomerModel]:
        """
        Lấy danh sách khách hàng đã mua hàng hoặc tương tác với shop (seller)
        thông qua reviews (JOIN qua products)
        """
        try:
            with Session() as session:
                customers_from_reviews = session.query(Customer).join(
                    Review, Customer.customer_id == Review.customer_id
                ).join(
                    Product, Review.product_id == Product.product_id
                ).filter(
                    Product.seller_id == seller_id
                ).distinct().all()
                if not customers_from_reviews:
                    return []
                return [CustomerModel.model_validate(customer) for customer in customers_from_reviews]
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách khách hàng của seller {seller_id}: {str(e)}")
            return []
