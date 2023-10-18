from typing import List
from pydantic import BaseModel
import sqlalchemy



class Inventory():
    def __init__(self, engine):
        self.engine = engine
        self.gold = 0
        self.num_red_ml = 0
        self.num_blue_ml = 0
        self.num_green_ml = 0

    def __repr__(self):
        return f"<Inventory {self.inventory_id}>"
    
    def fetch_inventory(self):
        with self.engine.begin() as connection:
            _,self.gold, self.num_red_ml,self.num_blue_ml,self.num_green_ml,_ = connection.execute(sqlalchemy.text("SELECT * FROM inventory")).fetchone()

    def set_property(self,property,value):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text(f"UPDATE inventory SET {property}=:value"),{"value":value})
        self.fetch_inventory()
    
    def sync(self):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE inventory SET num_red_ml=:num_red_ml,num_green_ml=:num_green_ml,num_blue_ml=:num_blue_ml ,gold=:gold"),{"num_red_ml":self.num_red_ml,"gold":self.gold,"num_blue_ml":self.num_blue_ml,"num_green_ml":self.num_green_ml,"gold":self.gold})
        self.fetch_inventory()

    def get_inventory(self):
        return  self.gold, self.num_red_ml,self.num_blue_ml,self.num_green_ml
    
    def set_inventory(self,gold, num_red_ml,num_blue_ml,num_green_ml):
        self.gold = gold
        self.num_red_ml = num_red_ml
        self.num_blue_ml = num_blue_ml
        self.num_green_ml = num_green_ml

class PotionsInventory():
    def __init__(self, engine):
        self.engine = engine

    def __repr__(self):
        return f"<PotionInventory {self.sku}>"

        
    def add_potion_type(self,potion_type,quantity,sku,price):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("INSERT INTO potions_inventory (potion_type,quantity,sku,price) VALUES ( :potion_type,:quantity,:sku,:price)"),{"potion_type":potion_type,"quantity":quantity,"sku":sku,"price":price})

    def update_quantity(self,potion_type,quantity):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE potions_inventory SET quantity=:quantity WHERE potion_type=  :potion_type"),{"quantity":quantity,"potion_type":potion_type})

    def get_inventory(self):
        with self.engine.begin() as connection:
            entries =  connection.execute(sqlalchemy.text("SELECT * FROM potions_inventory")).fetchall()
            return entries
        
    def get_entry(self,potion_type):
        with self.engine.begin() as connection:
            return connection.execute(sqlalchemy.text("SELECT * FROM potions_inventory WHERE potion_type=  :potion_type"),{"potion_type":potion_type}).fetchone()

    def reset_quantities(self):
        inventory = self.get_inventory()
        for entry in inventory:
            self.update_quantity(entry[1],0)


class CartItem(BaseModel):
    quantity: int
    potion: int

class Cart(BaseModel):
    items: List[CartItem]
    customer: str
    cart_id: int

class CartModel:

    def __init__(self,engine) -> None:
        self.engine = engine


    
    def get_inventory(self):
        with self.engine.begin() as connection:
            return connection.execute(sqlalchemy.text("SELECT * FROM cart")).fetchall()
        
    def get_entry(self,cart_id):
        with self.engine.begin() as connection:
             # get all cart items for cart id
            items_result =  connection.execute(sqlalchemy.text("SELECT * FROM cart,cart_items WHERE cart.id=cart_items.cart_id AND cart.id=:cart_id"),{"cart_id":cart_id}).fetchall()
            print(items_result)
            items = []
            for item in items_result:
                items.append(CartItem(quantity=item[4],potion=item[3]))
            cart = connection.execute(sqlalchemy.text("SELECT * FROM cart WHERE id=:cart_id"),{"cart_id":cart_id}).fetchone()
            
            return Cart(items=(items if len(items)  > 0 else []),customer=cart[1],cart_id=cart_id)
        
    def delete_cart(self,cart_id):
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("DELETE FROM cart_items WHERE cart_id=:cart_id"),{"cart_id":cart_id})
            connection.execute(sqlalchemy.text("DELETE FROM cart WHERE id=:cart_id"),{"cart_id":cart_id})
    
    def get_carts(self) -> [Cart] :
        carts = []
        for cart in self.get_inventory():
            carts.append(self.get_entry(cart[0]))
        return carts
    
    def create_cart(self,customer):
        with self.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("INSERT INTO cart (customer) VALUES (:customer) RETURNING id"),{"customer":customer}).fetchone()
            return Cart(items=[],customer=customer,cart_id=result[0])

    def update_cart(self,cart : Cart):
        # use update sql commands to change data in place without deleting
        
        with self.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE cart SET customer=:customer WHERE id=:cart_id"),{"customer":cart.customer,"cart_id":cart.cart_id})
            connection.execute(sqlalchemy.text("DELETE FROM cart_items WHERE cart_id=:cart_id"),{"cart_id":cart.cart_id})
            for item in cart.items:
                connection.execute(sqlalchemy.text("INSERT INTO cart_items (potion_id,quantity,cart_id) VALUES (:potion_id,:quantity,:cart_id)"),{"potion_id":item.potion,"quantity":item.quantity,"cart_id":cart.cart_id})
            

        return self.get_entry(cart.cart_id)
    
    def reset_carts(self):
        carts = self.get_carts()
        for cart in carts:
            self.delete_cart(cart.cart_id)
    
    



    
        
        