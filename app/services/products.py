from app.dependencies import BaseService
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate
from app.utils.constants import ERROR_MESSAGE, INVALID_ID, PRODUCT_NOT_FOUND
from app.utils.logger import logger


class ProductService(BaseService):
    """Service for managing products (Synchronous)"""

    def get_all_products(self):
        """Retrieve all products synchronously using ORM query."""
        try:
            products = self.db.query(Product)
            return True, "Products retrieved successfully.", products
        except Exception as e:
            logger.error("Error retrieving products: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def get_product(self, product_id: int) -> Product:
        """Retrieve a specific product using SQLAlchemy ORM."""
        try:
            if product_id <= 0:
                return False, INVALID_ID, 400
            product = (
                self.db.query(Product).filter(Product.id == product_id).first()
            )
            if not product:
                return False, PRODUCT_NOT_FOUND, 404
            return True, "Product retrieved successfully.", product
        except Exception as e:
            logger.error("Error retrieving product: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def create_product(self, product_data: ProductCreate):
        """Create a new product using SQLAlchemy ORM."""
        try:
            new_product = Product(**product_data.model_dump())
            self.db.add(new_product)
            self.db.flush()
            return True, "Product created successfully.", 201
        except Exception as e:
            logger.error("Error creating product: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def update_product(self, product_id: int, data: ProductUpdate):
        """Update product details efficiently using SQLAlchemy's .update()."""
        try:
            if product_id <= 0:
                return False, INVALID_ID, 400

            update_data = data.model_dump(exclude_unset=True)
            if "price" in update_data and update_data["price"] < 0:
                return False, "Price cannot be negative.", 400

            result = (
                self.db.query(Product)
                .filter(Product.id == product_id)
                .update(update_data, synchronize_session=False)
            )

            if result == 0:
                return False, PRODUCT_NOT_FOUND, 404

            self.db.commit()  # Commit transaction
            return True, "Product updated successfully.", 200

        except Exception as e:
            self.db.rollback()  # Rollback transaction on error
            logger.error("Error updating product: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500

    def delete_product(self, product_id: int):
        """Delete a product using SQLAlchemy ORM."""
        try:
            if product_id <= 0:
                return False, INVALID_ID, 400

            product = (
                self.db.query(Product).filter(Product.id == product_id).first()
            )
            if product is None:
                return False, PRODUCT_NOT_FOUND, 404

            self.db.delete(product)
            self.db.flush()
            return True, "Product deleted successfully", 200
        except Exception as e:
            logger.error("Error deleting product: %s", e, exc_info=True)
            return False, ERROR_MESSAGE, 500
