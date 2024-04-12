from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = "SELECT * FROM potion_catalog_items WHERE quantity > 0"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        rows = result.fetchall()
        catalog = []
        for row in rows:
            row = row._asdict()
            catalog.append(
                {
                    "sku": row["sku"],
                    "name": row["name"],
                    "quantity": row["quantity"],
                    "price": row["price"],
                    "potion_type": row["potion_type"],
                }
            )
        print(f"catalog: {catalog}")
        return catalog
