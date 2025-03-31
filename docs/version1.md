# Version 1 - Add Persistence for Red, Green, and Blue Potions

The first version of your improved store will involve keeping track of raw potion ml and number of red, green, and blue potions available for sale. Follow these steps:

1. **Add more columns to our global_inventory table**
  - Run:
  ```sh
  alembic revision -m "Add red, green, blue potions for version 1"
  ```
  - This creates a new version py file in your alembic/versions folder. Go to that file and replace the upgrade and downgrade functions with the following:
```python
def upgrade():
    op.add_column("global_inventory", sa.Column("red_ml", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("global_inventory", sa.Column("green_ml", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("global_inventory", sa.Column("blue_ml", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("global_inventory", sa.Column("red_potions", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("global_inventory", sa.Column("green_potions", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("global_inventory", sa.Column("blue_potions", sa.Integer(), nullable=False, server_default="0"))

    op.create_check_constraint("ck_red_ml_non_negative", "global_inventory", "red_ml >= 0")
    op.create_check_constraint("ck_green_ml_non_negative", "global_inventory", "green_ml >= 0")
    op.create_check_constraint("ck_blue_ml_non_negative", "global_inventory", "blue_ml >= 0")
    op.create_check_constraint("ck_red_potions_non_negative", "global_inventory", "red_potions >= 0")
    op.create_check_constraint("ck_green_potions_non_negative", "global_inventory", "green_potions >= 0")
    op.create_check_constraint("ck_blue_potions_non_negative", "global_inventory", "blue_potions >= 0")


def downgrade():
    op.drop_constraint("ck_red_ml_non_negative", "global_inventory", type_="check")
    op.drop_constraint("ck_green_ml_non_negative", "global_inventory", type_="check")
    op.drop_constraint("ck_blue_ml_non_negative", "global_inventory", type_="check")
    op.drop_constraint("ck_red_potions_non_negative", "global_inventory", type_="check")
    op.drop_constraint("ck_green_potions_non_negative", "global_inventory", type_="check")
    op.drop_constraint("ck_blue_potions_non_negative", "global_inventory", type_="check")

    op.drop_column("global_inventory", "red_ml")
    op.drop_column("global_inventory", "green_ml")
    op.drop_column("global_inventory", "blue_ml")
    op.drop_column("global_inventory", "red_potions")
    op.drop_column("global_inventory", "green_potions")
    op.drop_column("global_inventory", "blue_potions")
```
  - What this does is it will modify your global_inventory table to add new columns for storing each potion color's ml and potion quantity. It also puts a constraint to enforce that those values can't be negative. To now run this script to modify your local database run:
  ```sh
  alembic upgrade head
  ```
  - For more information on Alembic see their [tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html#the-migration-environment).

2. **Modify Your API to Use the Database**
   - Use the `global_inventory` table to track potion quantities and liquid volume.
   - Update your [API endpoints](https://blog.postman.com/what-is-an-api-endpoint/) to return JSON responses based on your inventory.
   - Assume you are only brewing and selling pure colored (red, green, and blue) potions for now.

3. **Modify Endpoint Definitions**
   - Execute SQL queries in each endpoint (e.g., `barrels.py`, `bottler.py`, `carts.py`, `catalog.py`) as follows:
     ```python
     with db.engine.begin() as connection:
         result = connection.execute(sqlalchemy.text(sql_to_execute))
     ```
   - You can see the examples where I already modify and report on gold correctly using database values in the endpoints. You need to do the same thing now for potion ml and bottles now.
   - Use `SELECT` and `UPDATE` SQL statements (no `INSERT` or `DELETE` needed for now).
   - Refer to the [getting started guide](https://observablehq.com/@calpoly-pierce/getting-started-with-sql-in-python) for SQLAlchemy execution examples.

7. **Implement Basic Business Logic**
   - In barrel plan, randomly pick a color between red, green, and blue. Check if that color has fewer than 5 potions in inventory and if you can afford a small barrel of that color. If both are true, then purchase a small barrel of that color. Do NOT modify your database in plan!
   - In barrel deliver, record delivery of your barrels. This means, update your gold to subtract the cost of barrels bought and add the respective ml for the right color.
   - In bottler plan, return a plan that always mixes all available ml into a red, green, or blue potion respectively. Do NOT modify your database in plan!
   - In bottler deliver, record delivery of your bottles. This means, update your ml to subtract the liquid used up and add the potions you just mixed.
   - List the number of red, green, and blue potions currently in inventory in the catalog. If you have 0 of a given potion color, just exclude it from the catalog, do not report as 0 or potion exchange will give you an error.
   - In cart checkout, deduct the potions bought and add the respective amount of gold.
   - in admin reset, make an update call to set your gold back to 100 (already done!) and all other values back to 0.
   - In inventory audit, also return the current total values for ml and number of bottles.
   - Write tests to confirm the above functionality.

8. **Reset Your Shop**
   - Once you've completed your changes, go to [Potion Exchange](https://potion-exchange.vercel.app/) and click "Burn Shop to Ground!" to reset your shop's state.

With this version, your shop should no longer encounter errors due to insufficient gold, missing potion ingredients, or selling non-existent potions.
