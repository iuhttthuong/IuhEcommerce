from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.products import Product, ProductCreate, ProductResponse, ProductModel
from repositories.products import ProductRepositories
from services.search import SearchServices

class ProductServices:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepositories(db)

    def get(self, product_id: int) -> Product:
        """Get a product by ID"""
        return self.repository.get(product_id)

    def create(self, product: ProductCreate) -> Product:
        """Create a new product"""
        product = self.repository.create(product)
        # Index the product for search
        SearchServices.index_product(
            product_id=product.product_id,
            product_name=product.name,
            description=product.description,
            category=product.category_id
        )
        return product

    def update(self, product_id: int, product: ProductCreate) -> Optional[Product]:
        """Update a product"""
        product = self.repository.update(product_id, product)
        if product:
            # Re-index the product for search
            SearchServices.index_product(
                product_id=product.product_id,
                product_name=product.name,
                description=product.description,
                category=product.category_id
            )
        return product

    def delete(self, product_id: int) -> bool:
        """Delete a product"""
        success = self.repository.delete(product_id)
        if success:
            # Remove from search index
            SearchServices.remove_product(product_id)
        return success

    def get_by_shop(
        self,
        shop_id: int,
        skip: int = 0,
        limit: int = 1000,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get products by shop with optional filtering"""
        return self.repository.get_by_shop(
            shop_id,
            skip,
            limit,
            category,
            search
        )

    def get_active_products(
        self,
        shop_id: int,
        skip: int = 0,
        limit: int = 1000
    ) -> List[Product]:
        """Get active products for a shop"""
        return self.repository.get_active_products(
            shop_id,
            skip,
            limit
        )

    def get_product_stats(self, shop_id: int) -> Dict[str, Any]:
        """Get product statistics for a shop"""
        return self.repository.get_product_stats(shop_id)

    def search(self, query: str, shop_id: Optional[int] = None) -> List[Product]:
        """Search products by name or description"""
        return self.repository.search(query, shop_id)

    def get_by_category(self, category_id: str, shop_id: Optional[int] = None) -> List[Product]:
        """Get products by category"""
        return self.repository.get_by_category(category_id, shop_id)

    def get_info(self, product_id: int):
        """Get detailed product information"""
        return self.repository.get_info(product_id)

    def get_home_products(self, offset: int = 0, limit: int = 10):
        """Get products for home page"""
        return self.repository.get_home_products(offset, limit)