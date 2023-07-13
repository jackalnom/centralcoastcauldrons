# Central Coast Cauldrons

Central Coast Cauldrons is a working example ecommerce backend that can be paired with https://potion-exchange.vercel.app/. The current example backend has no persistance store and returns the same json responses every time. The intent is for people to build their own forked versions of Central Coast Cauldrons that add in persistance and logic. The background for the simulation is you are in a fantasy RPG world where adventurers buy potions of various properties. You operate one of many shops with the intention of serving these adventurers and making the most gold possible.

## Basics of the game loop
You start the game with 100 gold, no potions, and no barrels. Every tick (currently defined as every 5 minutes but later I'll move to every 2 hours), your backend API will be called. There are 3 core activities that can happen on these ticks:

1. On every tick, your catalog endpoint will be hit and one or more simulated customers will attempt to purchase the potions you have available for sale. The customers that come at any point in time varies based on time of day and each customer has their own preference for what types of potions they are lookin# Central Coast Cauldrons - Improved Instructions

Central Coast Cauldrons serves as a sample ecommerce backend which can be integrated with the frontend at https://potion-exchange.vercel.app/. As it stands, this backend lacks a persistence store and consistently delivers the same JSON responses. The primary goal is to encourage users to create their own version of Central Coast Cauldrons, incorporating both persistence and custom logic. The simulated environment emulates a fantasy RPG setting where adventurers purchase potions with diverse characteristics. As an operator of a potion shop, your aim is to cater to these adventurers while maximizing profits.

## Understanding the Game Mechanism

Starting with 100 gold, an empty potion inventory, and no barrels, your backend API will be triggered at regular intervals known as 'ticks' (initially set to occur every 5 minutes, with plans to adjust to every 2 hours). Three core actions can occur during these ticks:

1. On each tick, your catalogue endpoint gets accessed by one or more simulated customers intending to buy your potions. Customer visits fluctuate according to the time of day, and each customer has specific potion preferences. Your shop performance is evaluated on several factors (details at https://potion-exchange.vercel.app/), influencing the frequency of customer visits.
2. Every alternate tick provides the opportunity to brew new potions, each containing 100 ml of either red, green, blue, or dark liquid. Required volumes of the chosen color must be present in your barrelled inventory.
3. Every 12th tick presents a chance to purchase extra barrels of various colors. Your API will be prompted with a catalogue of available barrels, and your API should respond with your purchase decisions. The barrel prices, listed in the catalogue, will be deducted from your gold.

## Initial Setup

1. Create a fork of this GitHub repository.
2. Sign up at vercel.com and deploy your forked repository to a new Vercel project.
3. Within Vercel, navigate to Settings -> Environment Variables to create a new environment variable named `API_KEY` and assign it a unique string.
4. Visit https://potion-exchange.vercel.app/, sign in with GitHub, and add your shop to the site. Ensure you provide the URL of your recently deployed Vercel site and insert the `API_KEY` from the previous step.
5. Return to https://potion-exchange.vercel.app/ to check for the upcoming tick. Monitor any changes in your gold and other resources, identify and rectify any job errors that appear.

## Version 1

In your first version, you should integrate basic persistence by following these steps:

1. Register an account at supabase.com.
2. Create a new database featuring a `global_inventory` table. This table should include the following columns: `num_potions`, `num_ml`, and `gold`.
3. Add your database connection details to your Vercel settings. In your Supabase project settings, navigate to Database -> Connection String -> URI and copy this string. Replace `PASSWORD` with your database password, then go back to Vercel and add this as a new environment variable named `SUPABASE_URI`.
4. Connect to your database from your backend repository using SQLAlchemy and pulling the `SUPABASE_URI` from environment variables. Use the `global_inventory` table to monitor potion availability and the volume of liquid in inventory. Modify your API to return appropriately updated JSON responses while maintaining the existing API structure. Initially, assume you're only dealing with red potions for simplicity.

## Version 2

Update your application to incorporate green, blue, and dark potions.

## Version 3

Enhance your application to allow concoctions of red, green, blue, and dark potions. Adjust your potion offerings according to time and customer preferences to boost profits.g for. You will get rated on different criteria (see https://potion-exchange.vercel.app/) which will affect how often customers come to visit your shop.
2. On every other tick, you will have a chance to mix new potions. Each potion consists of 100 ml in a combination of either red, green, blue, or dark. You must have the requisite amount of ml of the appropriate color in your barrelled inventory.
3. Every 12 ticks, you will have a chance to buy additional barrels of a variety of different colors. Your API will be called with the current catalog of available barrels for sale and your API will need to return back what it wants to purchase. These barrels cost a certain amount of gold to purchase as listed in the catalog.

## Initial Setup
1. Fork this github repository.
2. Create an account on vercel.com and deploy your forked github repository to a new vercel project.
3. In vercel, go to Settings->Environment Variables and create a new environment variable named API_KEY and set the value to some unique string.
4. Go to https://potion-exchange.vercel.app/, login with github, then add your new shop to the site. Make sure to use the URL of your newly deployed site on vercel and enter the API_KEY value you set on the previous step.
5. Come back to https://potion-exchange.vercel.app/ and look for the next tick. See if your gold, etc. has changed. See if there are any job errors that popped up and correct if so.

## v1
In your v1 of the application you will want to add some basic persistance. Follow these steps to do so:

1. Create an account on supabase.com
2. Create a new database, with a table called global_inventory. The table should have columns for: num_potions, num_ml, and gold.
3. Add your database connection settings to your vercel. Go to Supabase Project Settings->Database->Connection String->URI and copy the connection string. Replace PASSWORD with the password your database. Go to vercel and add this as a new environment variable called SUPABASE_URI.
4. In your backend repository, connect to your database using sqlalchemy and by reading from the SUPABASE_URI from environment variables. Use the database table to keep track of how many potions are available, how much ml is currently in inventory etc. Modify the json responses returned by your API appropriately while keeping to the same overall API definition. For now, assume you are only dealing in red potions to keep everything simple.

## v2
Modify your application to make green, blue, and dark potions as well.

## v3
Modify your application to make mixtures of red, green, blue, and dark potions. Offer up the appropriate potions at the right time to maximize profit.
