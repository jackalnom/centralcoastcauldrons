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
            _,self.gold,self.num_red_potions, self.num_red_ml, self.num_blue_potions,self.num_blue_ml,self.num_green_potions,self.num_green_ml = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).fetchone()

    def set_property(self,property,value):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {property}=:value"),{"value":value})
        self.fetch_inventory()
    
    def sync(self):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:num_red_ml,num_green_ml=:num_green_ml,num_blue_ml=:num_blue_ml,num_red_potions=:num_red_potions,num_green_potions=:num_green_potions, num_blue_potions=:num_blue_potions ,gold=:gold"),{"num_red_potions":self.num_red_potions,"num_red_ml":self.num_red_ml,"gold":self.gold,"num_blue_potions":self.num_blue_potions,"num_blue_ml":self.num_blue_ml,"num_green_potions":self.num_green_potions,"num_green_ml":self.num_green_ml,"gold":self.gold})
        self.fetch_inventory()

    def get_inventory(self):
        return  self.gold,self.num_red_potions, self.num_red_ml, self.num_blue_potions,self.num_blue_ml,self.num_green_potions,self.num_green_ml
    
    def set_inventory(self,gold,num_red_potions, num_red_ml, num_blue_potions,num_blue_ml,num_green_potions,num_green_ml):
        self.gold = gold
        self.num_red_potions = num_red_potions
        self.num_red_ml = num_red_ml
        self.num_blue_potions = num_blue_potions
        self.num_blue_ml = num_blue_ml
        self.num_green_potions = num_green_potions
        self.num_green_ml = num_green_ml

class PotionInventory():
    def __init__(self, engine):
        self.engine = engine
        self.potion_type = [0,0,0,0]
        self.quantity = 0
        self.sku = ""
        self.price = 0

    def __repr__(self):
        return f"<PotionInventory {self.sku}>"

    def fetch_inventory(self):
        with self.engine.begin() as connection:
            _,self.potion_type,self.quantity,self.sku,self.price = connection.execute(sqlalchemy.text("SELECT * FROM potion_inventory")).fetchone()
        
    def add_potion_type(self,potion_type,quantity,sku,price):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("INSERT INTO potion_inventory (potion_type,quantity,sku,price) VALUES (:potion_type,:quantity,:sku,:price)"),{"potion_type":potion_type,"quantity":quantity,"sku":sku,"price":price})
        self.fetch_inventory()

    def update_quantity(self,potion_type,quantity):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE potion_inventory SET quantity=:quantity WHERE potion_type=:potion_type"),{"quantity":quantity,"potion_type":potion_type})
        self.fetch_inventory()              

    def get_inventory(self):
        return self.potion_type,self.quantity,self.sku,self.price
    
    
