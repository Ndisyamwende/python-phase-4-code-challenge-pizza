from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey, Column, Integer, String
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    pizzas = relationship('Pizza', secondary='restaurant_pizzas', back_populates='restaurants')
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant')


    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurants = relationship('Restaurant', secondary='restaurant_pizzas', back_populates='pizzas', cascade='all, delete')


    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }
   
    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    pizza_id = Column(Integer, ForeignKey('pizzas.id'), nullable=False)

    # add relationships
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas', uselist=False)
    pizza = relationship('Pizza', back_populates='restaurants', cascade='all, delete')

    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'restaurant': self.restaurant.to_dict(),
            'pizza': self.pizza.to_dict()
        }


    # add validation
    @validates('price')
    def validate_price(self, key, price):
        assert 1 <= price <= 30, "Price must be between 1 and 30"
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
