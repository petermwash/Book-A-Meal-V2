from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api

"""here are my local imports"""
from instance.config import app_config
from .models import db

"""here am initializing sql-alchemy"""
#db = SQLAlchemy()

def create_app(config_name):
	from app.models import User, Meal, Order, OrderDetails

	app = FlaskAPI(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	api = Api(app)
	db.init_app(app)

	class UserSignup(Resource):
		def post(self):
			f_name = request.json.get('f_name')
			l_name = request.json.get('l_name')
			email = request.json.get('email')
			u_name = request.json.get('u_name')
			password = request.json.get('password')
			if u_name is None or password is None or f_name is None\
					or l_name is None or email is None: 
				response = jsonify({"message": "Missing argument"})
				response.status_code = 400
				return response
			users = User.query.all()
			for user in users:
				if user.u_name == u_name:
					response = jsonify({"message": "User already exists!"})
					response.status_code = 405
					return response
			uzer = User(f_name, l_name, email, u_name, password)
			uzer.save()
			response = jsonify({"message": "User created"})
			response.status_code = 201
			return response

	class UserSignin(Resource):
		def post(self):
			u_name = request.json.get('u_name')
			password = request.json.get('password')
			users = User.query.all()
			for user in users:
				if user.u_name == u_name:
					if user.password == password:
						response = jsonify({"message": "Succefully logged in"})
						response.status_code = 200
						return response
					"""verify_password(u_name, password)
					token = g.user.generate_auth_token(600)
					response = jsonify({"token": token.decode('ascii'),
										"duration": 600,
										"message": "User loged in"})"""
					#return response
				response = jsonify({
								"message": "Wrong password or username"
								})
				response.status_code = 401
				return response

	class UpgradeUser():
		def put():
			pass

	class Meals(Resource):
		def get(self):
			meals = Meal.query.all() #get_all()
			res = []

			for meal in meals:
				if not meal:
					response = jsonify({"message": "No meals available!"})
					response.status_code = 404
					return response
				meal_obj = {
					'id': meal.id,
					'm_name': meal.m_name,
					'category': meal.category,
					'price': meal.price
				}
				res.append(meal_obj)
			response = jsonify(res)
			response.status_code = 200
			return response

		def post(self):
			m_name = request.json.get('m_name')
			category = request.json.get('category')
			price = request.json.get('price')
			if m_name is None or category is None\
					or price is None: 
				response = jsonify({"message": "Missing argument!"})
				response.status_code = 400
				return response
			meals = Meal.query.all()
			for meal in meals:
				if meal.m_name == m_name:
					response = jsonify({"message": "Meal already exists!"})
					response.status_code = 405
					return response
			meal = Meal(m_name, category, price)
			meal.save()
			response = jsonify({"message": "Meal added"})
			response.status_code = 201
			return response

	class SingleMeal(Resource):

		def put(self, meal_id):
			meal = Meal.query.filter_by(id=meal_id).first()
			if not meal:
				abort(404)
			m_name = request.json.get('m_name')
			category = request.json.get('category')
			price = request.json.get('price')
			if m_name is not None:
				meal.m_name = m_name
			if category is not None:
				meal.category = category
			if price is not None:
				meal.price = price
			meal.save()
			response = jsonify({"message": "Meal updated"})
			response.status_code = 200
			return response

		def get(self, meal_id):
			meal = Meal.query.filter_by(id=meal_id).first()
			if not meal:
				abort(404)
			response = jsonify({
				'id': meal.id,
				'm_name': meal.m_name,
				'category': meal.category,
				'price': meal.price
				})
			response.status_code = 200
			return response

		def delete(self, meal_id):
			meal = Meal.query.filter_by(id=meal_id).first()
			if not meal:
				abort(404)
			meal.delete()
			response = jsonify({"message": "Meal deleted!"})
			response.status_code = 200
			return response

	class OrderEndpoints(Resource):
		def post(self):
			meal_id = request.json.get('meal_id')
			owner = request.json.get('owner')
			meal_name = request.json.get('meal_name')
			quantity = request.json.get('quantity')
			if owner is None or meal_id is None\
					or quantity is None or meal_name is None: 
				response = jsonify({"message": "Missing argument"})
				response.status_code = 400
				return response
			order = Order(meal_id, meal_name, quantity, owner)
			order.save()
			response = jsonify({"message": "Order created"})
			response.status_code = 201
			return response

		def get(self):
			orders = Order.get_all()
			res = []

			for order in orders:
				"""if not order:
					response = jsonify({"message": "No meals available"})
					response.status_code = 404
					return response"""
				meal_obj = {
					'cart_id': order.cart_id,
					'meal_name': order.meal_name,
					'quantity': order.quantity,
					'owner': order.owner
				}
				res.append(meal_obj)
			response = jsonify(res)
			response.status_code = 200
			return response

		def put(self, order_id):
			order = Order.query.filter_by(id=order_id).first()
			if not order:
				abort(404)
			quantity = request.json.get('quantity')
			if quantity is not None:
				order.quantity = quantity
			order.save()
			response = jsonify({"message": "Order updated"})
			response.status_code = 200
			return response

	class OrderDetsEndpoints(Resource):
		def get(self):
			o = OrderDetails.query.all()
			r = []

			for i in o:
				ob = {
				'id': o.id,
				'order': o.order_cart,
				'ordered_on': date_ordered
				}
				r.append(ob)
			response = jsonify(r)
			response.status_code = 200
			return response


	class MenuEndpoints(Resource):

		menu = []

		def get(self):
			#menu = Menu.query.all() #get_all()
			res = []

			for meal in menu:
				if not meal:
					response = jsonify({"message": "No meals available!"})
					response.status_code = 404
					return response
				meal_obj = {
					'id': meal.id,
					'm_name': meal.m_name,
					'category': meal.category,
					'price': meal.price
				}
				res.append(meal_obj)
			response = jsonify(res)
			response.status_code = 200
			return response

		def post(self, meal_id):
			meals = Meal.query.all()

			for meal in meals:
				for m in  menu:
					if m.meal_id == meal_id:
						response = jsonify({"message": "Meal already exists in menu!"})
						response.status_code = 405
						return response
				if meal.meal_id == meal_id:
					menu.append(meal)
			response = jsonify({"message": "Meal added to menu"})
			response.status_code = 201
			return response


	api.add_resource(UserSignup, '/api/v2/signup')
	api.add_resource(UserSignin, '/api/v2/signin')
	api.add_resource(Meals, '/api/v2/meals')
	api.add_resource(SingleMeal, '/api/v2/meals/<int:meal_id>')
	api.add_resource(MenuEndpoints, '/api/v2/menu', '/api/v2/menu/<int:meal_id>')
	api.add_resource(OrderEndpoints, '/api/v2/orders', '/api/v2/orders/<int:order_id>')
	api.add_resource(OrderDetsEndpoints, '/api/v2/orderst')

	return app
