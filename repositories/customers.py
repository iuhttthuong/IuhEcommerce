from db import Session
from models.customers import Customer, CustomerCreate, UpdateCustomerPayload, CustomerModel

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
            return CustomerModel.model_validate(customer)

    @staticmethod
    def update(customer_id: int, data: UpdateCustomerPayload) -> CustomerModel:
        with Session() as session:
            customer = session.get(Customer, customer_id)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(customer, field, value)
            session.commit()
            session.refresh(customer)
            return CustomerModel.model_validate(customer)

    @staticmethod
    def delete(customer_id: int):
        with Session() as session:
            customer = session.get(Customer, customer_id)
            session.delete(customer)
            session.commit()