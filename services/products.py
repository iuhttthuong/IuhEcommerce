from models.products import Product, ProductCreate, ProductResponse
from repositories.products import ProductRepositories
from services.search import SearchServices

class ProductServices:
    @staticmethod
    def create(payload: ProductCreate) -> Product:
        product = ProductRepositories.create(payload)
        # Index the product for search
        SearchServices.index_product(
            product_id=product.product_id,
            product_name=product.name,
            description=product.description,
            category=product.category_id
        )
        return product
    @staticmethod
    def get(product_id: int) -> ProductResponse:
        return ProductRepositories.get(product_id)
    @staticmethod
    def update(product_id: int, data: ProductCreate) -> ProductResponse:
        product = ProductRepositories.update(product_id, data)
        # Re-index the product for search
        SearchServices.index_product(
            product_id=product.product_id,
            product_name=product.name,
            description=product.description,
            category=product.category_id
        )
        return product
    @staticmethod
    def delete(product_id: int) -> ProductResponse:
        product = ProductRepositories.delete(product_id)
        # Remove from search index
        SearchServices.remove_product(product_id)
        return product
    @staticmethod
    def get_info(id: int):
        return ProductRepositories.get_info(id)
    @staticmethod
    def get_home_products(offset = 0, limit = 10):
        return ProductRepositories.get_home_products(offset, limit)