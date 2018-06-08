import os
import unittest
import json
import uuid
import time

"""here are my local imports"""
from app import create_app, db
from tests.u_base import BaseTest

class MenuTestCase(BaseTest):
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

	def test_post_a_menu_for_the_day(self):
		"""Test API can post the menu by a catere user (POST request)."""

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal added to menu")
		self.assertEqual(response.status_code, 200)

	def test_post_a_menu_for_the_day_when_meal_is_in_meal_options(self):
		"""Test API can post the menu by a catere user (POST request)."""

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Meal not available")
		self.assertEqual(response.status_code, 404)

	def test_regular_user_cannot_post_a_menu_for_the_day(self):
		"""Test API cannot post the menu by a regular user (POST request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def test_get_menu_when_not_set(self):
		"""Test API cannot get the menu if not set (GET request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		
		response = self.client().get('/api/v2/menu',
			headers={"x-access-token": access_token})
		self.assertEqual(response.status_code, 404)


	def test_get_menu_when_is_set(self):
		"""Test API can get the menu (GET request)."""

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)

		results = self.client().get('/api/v2/menu',
			headers={"x-access-token": access_token})
		self.assertEqual(results.status_code, 200)
		resp = json.loads(results.data)
		retn = {'1': {'category': 'Snacks', 'meal_name': 'Burger', 'price': 400.0}}
		self.assertIn(retn, resp)

	def test_clear_menu(self):
		"""Test API can clear all the contents in menu (DELETE request)"""

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)

		results = self.client().delete('/api/v2/menu',
			headers={"x-access-token": access_token})
		response = json.loads(results.data)
		self.assertEqual(results.status_code, 200)
		self.assertEqual(response["message"], "Menu cleared succesfully")

	def test_clear_menu_by_regular_user(self):
		"""
		Test API cannot clear all the contents in menu 
		by regular user(DELETE request)
		"""

		res = self.login_user()
		ress = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']
		a_access_token = json.loads(ress.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/meals', 
				headers={"x-access-token": a_access_token},
				data = json.dumps(
				self.meal_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().post('/api/v2/menu/1',
			headers={"x-access-token": a_access_token},
			data = json.dumps(
				self.meal_data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)

		results = self.client().delete('/api/v2/menu',
			headers={"x-access-token": access_token})
		response = json.loads(results.data)
		self.assertEqual(results.status_code, 401)
		self.assertEqual(response["message"], 
			"Not authorized to perform this function!")

	def test_clear_menu_when_not_set(self):
		"""
		Test API cannot clear all the contents in menu 
		when not set(DELETE request)
		"""

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		results = self.client().delete('/api/v2/menu',
			headers={"x-access-token": access_token})
		response = json.loads(results.data)
		self.assertEqual(results.status_code, 404)
		self.assertEqual(response["message"], "Menu not set yet!")


	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()