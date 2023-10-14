import sqlalchemy



class Inventory():
    def __init__(self, engine):
        self.engine = engine
        self.gold = 0
        self.num_red_potions = 0
        self.num_red_ml = 0
        self.num_blue_potions = 0
        self.num_blue_ml = 0
        self.num_green_potions = 0
        self.num_green_ml = 0

    def __repr__(self):
        return f"<Inventory {self.inventory_id}>"
    
    def fetch_inventory(self):
        with self.engine.begin() as connection:
            self.num_red_potions, self.num_red_ml, self.gold, self.num_blue_potions,self.num_blue_ml,_,self.num_green_potions,self.num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()

    def set_inventory(self,gold,num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:num_red_ml,num_green_ml=:num_green_ml,num_blue_ml=:num_blue_ml,num_red_potions=:num_red_potions,num_green_potions=:num_green_potions, num_blue_potions=:num_blue_potions ,gold=:gold"),{"num_red_potions":num_red_potions,"num_red_ml":num_red_ml,"gold":gold,"num_blue_potions":num_blue_potions,"num_blue_ml":num_blue_ml,"num_green_potions":num_green_potions,"num_green_ml":num_green_ml,"gold":gold})
        self.fetch_inventory()

    def set_property(self,property,value):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {property}=:value"),{"value":value})
        self.fetch_inventory()