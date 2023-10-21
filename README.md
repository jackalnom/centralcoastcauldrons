# Central Coast Cauldrons

Central Coast Cauldrons is a stubbed out API meant to serve as a starting point for learning how to build backend servies that integrate with a persistance layer. You will progressively build out your own forked version of the API and integrate with a progressively more sophisticated database backend. When you register your backend at the [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/) simulated customers will shop at your store using your API. 

The application's setting is a simulated fantasy RPG world with adventurers seeking to buy potions. You are one of many shops in this world that offer a variety (over 100k possibilities) of potions.

## Understanding the Game Mechanics

With an initial capital of 100 gold, no potions in your inventory, and devoid of barrels, your backend API is scheduled to be invoked at regular intervals, known as 'ticks' (set at every 5 minutes while testing, but I will later make this happen every 2 hours and align with calendar-time). There are 12 ticks in a day, and 7 days in a week. 

There are three primary actions that may unfold during these ticks:

1. **Customer Interactions**: On each tick, one or more simulated customers access your catalog endpoint intending to buy potions. The frequency and timing of customer visits vary based on the time of day, and each customer exhibits specific potion preferences. Your shop's performance is evaluated and scored based on multiple criteria (more details on [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/)), which in turn influences the frequency of customer visits.

2. **Potion Creation**: Every alternate tick presents an opportunity to brew new potions. Each potion requires 100 ml of either red, green, blue, or dark liquid. You must have sufficient volume of the chosen color in your barrelled inventory to brew a potion.

3. **Barrel Purchasing**: On every alternate tick, you have an opportunity to purchase additional barrels of various colors. Your API receives a catalog of barrels available for sale and should respond with your purchase decisions. The gold cost of each barrel is deducted from your balance upon purchase.

Part of the challenge in these interactions is you are responsible for keeping track of your gold and your various inventory levels. The [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/) separately keeps an authoritiative record (which can be viewed under Shop stats).

### Customers
Customers of various types have different seasonality on when they show up. For example, some customers are more likely to shop on certain days of the week and at certain times of day. Customers each have their own class which has a huge impact on what types of potions that customer is looking for. The amount a customer is willing to spend on a given potion depends on both the customers own level of wealth and how precisely the potions available in a store match their own preference.

