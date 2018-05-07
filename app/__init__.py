from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api
import uuid
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

"""here are my local imports"""
from instance.config import app_config


"""here am initializing sql-alchemy"""
db = SQLAlchemy()

def create_app(config_name):
	from app.models import User, Meal, Order, Menu

	app = Flask(__name__)
	app.config.from_object(app_config[config_name])
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SECRET_KEY'] = "thisismysupersevrectkeythatyoucannevverguewhatitis"
	api = Api(app)
	db.init_app(app)

	def token_required(f):
		 @wraps(f)
		 def decorated(*args, **kwargs):
		 	access_token = None

		 	if 'x-access-token' in request.headers:
		 		access_token = request.headers['x-access-token']

		 	if not access_token:
		 		response = jsonify({"message": "Token is  mising!. You need to sign in first"})
		 		response.status_code = 401
		 		return response

		 	try:
		 		data = jwt.decode(access_token, app.config['SECRET_KEY'])
		 		current_user = User.query.filter_by(public_id=data['public_id']).first()
		 	except:
		 		response = jsonify({"message": "Token is invalid!. You need to sign in first"})
		 		response.status_code = 401
		 		return response

		 	return f(current_user, *args, **kwargs)

		 return decorated

	class UserSignup(Resource):
		"""This class contains signup resource"""
		
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
				if user.u_name == u_name or user.email == email:
					response = jsonify({"message": "User already exists!"})
					response.status_code = 202
					return response

			hashed_pasword = generate_password_hash(password, method='sha256')
			public_id = str(uuid.uuid4())

			uzer = User(public_id, f_name, l_name, email, u_name, hashed_pasword)
			uzer.save()
			response = jsonify({"message": "New user created!"})
			response.status_code = 201
			return response

	class UserSignin(Resource):
		"""This class contains signin resource"""
		
		def post(self):
			u_name = request.json.get('u_name')
			password = request.json.get('password')
			#auth = request.authorization

			#if not auth or not auth.username or not auth.password:
			if not u_name or not password:
				response = jsonify({"message": "can\'t verify"})
				response.status_code = 401
				return response

			current_user = User.query.filter_by(u_name=u_name).first()
			
			if not current_user:
				response = jsonify({"message": "User {} doesn\'t exist".format(u_name)})
				response.status_code = 404
				return response

			if check_password_hash(current_user.password, password):
				access_token = jwt.encode({'public_id': current_user.public_id, 'exp': datetime.datetime.utcnow()
					+ datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
				response = jsonify({
					"message": "Logged in as {}".format(current_user.u_name),
					"access_token": access_token.decode('UTF-8')})
				response.status_code = 200
				return response
			else:
				response = jsonify({"message": "Wrong password or username!"})
				response.status_code = 401
				return response


	class UpgradeUser(Resource):
		"""This class contains resource  to give a user admin rights"""
		
		@token_required
		def put(current_user, self, id):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response
				
			user = User.query.filter_by(id=id).first()

			if not user:
				response = jsonify({"message": "User {} doesn\'t exist".format(id)})
				response.status_code = 404
				return response

			user.type_admin = True
			user.save()
			response = jsonify({"message": "User {} promoted to admin".format(user.u_name)})
			response.status_code = 200
			return response

	class Users(Resource):
		"""This class is for inspecting users"""
		
		@token_required
		def get(current_user, self):
			users = User.query.all()
			uzers = []

			for user in users:
				if not user:
					return jsonify({"message": "No user found!"})

				u = {
					"id": user.id,
					"u_name": user.u_name,
					"public_id": user.public_id,
					"type_admin": user.type_admin
				}
				uzers.append(u)

			return uzers

	class Meals(Resource):
		"""This class contains resources for maniputating meals"""

		@token_required
		def get(current_user, self):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

			meals = Meal.query.all()
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

		@token_required
		def post(current_user, self):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

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
		"""This class contains resource for maniputating a single meal"""

		@token_required
		def put(current_user, self, meal_id):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

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

		@token_required
		def get(current_user, self, meal_id):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

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

		@token_required
		def delete(current_user, self, meal_id):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response
			
			meal = Meal.query.filter_by(id=meal_id).first()
			if not meal:
				abort(404)

			meal.delete()
			response = jsonify({"message": "Meal deleted!"})
			response.status_code = 200
			return response

	class OrderEndpoints(Resource):
		"""This class contains resources for maniputating orders"""

		@token_required
		def post(current_user, self):
			
			owner = request.json.get('owner')
			meal_name = request.json.get('meal_name')
			quantity = request.json.get('quantity')

			if owner is None or quantity is None or meal_name is None: 
				response = jsonify({"message": "Missing argument"})
				response.status_code = 400
				return response

			order = Order(meal_name, quantity, owner)
			order.save()
			response = jsonify({"message": "Order sccesfully posted"})
			response.status_code = 201
			return response

		@token_required
		def get(current_user, self):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response
			
			orders = Order.get_all()
			res = []

			if not orders:
				response = jsonify({"message": "No order available"})
				response.status_code = 404
				return response

			for order in orders:	
				meal_obj = {order.owner: {
										'meal_name': order.meal_name,
										'quantity': order.quantity

										}
					
							}
				res.append(meal_obj)

			response = jsonify(res)
			response.status_code = 200
			return response

		@token_required
		def put(current_user, self, order_id):
			
			me = User.query.filter_by(u_name=current_user.u_name).first()
			order = Order.query.filter_by(id=order_id).first()

			if not me:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response
			
			if not order:
				abort(404)

			quantity = request.json.get('quantity')
			if quantity is not None:
				order.quantity = quantity

			order.save()
			response = jsonify({"message": "Order updated"})
			response.status_code = 200
			return response


	class MenuEndpoints(Resource):

		"""This class contains resources for maniputating the menu"""

		@token_required
		def get(current_user, self):

				menu = Menu.get_all()

				if not menu:
					response = jsonify({"message": "No meals available  in menu!"})
					response.status_code = 404
					return response

				res = []

				for meal in menu:
					meal_obj = {
								meal.id:{
										'meal_name': meal.m_name,
										'category': meal.category,
										'price': meal.price
										}
								}
					res.append(meal_obj)
				
				response = jsonify(res)
				response.status_code = 200
				return response

		@token_required
		def post(current_user, self, meal_id):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

			meal = Meal.query.filter_by(id=meal_id).first()
				
			if not meal:
				response = jsonify({"message": "Meal not available"})
				response.status_code = 404
				return response
				
			menus = Menu(meal.m_name, meal.category, meal.price)
			menus.save()

			response = jsonify({"message": "Meal added to menu"})
			response.status_code = 200
			return response

	api.add_resource(UserSignup, '/api/v2/auth/signup')
	api.add_resource(UserSignin, '/api/v2/auth/login')
	api.add_resource(Meals, '/api/v2/meals')
	api.add_resource(SingleMeal, '/api/v2/meals/<int:meal_id>')
	api.add_resource(MenuEndpoints, '/api/v2/menu', '/api/v2/menu/<int:meal_id>')
	api.add_resource(OrderEndpoints, '/api/v2/orders', '/api/v2/orders/<int:order_id>')
	api.add_resource(UpgradeUser, '/api/v2/upgrade/<int:id>',)
	api.add_resource(Users, '/api/v2/users')


	return app
