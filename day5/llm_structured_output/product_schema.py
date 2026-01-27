from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

class ProductDetails(BaseModel):
    product_name: str = Field(description="The name of the product.")
    brand: Optional[str] = Field(None, description="The brand of the product, if specified.")
    price: float = Field(description="The price of the product as a floating-point number.")
    currency: str = Field(description="The currency of the product price, e.g., USD, EUR.")
    features: List[str] = Field(description="A list of key features of the product.")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="The average rating of the product, between 1.0 and 5.0.")

# Example usage (not executed by main.py directly, but useful for schema understanding)
if __name__ == "__main__":
    schema_json = ProductDetails.model_json_schema()
    import json
    print(json.dumps(schema_json, indent=2))
