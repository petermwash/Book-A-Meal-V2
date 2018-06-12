from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api
import uuid
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import random

"""here are my local imports"""
from instance.config import app_config


"""here am initializing sql-alchemy"""
db = SQLAlchemy()

def create_app(config_name):
	from app.models import User, Meal, Order, Menu, BlacklistToken

	app = Flask(__name__)
	app.config.from_object(app_config[config_name])
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SECRET_KEY'] = "thisismysupersevrectkeythatyoucannevverguewhatitis"
	handle_exception = app.handle_exception
	handle_user_exception = app.handle_user_exception
	app.handle_exception = handle_exception
	api = Api(app)
	app.handle_user_exception = handle_user_exception
	app.handle_user_exception = handle_user_exception
	app.register_error_handler(404, lambda err: jsonify(
		{"message":"Resource does not exist!",
		"status_code": 404}))
	db.init_app(app)


	def generate_token(public_id, time):
		token = jwt.encode(
			{'public_id':public_id, 'exp': datetime.datetime.utcnow()
			+ datetime.timedelta(minutes=time)}, app.config['SECRET_KEY'])
		return token

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

		 	"""Check if the access_token is blacklisted"""
		 	is_blacklisted_token = BlacklistToken.check_token_blacklist(access_token)
		 	if is_blacklisted_token:
		 		response = jsonify({"message": "User is logged out! You need to sign in again"})
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
			
			if not u_name or not password:
				response = jsonify({"message": "can\'t verify"})
				response.status_code = 400
				return response

			current_user = User.query.filter_by(u_name=u_name).first()
			
			if not current_user:
				response = jsonify({"message": "User {} doesn\'t exist".format(u_name)})
				response.status_code = 404
				return response

			if check_password_hash(current_user.password, password):
				access_token = generate_token(current_user.public_id, 30)
				response = jsonify({
					"message": "Logged in as {}".format(current_user.u_name),
					"access_token": access_token.decode('UTF-8')})
				response.status_code = 200
				return response
			else:
				response = jsonify({"message": "Wrong password or username!"})
				response.status_code = 401
				return response

	class UserLogout(Resource):
		"""This class contains the logout resource"""

		@token_required
		def post(current_user, self):
			auth_token = request.headers['x-access-token']
			blacklist_token = BlacklistToken(token=auth_token)
			
			try:
				blacklist_token.add()
				response = jsonify({"message": "Successfully logged out."})
				response.status_code = 200
				return response

			except Exception as e:
				response = jsonify({"message": e})
				response.status_code = 200
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
			response = jsonify({
				"message": "User {} promoted to admin".format(user.u_name)},
				{
					"id": user.id,
					"u_name": user.u_name,
					"public_id": user.public_id,
					"type_admin": user.type_admin
					})
			response.status_code = 200
			return response

	class Users(Resource):
		"""This class is for inspecting users"""
		
		@token_required
		def get(current_user, self):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

			users = User.query.all()
			uzers = []

			for user in users:
				if not user:
					response = jsonify({"message": "No user found!"})
					response.status_code = 404
					return response

				u = {
					"id": user.id,
					"u_name": user.u_name,
					"public_id": user.public_id,
					"type_admin": user.type_admin
				}
				uzers.append(u)

			response = jsonify(uzers)
			response.status_code = 200
			return response

		def post(self):
			"""
			Here I'm creating an initial admin user
			This user can be created only once
			"""

			users = User.query.all()
			for user in users:
				if user.u_name == "Admin" or\
						user.email == "admin@pemwa.com":
					response = jsonify({"message": "Super User already exists!"})
					response.status_code = 202
					return response

			admin = User(public_id = str(uuid.uuid4()),
				f_name = "Purity", l_name = "Resian",
				email = "admin@pemwa.com", u_name = "Admin",
				password = generate_password_hash("pass", method='sha256'),
				type_admin = True)
			admin.save()
			response = jsonify({"message": "Super User created!"})
			response.status_code = 201
			return response

		@token_required
		def delete(current_user, self, user_id):
			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response
			
			user = User.query.filter_by(id=user_id).first()
			if not user:
				response = jsonify({"message": "The user does not exist"})
				response.status_code = 404
				return response

			user.delete()

			response = jsonify({"message": "User deleted!"})
			response.status_code = 200
			return response
			
	class ChangePasswordAPI(Resource):
		"""This resource is for changing the old password to the new password"""

		@token_required
		def post(current_user, self):
			old_password = request.json.get('old_password')
			new_password = request.json.get('new_password')

			if old_password is None or new_password is None:
				response = jsonify({"message": "Missing argument!"})
				response.status_code = 400
				return response

			user = User.query.filter_by(id=current_user.id).first()
			if not check_password_hash(user.password, old_password):
				response = jsonify({"message": "Old password is not correct!"})
				response.status_code = 401
				return response

			user.password = generate_password_hash(
				new_password, method='sha256')
			user.save()

			response = jsonify({"message": "Password changed Successfully"})
			response.status_code = 200
			return response

	class ForgetPasswordAPI(Resource):
		"""This class contains resources to reset forgotten password"""

		def get(self):
			"""Reset user's password and return the temporary password"""
			
			if 'x-access-token' in request.headers:
				reset_token = request.headers['x-access-token']

			if not reset_token:
				response = jsonify({"message": "Token is  mising!"})
				response.status_code = 400
				return response

			try:
				data = jwt.decode(reset_token, app.config['SECRET_KEY'])
				user = User.query.filter_by(public_id=data['public_id']).first()

			except:
				response = jsonify({"message": "Token is invalid!"})
				response.status_code = 401
				return response

			temp_password = (''.join(str(random.randint(0, 9)) for x in range(8)))
			user.password = generate_password_hash(temp_password)
			user.save()

			response = jsonify({
		 		"message": "Your temporary password is: {}".format(
		 			temp_password)})
			response.status_code = 200
			return response

		def post(self):
			"""
			Verify the information from user and
			Return a reset token if the information is correct
			"""
			email = request.json.get('email')
			if email is None:
				response = jsonify({"message": "Missing argument!"})
				response.status_code = 400
				return response

			user = User.query.filter_by(email=email).first()
			if user is None:
				response = jsonify({"message": "No user associated with the email!"})
				response.status_code = 404
				return response

			reset_token = generate_token(user.public_id, 5)
			response = jsonify({
					"message": "Reset token returned to let you reset password",
					"Reset_token": reset_token.decode('UTF-8')})
			response.status_code = 200
			return response

	class Meals(Resource):
		"""This class contains resources for manipulating meals"""

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

			if not isinstance(price, float):
				response = jsonify({"message": "Price has to be a float number!"})
				response.status_code = 400
				return response

			meals = Meal.query.all()
			for meal in meals:
				if meal.m_name == m_name:
					response = jsonify({"message": "Meal already exists!"})
					response.status_code = 202
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
				response = jsonify({"message": "The meal does not exist"})
				response.status_code = 404
				return response

			m_name = request.json.get('m_name')
			category = request.json.get('category')
			price = request.json.get('price')

			if m_name is None and category is None and price is None:
				response = jsonify(
					{"message": "You need to provide at least one argument!"})
				response.status_code = 400
				return response

			if m_name is not None:
				meal.m_name = m_name

			if category is not None:
				meal.category = category

			if price is not None:
				if not isinstance(price, float):
					response = jsonify({"message": "Price has to be a float number!"})
					response.status_code = 400
					return response
				else:
					meal.price = price

			meal.save()

			response = jsonify({"message": "Meal updated"},
				{
				'id': meal.id,
				'm_name': meal.m_name,
				'category': meal.category,
				'price': meal.price
				})
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
				response = jsonify({"message": "The meal does not exist"})
				response.status_code = 404
				return response

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
				response = jsonify({"message": "The meal does not exist"})
				response.status_code = 404
				return response

			meal.delete()

			response = jsonify({"message": "Meal deleted!"})
			response.status_code = 200
			return response

	class OrderEndpoints(Resource):
		"""This class contains resources for manipulating orders"""

		@token_required
		def post(current_user, self):
			
			meal_name = request.json.get('meal_name')
			quantity = request.json.get('quantity')

			today8am = datetime.datetime.now().replace(
				hour=8, minute=0, second=0, microsecond=0)
			today12am = datetime.datetime.now().replace(
				hour=0, minute=0, second=0, microsecond=0)
			if datetime.datetime.now() > today12am and\
					datetime.datetime.now() < today8am:
				response = jsonify(
					{"message": "This functionality not available at this time"}
					)
				response.status_code = 404
				return response

			if quantity is None or meal_name is None: 
				response = jsonify({"message": "Missing argument"})
				response.status_code = 400
				return response

			if not isinstance(quantity, int):
				response = jsonify({"message": "Quantity has to be an integer Number"})
				response.status_code = 400
				return response

			owner = User.query.filter_by(u_name=current_user.u_name).first()
			order = Order(meal_name, quantity, owner.u_name)
			order.save()

			response = jsonify({"message": "Order succesfully posted"})
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
										'id': order.id,
										'meal_name': order.meal_name,
										'quantity': order.quantity
										},
							'ordered_on': order.ordered_on
					
							}
				res.append(meal_obj)

			response = jsonify(res)
			response.status_code = 200
			return response

		@token_required
		def put(current_user, self, order_id):
			
			me = User.query.filter_by(u_name=current_user.u_name).first()
			order = Order.query.filter_by(id=order_id).first()

			today8am = datetime.datetime.now().replace(
				hour=8, minute=0, second=0, microsecond=0)
			today12am = datetime.datetime.now().replace(
				hour=0, minute=0, second=0, microsecond=0)
			if datetime.datetime.now() > today12am and\
					datetime.datetime.now() < today8am:
				response = jsonify(
					{"message": "This functionality not available at this time"}
					)
				response.status_code = 404
				return response

			if me.u_name != order.owner:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

			if not order:
				response = jsonify({"message": "That order is not available"})
				response.status_code = 404
				return response

			quantity = request.json.get('quantity')
			meal_name = request.json.get('meal_name')

			if quantity is None and meal_name is None:
				response = jsonify(
					{"message": "You need to provide at least one argument!"})
				response.status_code = 400
				return response
			
			if quantity is not None:
				if not isinstance(quantity, int):
					response = jsonify(
						{"message": "Quantity has to be an integer Number"})
					response.status_code = 400
					return response
				order.quantity = quantity

			if meal_name is not None:
				order.meal_name =meal_name

			order.save()

			response = jsonify({"message": "Order updated"},
				{order.owner: {
										'id': order.id,
										'meal_name': order.meal_name,
										'quantity': order.quantity
										},
								'ordered_on': order.ordered_on
					
							})
			response.status_code = 200
			return response

		@token_required
		def delete(current_user, self, order_id):
			
			me = User.query.filter_by(u_name=current_user.u_name).first()
			order = Order.query.filter_by(id=order_id).first()

			today8am = datetime.datetime.now().replace(
				hour=8, minute=0, second=0, microsecond=0)
			today12am = datetime.datetime.now().replace(
				hour=0, minute=0, second=0, microsecond=0)
			if datetime.datetime.now() > today12am and\
					datetime.datetime.now() < today8am:
				response = jsonify(
					{"message": "This functionality not available at this time"}
					)
				response.status_code = 404
				return response

			if not order:
				response = jsonify({"message": "That order is not available"})
				response.status_code = 404
				return response

			if me.u_name != order.owner:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

			try:
				order.delete()
				response = jsonify({"message": "Order deleted succesfully"})
				response.status_code = 200
				return response

			except Exception as e:
				response = jsonify({"message": e})
				response.status_code = 200
				return response


	class MenuEndpoints(Resource):

		"""This class contains resources for manipulating the menu"""

		@token_required
		def get(current_user, self):

				menu = Menu.get_all()

				if not menu:
					response = jsonify({"message": "Menu not set yet!"})
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

		@token_required
		def delete(current_user, self):
			"""Clear all the contents in menu"""

			if not current_user.type_admin:
				response = jsonify({"message": "Not authorized to perform this function!"})
				response.status_code = 401
				return response

			menu = Menu.get_all()
			if not menu:
				response = jsonify({"message": "Menu not set yet!"})
				response.status_code = 404
				return response
			try:
				Menu.clear()
				response = jsonify({"message": "Menu cleared succesfully"})
				response.status_code = 200
				return response

			except Exception as e:
				response = jsonify({"message": e})
				response.status_code = 200
				return response

	api.add_resource(UserSignup, '/api/v2/auth/signup')
	api.add_resource(UserSignin, '/api/v2/auth/login')
	api.add_resource(Meals, '/api/v2/meals')
	api.add_resource(SingleMeal, '/api/v2/meals/<int:meal_id>')
	api.add_resource(MenuEndpoints, '/api/v2/menu', '/api/v2/menu/<int:meal_id>')
	api.add_resource(OrderEndpoints, '/api/v2/orders', '/api/v2/orders/<int:order_id>')
	api.add_resource(UpgradeUser, '/api/v2/upgrade/<int:id>')
	api.add_resource(Users, '/api/v2/users', '/api/v2/users/<int:user_id>')
	api.add_resource(UserLogout, '/api/v2/auth/logout')
	api.add_resource(ChangePasswordAPI, '/api/v2/auth/changepass')
	api.add_resource(ForgetPasswordAPI, '/api/v2/auth/resetpass')


	return app
