#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()

    # Convert restaurants to JSON format
    restaurants_json = []
    for restaurant in restaurants:
        restaurants_json.append({
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        })

    return jsonify(restaurants_json)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    # Convert restaurant to JSON format
    restaurant_json = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'restaurant_pizzas': []
    }

    for restaurant_pizza in restaurant.restaurant_pizzas:
        pizza_data = {
            'id': restaurant_pizza.id,
            'pizza': {
                'id': restaurant_pizza.pizza.id,
                'name': restaurant_pizza.pizza.name,
                'ingredients': restaurant_pizza.pizza.ingredients
            },
            'pizza_id': restaurant_pizza.pizza_id,
            'price': restaurant_pizza.price,
            'restaurant_id': restaurant_pizza.restaurant_id
        }
        restaurant_json['restaurant_pizzas'].append(pizza_data)

    return jsonify(restaurant_json)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    # Delete associated RestaurantPizzas
    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
    for restaurant_pizza in restaurant_pizzas:
        db.session.delete(restaurant_pizza)

    # Delete the restaurant
    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()

    # Convert pizzas to JSON format
    pizzas_json = []
    for pizza in pizzas:
        pizzas_json.append({
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        })

    return jsonify(pizzas_json)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    # Check if the Pizza exists
    pizza = Pizza.query.get(pizza_id)
    if pizza is None:
        return jsonify({'error': 'Pizza not found'}), 404

    # Check if the Restaurant exists
    restaurant = Restaurant.query.get(restaurant_id)
    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    # Create a new RestaurantPizza
    restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)

    # Validate the new RestaurantPizza
    errors = restaurant_pizza.validate()
    if errors:
        return jsonify({'errors': errors}), 400

    # Commit changes to the database
    db.session.add(restaurant_pizza)
    db.session.commit()

    # Return data related to the new RestaurantPizza
    return jsonify({
        'id': restaurant_pizza.id,
        'pizza': {
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        },
        'pizza_id': pizza.id,
        'price': restaurant_pizza.price,
        'restaurant': {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        },
        'restaurant_id': restaurant.id
    }), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
