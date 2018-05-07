import os
import unittest
import json
import uuid

"""here are my local imports"""
from app import create_app, db

class UserTestCase(unittest.TestCase):

	"""This class will contain tests for a user endpoits"""
	
	def setUp(self):
		"""Defininng test varibles to be used and initialize the app"""
		# import ipdb; ipdb.set_trace()
		self.app = create_app("testing")
		self.client = self.app.test_client
		self.user_data = {
			'f_name': 'Peter',
			'l_name': 'Mwaura',
			'u_name': 'Pemwa',
			'email': 'pemwa@gm.com',
			'password': '12345'
		}

		"""
		Binding the app with the current context
		and creating all tables
		"""
		with self.app.app_context():
			db.session.close()
			db.drop_all()
			db.create_all()

	def test_user_creation(self):
		"""Test that API can register a user"""
		response = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "New user created!")
		self.assertEqual(response.status_code, 201)

	def test_user_creation_without_all_fields(self):
		"""Test that a user cannot be registered without filling all fields."""
		response = self.client().post(
			'/api/v2/auth/signup', data = json.dumps({
				"f_name":"peter",
				"l_name":"peter",
				"u_name":"peter",
				"email":"my.email@gmail.com"
				}), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Missing argument")
		self.assertEqual(response.status_code, 400)

	def test_already_registered_user(self):
		"""Test that a user cannot be registered twice."""
		response = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)
		response = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "User already exists!")
		self.assertEqual(response.status_code, 202)

	def test_user_login(self):
		"""Test that registered user can sign in."""
		response = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)
		signin = self.client().post(
			'/api/v2/auth/login', data = json.dumps({
				'u_name': 'Pemwa',
				'password': '12345'
				}) , content_type = 'application/json')
		result = json.loads(signin.data)
		self.assertEqual(signin.status_code, 200)

	def test_non_registered_user_login(self):
		"""Test that non registered users cannot sign in"""
		wrong_data = {
				'u_name': 'Mwash',
				'password': '12345'
		}
		response = self.client().post(
			'/api/v2/auth/login', data = json.dumps(
			 wrong_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(response.status_code, 404)
		self.assertEqual(result["message"], "User {} doesn\'t exist".format(
			wrong_data['u_name']))

	def test_user_login_with_wrong_password(self):
		"""Test that users cannot sign in with wrong password"""
		response = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)
		signin = self.client().post(
			'/api/v2/auth/login', data = json.dumps({
				'u_name': 'Pemwa',
				'password': 'wrong_abc'
				}) , content_type = 'application/json')
		result = json.loads(signin.data)
		self.assertEqual(signin.status_code, 401)
		self.assertEqual(result["message"], "Wrong password or username!")


	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

class MealTestCase(unittest.TestCase):
	"""This class represents the meals test cases"""

	def setUp(self):
		self.app = create_app("testing")
		self.client = self.app.test_client
		self.meal_data = {
					"m_name":"Burger",
					"category":"Snacks",
					"price":400.00
					 }

		"""Binding the app with the current context and creating all tables"""
		with self.app.app_context():
			db.session.close()
			db.drop_all()
			db.create_all()

	def register_a_user(self,public_id=str(uuid.uuid4()),f_name='Peter',
			l_name='Mwaura',u_name='Pemwa',email='pemwa@gm.com',password='12345'):
		user_data = {
			'public_id': str(uuid.uuid4()),
			'f_name': 'Peter',
			'l_name': 'Mwaura',
			'u_name': 'Pemwa',
			'email': 'pemwa@gm.com',
			'password': '12345'
		}
		return self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				user_data) , content_type = 'application/json')

	def login_user(self, u_name="Pemwa", password="12345"):
		user_data = {
			'u_name': 'Pemwa',
			'password': '12345'
		}
		return self.client().post(
			'/api/v2/auth/login', data = json.dumps(
				user_data) , content_type = 'application/json')
	
	def upgrade_user(self):
		return self.client().put('/api/v2/upgrade/1')

	def test_meal_addition_to_meal_options(self):
		"""Test API can add a meal to meal options (POST request)"""
		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode('UTF-8'))['access_token']
		print (access_token)

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal added")
		self.assertEqual(response.status_code, 201)

	def test_meal_addition_without_one_field(self):

		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals', 
			headers={"x-access-token": access_token},
			data = json.dumps({
				"meal_category":"Snacks",
				"meal_price":400.00
				}), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Missing argument!")
		self.assertEqual(response.status_code, 400)	

	def test_get_all_meals(self):
		"""Test API can get all meals (GET request)."""
		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']
		
		response = self.client().post(
			'/api/v2/meals',
			headers={"x-access-token": access_token}, 
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		response = self.client().get('/api/v2/meals')
		self.assertEqual(response.status_code, 200)

	def test_a_meal_can_be_edited(self):
		"""Test API can update an existing meal option. (PUT request)"""
		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		new_data = {
					"m_name":"Burger",
					"category":"Snacks",
					"price":750.00
					 }
		res = self.client().post(
			'/api/v2/meals',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(res.status_code, 201)
		res = self.client().put(
			'/api/v2/meals/1', data = json.dumps(
				new_data), content_type = 'application/json')
		self.assertEqual(res.status_code, 200)
		results = self.client().get('/api/v2/meals/1')
		self.assertIn(750.00, float(results.data))

	def test_api_can_get_a_meal_by_id(self):
		"""Test API can get a single meal by using it's id."""
		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		res = self.client().post(
			'/api/v2/meals',
			headers={"x-access-token": access_token},
			data= json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(res.status_code, 201)
		result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
		result = self.client().get(
			'/api/v2/meals/{}'.format(result_in_json['id']))
		self.assertEqual(result.status_code, 200)
		self.assertIn('Burger', str(result.data))

	def test_update_a_meal(self):
		"""Test API can edit an existing meal. (PUT request)"""

		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		new_data = {
					"meal_name":"Burger",
					"meal_category":"Snacks",
					"meal_price":550.00
					}
		response = self.client().put(
			'/api/v2/meals/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				new_data), content_type = 'application/json')
		res = json.loads(response.data)
		self.assertEqual(res["message"], "Meal updated")
		self.assertEqual(response.status_code, 200)

	def test_delete_a_meal(self):
		"""Test API can delete an existing meal. (DELETE request)"""

		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().delete('/api/v2/meals/1',
			headers={"x-access-token": access_token},)
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal deleted!")
		self.assertEqual(response.status_code, 200)

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()


	def test_make_order(self):
		"""Test API can make an order (POST request)."""

		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		data = {
			"owner": "Pemwa",
			"meal_name": "pizza",
			"quantity": 4
		}

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Order sccesfully posted")
		self.assertEqual(response.status_code, 201)

	def test_post_a_menu_for_the_day(self):
		"""Test API can post the menu (POST request)."""

		self.register_a_user()
		self.upgrade_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post('/api/v2/menu',
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(response.status_code, 201)
		response = self.app.get('/api/v2/orders')
		self.assertEqual(response.status_code, 200)

	def test_get_menu_when_not_set(self):
		"""Test API cannot get the menu if not set (GET request)."""

		self.register_a_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		
		response = self.client().get('/api/v2/menu',
			headers={"x-access-token": access_token},)
		self.assertEqual(response.status_code, 404)

	def test_get_menu(self):
		"""Test API can get the menu (GET request)."""

		self.register_a_user()
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(response.status_code, 201)
		response = self.client().get('/api/v2/menu',
			headers={"x-access-token": access_token})
		self.assertEqual(response.status_code, 404)


	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

if __name__ == "__main__":
	unittest.main()

