from fastapi import APIRouter, HTTPException
from models.customers import CustomerCreate, UpdateCustomerPayload, CustomerModel
from services.customers import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/add", response_model=CustomerModel)
def create_customer(payload: CustomerCreate):
    return CustomerService.create_customer(payload)

@router.get("/get/{customer_id}", response_model=CustomerModel)
def get_customer(customer_id: int):
    customer = CustomerService.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
@router.put("/update/{customer_id}", response_model=CustomerModel)
def update_customer(customer_id: int, payload: UpdateCustomerPayload):
    customer = CustomerService.update_customer(customer_id, payload)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
@router.delete("/delete/{customer_id}")
def delete_customer(customer_id: int):
    CustomerService.delete_customer(customer_id)
    return {"message": "Customer deleted successfully"}