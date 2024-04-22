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
        rows = [row.asdict() for row in result.fetchall()]
        catalog = []
        for row in rows:
            potion_quantity_sql = "SELECT SUM(quantity) FROM potions WHERE potion_type = :potion_type"
            result = connection.execute(sqlalchemy.text(potion_quantity_sql), [{"potion_type": row["potion_type"]}])
            quantity = result.fetchone()[0]
            if quantity > 0:
                catalog.append(
                    {
                        "sku": row["sku"],
                        "name": row["name"],
                        "quantity": quantity,
                        "price": row["price"],
                        "potion_type": row["potion_type"],
                    }
                )
        print(f"catalog: {catalog}")
        return catalog
