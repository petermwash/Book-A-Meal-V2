import os
import unittest
import json
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

"""here are my local imports"""
from app import create_app, db
from app.models import User
from tests.u_base import BaseTest

class MealTestCase(BaseTest):
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

	def test_meal_addition_to_meal_options(self):
		"""Test API can add a meal to meal options (POST request)"""
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode('UTF-8'))['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal added")
		self.assertEqual(response.status_code, 201)

	def test_meal_addition_to_meal_options_twice(self):
		"""Test API cannot add same meal to meal options twice(POST request)"""
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode('UTF-8'))['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal already exists!")
		self.assertEqual(response.status_code, 202)

	def test_meal_addition_to_meal_options_with_mising_argument(self):
		"""
		Test API cannot add a meal to meal options with mising argument 
		(POST request)
		"""

		meal_data = {
					
					 }
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode('UTF-8'))['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				meal_data) , content_type = 'application/json')
		
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Missing argument!")
		self.assertEqual(response.status_code, 400)

	def test_price_has_to_be_a_float(self):
		"""
		Test API cannot add a meal to meal options if price not float 
		(POST request)
		"""

		meal_data = {
					"m_name":"Burger",
					"category":"Snacks",
					"price":"400.00"
					 }
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode('UTF-8'))['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				meal_data) , content_type = 'application/json')
		
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Price has to be a float number!")
		self.assertEqual(response.status_code, 400)

	def test_meal_addition_by_a_regular_user(self):
		"""Test API cannot add a meal to meal options by regular user (POST request)"""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals', 
			headers={"x-access-token": access_token},
			data = json.dumps(self.meal_data
				), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)	

	def test_get_all_meals_by_admin(self):
		"""Test API can get all meals by admin user (GET request)."""
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']
		
		response = self.client().get(
			'/api/v2/meals',
			headers={"x-access-token": access_token}, 
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(response.status_code, 200)

	def test_get_all_meals_by_regular_user(self):
		"""Test API cannot get all meals by regular user (GET request)."""
		
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']
		
		response = self.client().get(
			'/api/v2/meals',
			headers={"x-access-token": access_token}, 
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def test_a_meal_can_be_edited(self):
		"""Test API can update an existing meal option. (PUT request)"""
		
		res = self.login_admin_user()
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
			'/api/v2/meals/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				new_data), content_type = 'application/json')
		self.assertEqual(res.status_code, 200)
		results = self.client().get('/api/v2/meals/1',
			headers={"x-access-token": access_token})
		resp = json.loads(results.data)
		self.assertEqual(resp['m_name'], 'Burger')
		self.assertEqual(resp['category'], 'Snacks')
		self.assertEqual(resp['price'], 750.00)

	def test_api_can_get_a_meal_by_id(self):
		"""Test API can get a single meal by using it's id. (GET request)"""
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		res = self.client().post(
			'/api/v2/meals',
			headers={"x-access-token": access_token},
			data= json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(res.status_code, 201)

		result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
		
		result = self.client().get(
			'/api/v2/meals/1',
			headers={"x-access-token": access_token})
		self.assertEqual(result.status_code, 200)
		self.assertIn('Burger', str(result.data))

	def test_regular_user_cannot_edit_a_meal(self):
		"""Test API cannot edit an existing meal by a regular user. (PUT request)"""

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
		self.assertEqual(res["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def test_regular_user_cannot_delete_a_meal(self):
		"""Test API cannot delete an existing meal by a regular user. (DELETE request)"""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().delete('/api/v2/meals/1',
			headers={"x-access-token": access_token},)
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def test_meal_can_be_deleted(self):
		"""Test API can delete an existing meal. (DELETE request)"""
		
		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals',
			headers={"x-access-token": access_token},
			data= json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		resp = self.client().delete('/api/v2/meals/1',
			headers={"x-access-token": access_token})
		result = json.loads(resp.data)
		self.assertEqual(result["message"], "Meal deleted!")
		self.assertEqual(resp.status_code, 200)

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()