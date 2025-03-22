# Version 1 - Adding Persistence

The first version of your improved store will involve: (1) changing from selling red potions to green potions and (2) adding inventory tracking for your green potions. Follow these steps:

1. **Create an Account on Supabase**
   - Sign up at [Supabase](https://supabase.com/).
   
2. **Set Up the Database**
   - Create a new project in Supabase.
   - Go to the query editor and enter the following SQL:
   ```SQL
   CREATE TABLE global_inventory (
    gold INT NOT NULL, -- tracks the amount of gold in your shop
    red_ml INT NOT NULL, -- tracks the amount of red ml in your inventory
    green_ml INT NOT NULL, -- tracks the amount of green ml in your inventory
    blue_ml INT NOT NULL, -- tracks the amount of blue ml in your inventory
    red_potions INT NOT NULL, -- tracks the number of red potions you have
    green_potions INT NOT NULL, -- tracks the number of green potions you have
    blue_potions INT NOT NULL -- tracks the number of blue potions you have
);```

   - Create a default row by running the following SQL:
```SQL
INSERT INTO global_inventory 
(gold, red_ml, green_ml, blue_ml, red_potions, green_potions, blue_potions) 
VALUES (100, 0, 0, 0, 0, 0, 0);
```
   This sets your gold to 100 and all other values to 0 when starting out.

3. **Configure Database Connection in Render**
   - In Supabase, navigate to **Project Settings > Database** and click "Connect".
   - Copy the connection string and modify it:
     - Replace `postgres://` with `postgresql+psycopg2://`.
     - Replace `[YOUR-PASSWORD]` with your actual password.
     - Avoid special characters in the password to prevent parsing issues.
   - In your Render project, add this modified string as an environment variable named `POSTGRES_URI`.

4. **Connect to the Database in Your Backend**
   - Create a `database.py` file in the `src` folder with the following code:
     ```python
     import os
     import dotenv
     from sqlalchemy import create_engine

     def database_connection_url():
         dotenv.load_dotenv()
         return os.environ.get("POSTGRES_URI")

     engine = create_engine(database_connection_url(), pool_pre_ping=True)
     ```

5. **Modify Your API to Use the Database**
   - Use the `global_inventory` table to track potion quantities and liquid volume.
   - Update your API endpoints to return JSON responses based on your inventory.
   - Assume you are only brewing and selling green potions for now.

6. **Modify Endpoint Definitions**
   - Add the following imports:
     ```python
     import sqlalchemy
     from src import database as db
     ```
   - Execute SQL queries in each endpoint (e.g., `barrels.py`, `bottler.py`, `carts.py`, `catalog.py`) as follows:
     ```python
     with db.engine.begin() as connection:
         result = connection.execute(sqlalchemy.text(sql_to_execute))
     ```
   - Use `SELECT` and `UPDATE` SQL statements (no `INSERT` or `DELETE` needed for now).
   - Refer to the [getting started guide](https://observablehq.com/@calpoly-pierce/getting-started-with-sql-in-python) for SQLAlchemy execution examples.

7. **Implement Basic Business Logic**
   - In barrel plan, randomly pick a color between red, green, and blue. Check if that color has fewer than 5 potions in inventory and if you can afford a small barrel of that color. If both are true, then purchase a small barrel of that color. Do NOT modify your database in plan!
   - In barrel deliver, record delivery of your barrels. This means, update your gold to subtract the cost of barrels bought and add the respective ml for the right color.
   - In bottler plan, return a plan that always mixes all available ml into a red, green, or blue potion respectively. Do NOT modify your database in plan!
   - In bottler deliver, record delivery of your bottles. This means, update your ml to subtract the liquid used up and add the potions you just mixed.
   - List the number of red, green, and blue potions currently in inventory in the catalog. If you have 0 of a given potion color, just exclude it from the catalog, do not report as 0 or potion exchange will give you an error.
   - In cart checkout, deduct the potions bought and add the respective amount of gold.
   - in admin reset, make an update call to set your gold back to 100 and all other values back to 0.
   - Write a unit test to confirm this functionality (this will be checked!).

8. **Reset Your Shop**
   - Once you've completed your changes, go to [Potion Exchange](https://potion-exchange.vercel.app/) and click "Burn Shop to Ground!" to reset your shop's state.

With this version, your shop should no longer encounter errors due to insufficient gold, missing potion ingredients, or selling non-existent potions.

## Testing Locally

To test your changes locally without modifying the production database:

1. **Set Up a Local PostgreSQL Server**
   - Run the following command in your terminal:
     ```sh
     docker run --name mypostgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgres:latest
     ```

2. **Connect to Your Local Database**
   - Download and install [TablePlus](https://tableplus.com/).
   - Create a new connection with the following connection string:
     ```sh
     postgresql://myuser:mypassword@localhost:5432/mydatabase
     ```

3. **Create the `global_inventory` Table Locally**
   - Run the same `CREATE TABLE` and `INSERT` SQL statements you run above in Supabase

4. **Update Your Local Environment Variables**
   - Add the following line to your `.env` file:
     ```sh
     POSTGRES_URI=postgresql://myuser:mypassword@localhost:5432/mydatabase
     ```

