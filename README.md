# Central Coast Cauldrons

Central Coast Cauldrons serves as a fully operational ecommerce backend demonstration that integrates seamlessly with [Potion Exchange](https://potion-exchange.vercel.app/). Its current version lacks persistent data storage and sends identical JSON responses on every interaction. The project's primary objective is to encourage developers to fork and modify Central Coast Cauldrons by introducing persistence and custom logic.

The application's setting is a simulated fantasy RPG world teeming with adventurers seeking to buy potions with various magical properties. You are entrusted with the operation of one of the many shops within this world. Your challenge? Catering to the needs of these adventurers while optimizing your profits.

## Understanding the Game Mechanics

With an initial capital of 100 gold, no potions in your inventory, and devoid of barrels, your backend API is scheduled to be invoked at regular intervals, known as 'ticks' (set at every 5 minutes initially, with plans for future extension to every 2 hours). There are three primary actions that may unfold during these ticks:

1. **Customer Interactions**: On each tick, one or more simulated customers access your catalogue endpoint intending to buy potions. The frequency and timing of customer visits vary based on the time of day, and each customer exhibits specific potion preferences. Your shop's performance is evaluated and scored based on multiple criteria (more details on [Potion Exchange](https://potion-exchange.vercel.app/)), which in turn influences the frequency of customer visits.

2. **Potion Creation**: Every alternate tick presents an opportunity to brew new potions. Each potion requires 100 ml of either red, green, blue, or dark liquid. You must have sufficient volume of the chosen color in your barrelled inventory to brew a potion.

3. **Barrel Purchasing**: On every 12th tick, you have an opportunity to purchase additional barrels of various colors. Your API receives a catalogue of barrels available for sale and should respond with your purchase decisions. The gold cost of each barrel is deducted from your balance upon purchase.

## Initial Setup

Follow these steps to get your potion shop up and running:

1. Fork the Central Coast Cauldrons GitHub repository.
2. Register on [Vercel](https://vercel.com/) and deploy your forked repository as a new Vercel project.
3. Inside Vercel, go to Settings -> Environment Variables to create a new environment variable named `API_KEY`. Assign a unique string value to this variable. This string acts as a unique identifier for your shop and helps secure your communications.
4. Navigate to [Potion Exchange](https://potion-exchange.vercel.app/), sign in using your GitHub account, and add your newly created shop to the platform. Be sure to provide the URL of your newly deployed Vercel site and the `API_KEY` you set earlier.
5. Return to [Potion Exchange](https://potion-exchange.vercel.app/) to monitor the next tick. Check for changes in your gold balance, potion inventory, and other assets. Also, pay attention to any job errors that appear and take corrective action if necessary.

## Version 1

The first version of your application should introduce basic persistence. Follow these steps:

1. Create an account on [Supabase](https://supabase.com/).
2. Build a new database featuring a `global_inventory` table. This table should have columns named `num_potions`, `num_ml`, and `gold` to keep track of your current resources.
3. Add your database connection details to your Vercel environment variables. Within your Supabase project settings, go to Database -> Connection String -> URI, copy the connection string, and replace `PASSWORD` with your actual database password. Back in Vercel, add this modified string as a new environment variable named `SUPABASE_URI`.
4. In your backend repository, establish a connection to your Supabase database using SQLAlchemy, drawing the `SUPABASE_URI` from environment variables. Leverage the `global_inventory` table to keep tabs on potion quantities and the total liquid volume in your inventory. Adapt your API to deliver updated JSON responses based on your inventory while maintaining the same API structure. For the sake of simplicity, assume you're only brewing and selling red potions at this stage.

## Version 2

Enhance your application to include not just red, but also green, blue, and dark potions in your offerings. You will need to adjust your `global_inventory` table and relevant API responses accordingly.

## Version 3

Further upgrade your application to produce mixtures of red, green, blue, and dark potions. These mixed potions could appeal to a wider range of customers and fetch higher profits. Modify your offerings based on time, customer preferences, and market demand to maximize your returns. This phase will require sophisticated logic and possibly machine learning algorithms to predict and match customer preferences accurately.
