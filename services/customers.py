from models.customers import Customer, CustomerCreate, UpdateCustomerPayload, CustomerModel
from repositories.customers import CustomerRepository

class CustomerService:
    @staticmethod
    def create_customer(payload: CustomerCreate) -> CustomerModel:
        return CustomerRepository.create(payload)

    @staticmethod
    def get_customer(customer_id: int) -> CustomerModel:
        return CustomerRepository.get_one(customer_id)

    @staticmethod
    def update_customer(customer_id: int, data: UpdateCustomerPayload) -> CustomerModel:
        return CustomerRepository.update(customer_id, data)

    @staticmethod
    def delete_customer(customer_id: int):
        return CustomerRepository.delete(customer_id)

    @staticmethod
    def check_customer(customer_id: int):
        return CustomerRepository.check_customer(customer_id)