Lastly, customers are more likely to shop in a store in the first place that has a good reputation. You can see your shop's reputation with a particular class at [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/). Reputation is based on three different factors:
1. Value: Value is calculated as the delta between the utility the customer gets from a potion (which is increased by getting as close to possible to that customer's preference) and how much the store charges. The highest value is achieved by offering cheap potions that exactly match a customer's preference.
2. Reliability: Reliability is based upon not having errors in the checkout process. Your site being down or offering up potions for sale you don't have in inventory are examples of errors that will hurt reliability.
3. Recognition: Recognition is based upon the number of total successful purchasing trips that customers of that class have had. The more you serve a particular class, the more others of that class will trust to come to you.

For more information please reference the [API Spec](APISpec.md)

## Initial Setup

Follow these steps to get your potion shop up and running:

1. Create your own Github repository based on Central Coast Cauldrons GitHub repository. When creating your repository, name it something unique from centralcoastcauldrons.
2. Register on [Render](https://render.com/). Click New + and select Web Service. We will do a basic Build and deploy from a Git repository. Connect it to your Github repository and point it the new repository you created on step 1.
3. Name your service something cute and unique. Oregon is fine as a region. Leave branch and Root Directory as default. The Runtime should be Python 3. Build command should be pip install -r requirements.txt. Start command should be changed to uvicorn src.api.server:app --host 0.0.0.0 --port $PORT. Select the Free Instance Type. Seelct Advanced and add two environment variables to start. The first is called `API_KEY`. Assign a unique string value to this variable. This string acts as a unique identifier for your shop and helps secure your communications. You will use it later when testing your service and registering it. The second is called `PYTHON_VERSION`. We will set this to 3.11.4.
5. Visit your newly deployed project to ensure it's functioning as expected. Try navigating to https://`your-project`.onrender.com/docs. Once there, click the 'Authorize' button in the upper right corner and enter the same `API_KEY` you entered into environment variables earlier. After authorization, try out various endpoints to confirm their functionality.
6. Navigate to [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/), sign in using your GitHub account, and add your newly created shop to the platform. Be sure to provide the URL of your newly deployed webservice (don't include doc/, just the base url) and the `API_KEY` you set earlier.
7. Return to [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/) to monitor the next tick. Check for changes in your gold balance, potion inventory, and other assets. You should see with even this purely static implementation of your API barrels being purchased, potions getting mixed, and selling some potions to customers.

## Version 1 - Adding persistance

The first version of your improved store will simply keep track of how many red potions are available. Follow these steps:

1. Create an account on [Supabase](https://supabase.com/).
2. We will start with the simplest possible schema: a single row in a single table. Create a new project in Supabase, select the 'Table Editor' on the left-hand navigation menu, and then click the "Create a new table" button. Create a table called `global_inventory`. This table should have columns named `num_red_potions` (int4), `num_red_ml` (int4), and `gold` (int4) to keep track of your current resources.
3. Insert an initial row in your database and set `num_red_potions` to 0, `num_red_ml` to 0, and `gold` to 100.
3. Add your database connection details to the environment variables in your Render project. Within your Supabase project settings, go to Database -> Connection String -> URI, copy the connection string, and replace `PASSWORD` with your database password. Back in Vercel, add this modified string as a new environment variable named `POSTGRES_URI`.

In your backend repository, establish a connection to your Supabase database using SQLAlchemy, drawing the `POSTGRES_URI` from environment variables. To do so, create a database.py file in your src folder with the following code:
```py
import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
```

Next, we will leverage the `global_inventory` table to keep tabs on potion quantities and the total liquid volume in your inventory. Adapt your API to deliver updated JSON responses based on your inventory while maintaining the same API structure. For the sake of simplicity, assume you're only brewing and selling red potions at this stage.

In your endpoint definition files add these imports:
```py
import sqlalchemy
from src import database as db
```

And execute SQL in each of your endpoints (barrels.py, bottler.py, carts.py, and catalog.py) as:
```py
with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
```

You will need to use SELECT and UPDATE sql statements. In this version you won't need to do any INSERTs or DELETEs.

As a very basic initial logic, purchase a new small red potion barrel only if the number of potions in inventory is less than 10. Always mix all available red ml if any exists. Offer up for sale in the catalog only the amount of red potions that actually exist currently in inventory.

Once you've finished making your changes, go back to [Consortium of Concotions and Charms](https://potion-exchange.vercel.app/) and click "Burn Shop to Ground!" at the bottom of the page to reset your shop's state back to the beginning.

With the release of this version, you should no longer encounter job errors resulting from attempting to buy barrels without sufficient gold, mix potions without the necessary ml of ingredients, or sell potions not currently in your inventory.

## Version 2 - Selling more than red potions

In this second version of your shop, you need to also make and sell blue and green potions. You will need to come up with your own logic for when to buy red, green, or blue barrels. Your logic does not have to be particularly clever, you just have to make sure at some point your shop is successfully selling red, green, and blue potions. The implementation details from there are completely up to you.

## Version 3 - Custom Potion Types and Order Management

In the third version of central coast cauldrons, your goal is to:
* support customizable potion mixes and remove all hardcoding of the potions sold from your code. 
* build out a proper order management system for our carts backed by our database.
* Implement audit if you haven’t done so already.

Additionally, please include the SQL used to create and initially populate your database in a file called schema.sql in the root of your github. I will be reviewing this to ensure your database tables are setup correctly.

### Supporting custom potion types
Thus far, you’ve been hardcoding the mixing of potions to pure Red, pure Green, and pure Blue potions. What we are going to do now is create a table in your database where every row indicates a unique potion mixture. Each row will have (at a minimum):
* the type of potion (for example 50 red, 0 green, 50 blue, 0 dark to make a purple potion) that can be made
* all relevant catalog information you will need to offer them for sale. 
* the available inventory of that potion.

Across your endpoints, you must no longer hardcode ANY reference to a particular potion type. The potions your shop makes should be entirely driven by your new table.

To get full points, I need to see at least one purchase occur of a potion that isn't purely red, green, or blue.

### Order management
I encouraged many of you to just use an in-memory structure to handle management of your carts for versions 1 and 2 (for example, a global cart_id that you incremented, and a dictionary to hold cart items.). Now, I am requiring that carts be stored in the database. You should at a minimum have two tables to support your carts: a carts table to reflect a new cart created by a customer and a cart items table to represent a specific item being added to your cart. Foreign key references in the cart items table must be setup correctly (cart items should have at least two…).

### Audit
If you haven’t already, make sure the audit inventory endpoint correctly reflects your gold, number of potions, and number of mls.

## Version 4 - Ledgers

In the fourth version of central coast cauldrons, you will ledgerize your database. Rather than updating inventory values (gold, ml, and potion amounts) directly, you will instead just record changes to values. When calculating the amount of inventory you have, you will instead SUM up your ledger on-the-fly. By doing so, you gain several new advantages:
* You can gain a history of changes made over time
* You can see what your historical inventory levels were at any point in time
* You can reconcile what events caused discrepencies in your inventory levels and undo those events independently of other events

To gain full points on this version, you must convert gold, ml, and potion inventory tracking to a ledgerized design.

### Example of a ledger design
For a concrete example of how you would build a ledger, let's say I was building a database to record the movement of money between groups of people. I could decide I want to model out three entities:
* accounts - An entity representing each person's account. This would include things like the account holder's name, etc.
* account_transactions - An entity representing discrete transactions on people's accounts. This might be something such as Alice transfers Bob $50.
* account_ledger_entries - An entity representing ledger entries aka modifications to people's account balances.

For account_ledger_entries, we have these columns:
* id - The primary key
* account_id - A foreign key reference to the accounts table
* account_transaction_id - A foreign key reference to the account_transactions table
* change - An integer field that represents how much to increase or decrease the account value

For account_transactions, we have these columns:
* id - The primary key
* created_at - When the transaction occurred auto-assigned by current timestamp
* description - A description of the transaction 

If I wanted to record the transaction between Alice and Bob, I would add one row to the account_transactions table:
```SQL
INSERT INTO account_transactions (description) VALUES ('Alice paying back Bob the $50 he lent her');
```
and two rows to the account_ledger_entries table:
```SQL
INSERT INTO account_ledger_entries (account_id, account_transaction_id, change)
VALUES
(:alice_account_id, :transaction_id, -50),
(:bob_account_id, :transaction_id, 50);
```

If I wanted to then get Bob's current account balance, I could then run the following query:
```SQL
SELECT SUM(change) AS balance
FROM account_ledger_entries
WHERE account_id = :bob_account_id;
```

## Version 5 - Order Search

This is the final version of your potion shop. You will now add search functionality to your backend that will power the search orders page on https://potion-exchange.vercel.app/.
<img width="622" alt="image" src="https://github.com/jackalnom/centralcoastcauldrons/assets/26583819/9bd9cee7-973c-4cc5-9676-a0f874b6ce6d">

In the latest pull of carts.py, it now contains a new search endpoint. Do not change the method signature of this endpoint, and ensure that the format of what you return matches the example JSON.

Additionally, make sure you pull the latest server.py. It includes a CORS configuration that is necessary for the front-end to call your webservice.

Once you've implemented the search endpoint, make sure you test your work using the search orders page mentioned above. Filtering, paging, and sorting must all work correctly to get full points on this assignment.

As a reference, feel free to look at this lecture where I cover one way of implementing such a search functionality: https://observablehq.com/@calpoly-pierce/python-connectivity#cell-70.
