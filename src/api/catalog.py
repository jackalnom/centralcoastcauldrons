from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = "SELECT * FROM potion_catalog_items"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        rows = [row._asdict() for row in result.fetchall()]
        results = []
        for row in rows:
            results.append(
                {
                    "sku": row["sku"],
                    "name": row["name"],
                    "quantity": row["quantity"],
                    "price": row["price"],
                    "potion_type": row["potion_type"],
                }
            )
        return results
