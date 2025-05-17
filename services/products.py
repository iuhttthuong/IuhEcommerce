from models.products import Product, ProductCreate, ProductModel
from repositories.products import ProductRepositories

class ProductServices:
    @staticmethod
    def create(payload: ProductCreate) -> Product:
        return ProductRepositories.create(payload)
    @staticmethod
    def get(product_id: int) -> ProductModel:
        return ProductRepositories.get(product_id)
    @staticmethod
    def update(product_id: int, data: ProductCreate) -> ProductModel:
        return ProductRepositories.update(product_id, data)
    @staticmethod
    def delete(product_id: int) -> ProductModel:
        return ProductRepositories.delete(product_id)
    @staticmethod
    def get_info(id: int):
        return ProductRepositories.get_info(id)
    @staticmethod
    def get_home_products(offset = 0, limit = 10):
        return ProductRepositories.get_home_products(offset, limit)