import os
import unittest
import json

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
			'email': 'pemwa@me.com',
			'password': '12345'
		}

		"""
		Binding the app with the current context
		and creating all tables
		"""
		with self.app.app_context():
			db.create_all()

	def test_user_creation(self):
		response = self.client().post(
			'/api/v2/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "User created")
		self.assertEqual(response.status_code, 201)

	def test_user_creation_without_all_fields(self):
		response = self.client().post(
			'/api/v2/signup', data = json.dumps({
				"f_name":"peter",
				"l_name":"peter",
				"u_name":"peter",
				"email":"my.email@gmail.com"
				}), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Missing argument")
		self.assertEqual(response.status_code, 400)


	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

class MealTestCase(unittest.TestCase):

	def setUp(self):
		self.app = create_app("testing")
		self.client = self.app.test_client
		self.meal_data = {
					"m_name":"Burger",
					"category":"Snacks",
					"price":400.00
					 }

		"""
		Binding the app with the current context
		and creating all tables
		"""
		with self.app.app_context():
			db.create_all()

	def test_meal_addition(self):
		response = self.client().post(
			'/api/v2/meals', data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal added")

	def test_meal_addition_without_one_field(self):
		response = self.client().post(
			'/api/v2/meals', data = json.dumps({
				"meal_category":"Snacks",
				"meal_price":400.00
				}), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Missing argument")
		self.assertEqual(response.status_code, 400)	

	def test_get_all_meals(self):
		"""Test API can get all meals (GET request)."""
		
		response = self.client().post(
			'/api/v2/meals', data = json.dumps(
				self.meal_data), content_type = 'application/json')
		response = self.client().get('/api/v2/meals')
		self.assertEqual(response.status_code, 200)

	def test_a_meal_can_be_edited(self):
		"""Test API can update an existing meal option. (PUT request)"""
		new_data = {
					"m_name":"Burger",
					"category":"Snacks",
					"price":750.00
					 }
		res = self.client().post(
			'/api/v2/meals', data = json.dumps(
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
		res = self.client().post(
			'/api/v2/meals', data= json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(res.status_code, 201)
		result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
		result = self.client().get(
			'/api/v2/meals/{}'.format(result_in_json['id']))
		self.assertEqual(result.status_code, 200)
		self.assertIn('Burger', str(result.data))


	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

if __name__ == "__main__":
	unittest.main()

