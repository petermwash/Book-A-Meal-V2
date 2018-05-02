from flask_restful import Resource, Api
import json

"""here are my local imports"""
from app import create_app, db
from  models import User

config_name = os.getenv('APP_SETTINGS') # config_name = "development")
app = create_app(config_name)
api = Api(app)

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
		"""
		for u in users:
			if u.u_name == u_name:
				response = jsonify({"message": "User already exists"})
				response.status_code = 400
				return response
				"""
		uzer = User(f_name, l_name, email, u_name, password)
		uzer.save()
		#users.append(uzer)
		response = jsonify({"message": "User created"})
		response.status_code = 201
		return response

class UserSignin(Resource):
	def post(self):
		pass

class Meals(Resource):
	def post(self):
		pass

	def get(self):
		pass

	def put(self):
		pass

	def delete(self):
		pass

class MenuEndpoints(Resource):
	def post(self):
		pass

	def get(self):
		pass

class OrderEndpoints(Resource):
	def post(self):
		pass

	def get(self):
		pass

	def put(self):
		pass

	def delete(self):
		pass


api.add_resource(UserSignup, '/api/v2/signup')
api.add_resource(UserSignin, '/api/v2/signin')
api.add_resource(Meals, '/api/v2/meals', '/api/v2/meals/<int:meal_id>')
api.add_resource(MenuEndpoints, '/api/v2/menu')
api.add_resource(OrderEndpoints, '/api/v2/orders', '/api/v2/orders/<int:order_id>')
