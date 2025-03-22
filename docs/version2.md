# Version 2 - Custom Potion Types and Order Management

In the third version of central coast cauldrons, your goal is to:
* Support customizable potion mixes and remove all hardcoding of the potions sold from your code. 
* Build out a proper order management system for our carts backed by our database.
* Implement audit if you haven't done so already.
* Write automated tests that cover all of the above.

Additionally, please include the SQL used to create and initially populate your database in a file called schema.sql in the root of your github. I will be reviewing this to ensure your database tables are setup correctly.

### Supporting custom potion types
Thus far, you've been hardcoding the mixing of potions to pure Red, pure Green, and pure Blue potions. What we are going to do now is create a table in your database where every row indicates a unique potion mixture. Each row will have (at a minimum):
* The type of potion (for example 50 red, 0 green, 50 blue, 0 dark to make a purple potion) that can be made
* All relevant catalog information you will need to offer them for sale. 
* The available inventory of that potion.

Across your endpoints, you must no longer hardcode ANY reference to a particular potion type. The potions your shop makes should be entirely driven by your new table.

To get full points, I need to see at least one purchase occur of a potion that isn't purely red, green, or blue.

### Order management
I encouraged many of you to just use an in-memory structure to handle management of your carts for versions 1 and 2 (for example, a global cart_id that you incremented, and a dictionary to hold cart items.). Now, I am requiring that carts be stored in the database. You should at a minimum have two tables to support your carts: a carts table to reflect a new cart created by a customer and a cart items table to represent a specific item being added to your cart. Foreign key references in the cart items table must be setup correctly (cart items should have at least two…).

