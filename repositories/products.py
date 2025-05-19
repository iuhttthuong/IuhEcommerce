from db import Session
from models.categories import Category
from models.discounts import Discount
from models.inventories import Inventory
from models.product_discounts import ProductDiscount
from models.product_images import ProductImage
from models.products import Product, ProductCreate, ProductModel  
from models.brands import Brand
from models.sellers import Seller
from models.warranties import Warranty


class ProductRepositories:
    @staticmethod
    def create(product: ProductCreate) -> Product:
        with Session() as session:
            product = Product(**product.model_dump())
            session.add(product)
            session.commit()
            session.refresh(product)
            return ProductModel.model_validate(product)
    @staticmethod
    def get(product_id: int) -> ProductModel:
        with Session() as session:
            product = session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            return ProductModel.model_validate(product)
    @staticmethod
    def update(product_id: int, data: ProductCreate) -> ProductModel:
        with Session() as session:
            product = session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(product, field, value)

            session.commit()
            session.refresh(product)
            return ProductModel.model_validate(product)
    @staticmethod
    def delete(product_id: int):
        with Session() as session:
            product = session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")

            session.delete(product)
            session.commit()      
    @staticmethod
    def get_info(id: int):
        with Session() as session:
            products = session.query(Product).filter(Product.product_id == id).all()
            if not products:
                raise ValueError(f"Product with ID {id} not found")

            brands = session.query(Brand).filter(Brand.brand_id.in_([p.brand_id for p in products])).all()
            categories = session.query(Category).filter(Category.category_id.in_([p.category_id for p in products])).all()
            sellers = session.query(Seller).filter(Seller.seller_id.in_([p.seller_id for p in products])).all()
            product_images = session.query(ProductImage).filter(ProductImage.product_id.in_([p.product_id for p in products])).all()
            warranties = session.query(Warranty).filter(Warranty.product_id.in_([p.product_id for p in products])).all()
            inventories = session.query(Inventory).filter(Inventory.product_id.in_([p.product_id for p in products])).all()
            product_discounts = session.query(ProductDiscount).filter(ProductDiscount.product_id.in_([p.product_id for p in products])).all()
            discounts = session.query(Discount).filter(Discount.discount_id.in_([pd.discount_id for pd in product_discounts])).all()

            result = []
            for product in products:
                product_info = {
                    "product": ProductModel.model_validate(product),
                    "brand": [b for b in brands if b.brand_id == product.brand_id],
                    "category": [c for c in categories if c.category_id == product.category_id],
                    "seller": [s for s in sellers if s.seller_id == product.seller_id],
                    "product_image": [pi for pi in product_images if pi.product_id == product.product_id],
                    "warranty": [w for w in warranties if w.product_id == product.product_id],
                    "inventory": [i for i in inventories if i.product_id == product.product_id],
                    "product_discount": [pd for pd in product_discounts if pd.product_id == product.product_id],
                    "discount": [
                        d for d in discounts
                        if any(d.discount_id == pd.discount_id for pd in product_discounts if pd.product_id == product.product_id)
                    ]
                }
                result.append(product_info)
            return result[0] if result else None


    @staticmethod
    def get_home_products(offset: int = 0, limit: int = 10):
        with Session() as session:
            # Lấy tổng số sản phẩm
            total = session.query(Product).count()

            # Lấy danh sách sản phẩm theo trang
            products = (
                session.query(Product)
                .order_by(Product.created_at.desc())  # Hoặc product_id.desc()
                .offset(offset)
                .limit(limit)
                .all()
            )

            if not products:
                return {"total": total, "products": []}

            product_ids = [p.product_id for p in products]
            brand_ids = [p.brand_id for p in products]
            category_ids = [p.category_id for p in products]

            brands = session.query(Brand).filter(Brand.brand_id.in_(brand_ids)).all()
            categories = session.query(Category).filter(Category.category_id.in_(category_ids)).all()
            images = session.query(ProductImage).filter(ProductImage.product_id.in_(product_ids)).all()
            inventories = session.query(Inventory).filter(Inventory.product_id.in_(product_ids)).all()
            product_discounts = session.query(ProductDiscount).filter(ProductDiscount.product_id.in_(product_ids)).all()
            discount_ids = [pd.discount_id for pd in product_discounts]
            discounts = session.query(Discount).filter(Discount.discount_id.in_(discount_ids)).all()

            result = []
            for product in products:
                info = {
                    "product": ProductModel.model_validate(product),
                    "brand": next((b for b in brands if b.brand_id == product.brand_id), None),
                    "category": next((c for c in categories if c.category_id == product.category_id), None),
                    "image": next((img for img in images if img.product_id == product.product_id), None),
                    "inventory": next((inv for inv in inventories if inv.product_id == product.product_id), None),
                    "discount": next(
                        (
                            d for pd in product_discounts if pd.product_id == product.product_id
                            for d in discounts if d.discount_id == pd.discount_id
                        ),
                        None
                    ),
                }
                result.append(info)

            return {
                "total": total,
                "products": result
            }

