from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import logging
from models.categories import Category
from models.products import Product, ProductCreate, ProductResponse, ProductModel
from models.brands import Brand
from models.sellers import Seller

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductRepositories:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> Product:
        """Get a product by ID"""
        logger.info(f"Searching for product with ID: {product_id}")
        try:
            product = self.db.query(Product).filter(Product.product_id == product_id).first()
            
            if product:
                logger.info(f"Found product: {product.product_id} - {product.name}")
                return product
                
            # If not found, log all products for debugging
            all_products = self.db.query(Product).all()
            logger.warning(f"Product not found. Total products in DB: {len(all_products)}")
            for p in all_products:
                logger.warning(f"Product in DB - ID: {p.product_id}, Name: {p.name}")
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise e

    def create(self, product: ProductCreate) -> Product:
        """Create a new product"""
        db_product = Product(**product.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, product_id: int, product: ProductCreate) -> Optional[Product]:
        """Update a product"""
        db_product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if db_product:
            for key, value in product.model_dump(exclude_unset=True).items():
                setattr(db_product, key, value)
            self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def delete(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            db_product = self.db.query(Product).filter(Product.product_id == product_id).first()
            if db_product:
                self.db.delete(db_product)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting product: {str(e)}")
            raise e

    def get_by_shop(self, shop_id: int, skip: int = 0, limit: int = 100, category: Optional[str] = None, search: Optional[str] = None) -> List[Product]:
        """Get products by shop with optional filtering"""
        query = self.db.query(Product).filter(Product.seller_id == shop_id)
        
        if category:
            query = query.filter(Product.category_id == category)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
            
        return query.offset(skip).limit(limit).all()

    def get_active_products(
        self,
        shop_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get active products for a shop"""
        return self.db.query(Product).filter(
            Product.seller_id == shop_id,
            Product.availability == True
        ).offset(skip).limit(limit).all()

    def get_product_stats(
        self,
        shop_id: int
    ) -> Dict[str, Any]:
        """Get product statistics for a shop"""
        total_products = self.db.query(func.count(Product.product_id)).filter(
            Product.seller_id == shop_id
        ).scalar()
        
        active_products = self.db.query(func.count(Product.product_id)).filter(
            Product.seller_id == shop_id,
            Product.availability == True
        ).scalar()
        
        return {
            "total_products": total_products,
            "active_products": active_products
        }

    def search(self, query: str, shop_id: Optional[int] = None) -> List[Product]:
        """Search products by name or description"""
        search_query = self.db.query(Product)
        if shop_id:
            search_query = search_query.filter(Product.seller_id == shop_id)
        return search_query.filter(
            (Product.name.ilike(f"%{query}%")) | 
            (Product.description.ilike(f"%{query}%"))
        ).all()

    def get_by_category(self, category_id: str, shop_id: Optional[int] = None) -> List[Product]:
        """Get products by category"""
        query = self.db.query(Product).filter(Product.category_id == category_id)
        if shop_id:
            query = query.filter(Product.seller_id == shop_id)
        return query.all()

    def get_info(self, product_id: int):
        """Get detailed product information"""
        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        brand = self.db.query(Brand).filter(Brand.brand_id == product.brand_id).first()
        category = self.db.query(Category).filter(Category.category_id == product.category_id).first()
        seller = self.db.query(Seller).filter(Seller.seller_id == product.seller_id).first()

        return {
            "product": ProductResponse.model_validate(product),
            "brand": brand,
            "category": category,
            "seller": seller
        }

    def get_home_products(self, offset: int = 0, limit: int = 10):
        """Get products for home page"""
        # Lấy tổng số sản phẩm
        total = self.db.query(Product).count()

        # Lấy danh sách sản phẩm theo trang
        products = (
            self.db.query(Product)
            .order_by(Product.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not products:
            return {"total": total, "products": []}

        product_ids = [p.product_id for p in products]
        brand_ids = [p.brand_id for p in products]
        category_ids = [p.category_id for p in products]

        brands = self.db.query(Brand).filter(Brand.brand_id.in_(brand_ids)).all()
        categories = self.db.query(Category).filter(Category.category_id.in_(category_ids)).all()

        result = []
        for product in products:
            info = {
                "product": ProductResponse.model_validate(product),
                "brand": next((b for b in brands if b.brand_id == product.brand_id), None),
                "category": next((c for c in categories if c.category_id == product.category_id), None)
            }
            result.append(info)

        return {
            "total": total,
            "products": result
        }


            