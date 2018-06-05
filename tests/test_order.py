import os
import unittest
import json
import uuid
import time

"""here are my local imports"""
from app import create_app, db
from tests.u_base import BaseTest

class OrderTestCase(BaseTest):
	"""This class represents the meals test cases"""

	def setUp(self):
		self.app = create_app("testing")
		self.client = self.app.test_client
		self.order_data = {
					"owner": "Pemwa",
					"meal_name": "pizza",
					"quantity": 4
					 }

		"""Binding the app with the current context and creating all tables"""
		with self.app.app_context():
			db.session.close()
			db.drop_all()
			db.create_all()

	def test_make_order_by_authorised_user(self):
		"""Test API can make an order (POST request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.order_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Order succesfully posted")
		self.assertEqual(response.status_code, 201)

	def test_make_order_by_unauthorised_user(self):
		"""Test API cannot make an order by unauthorised user (POST request)."""

		response = self.client().post(
			'/api/v2/orders',
			data = json.dumps(
				self.order_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Token is  mising!. You need to sign in first")
		self.assertEqual(response.status_code, 401)

	def test_make_order_with_a_missing_field(self):
		"""Test API cannot make an order with a missing field (POST request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		order_data = {
					"owner": "Pemwa",
					"meal_name": "pizza"
					 }

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				order_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Missing argument")
		self.assertEqual(response.status_code, 400)

	def test_quantity_has_to_be_an_integer(self):
		"""Test API cannot take quantity if is not an integer (POST request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		order_data = {
					"owner": "Pemwa",
					"meal_name": "pizza",
					"quantity": '4'
					 }

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				order_data) , content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Quantity has to be an integer Number")
		self.assertEqual(response.status_code, 400)

	def test_get_orders_by_caterer(self):
		"""Test API can get all orders (GET request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.order_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().get(
			'/api/v2/orders',
			headers={"x-access-token": access_token})
		self.assertEqual(response.status_code, 200)

	def test_get_orders_by_unauthorised_user(self):
		"""Test API cannot get orders by regular user (GET request)."""

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.order_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().get(
			'/api/v2/orders',
			headers={"x-access-token": access_token})
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def test_an_order_can_be_edited(self):
		"""Test API can update an order (PUT request)."""

		new_data = {
					"owner": "Pemwa",
					"meal_name": "Burger",
					"quantity": 8
					 }

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().post(
			'/api/v2/orders',
			headers={"x-access-token": access_token},
			data = json.dumps(
				self.order_data) , content_type = 'application/json')
		self.assertEqual(response.status_code, 201)

		response = self.client().put(
			'/api/v2/orders/1',
			headers={"x-access-token": access_token},
			data = json.dumps(
				new_data), content_type = 'application/json')
		result = json.loads(response.data)
		self.assertEqual(response.status_code, 200)

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()
