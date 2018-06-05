import os
import unittest
import json
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

"""here are my local imports"""
from app import create_app, db
from tests.u_base import BaseTest
from app.models import User

class UserTestCase(BaseTest):

	"""This class will contain tests for a user endpoits"""
	
	def setUp(self):
		"""Defininng test varibles to be used and initialize the app"""
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

	def test_caterer_can_upgrade_user(self):
		"""Testing API can upgrade user by caterer (PUT request)"""
		self.create_a_user()

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().put(
			'/api/v2/upgrade/1',
			headers={"x-access-token": access_token})

		result = json.loads(response.data)
		self.assertEqual(response.status_code, 200)

	def test_regular_user_cannot_upgrade_user(self):
		"""Testing API cannot upgrade user by regular user (PUT request)"""

		
		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().put(
			'/api/v2/upgrade/1',
			headers={"x-access-token": access_token})

		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def test_cannot_upgrade_unexisting_user(self):
		"""Testing API cannot upgrade user that does not exist (PUT request)"""

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().put(
			'/api/v2/upgrade/2',
			headers={"x-access-token": access_token})

		result = json.loads(response.data)
		self.assertEqual(result["message"], "User 2 doesn\'t exist")
		self.assertEqual(response.status_code, 404)

	def test_get_user_by_admin(self):
		"""Test API can get users by admin user (GET request)"""

		self.create_a_user()

		res = self.login_admin_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().get(
			'/api/v2/users',
			headers={"x-access-token": access_token})
		self.assertEqual(response.status_code, 200)

	def test_get_user_by_regular_user(self):
		"""Test API cannot get users by a regular user (GET request)"""
		
		self.create_a_user()

		res = self.login_user()
		access_token = json.loads(res.data.decode())['access_token']

		response = self.client().get(
			'/api/v2/users',
			headers={"x-access-token": access_token})
		
		result = json.loads(response.data)
		self.assertEqual(result["message"], "Not authorized to perform this function!")
		self.assertEqual(response.status_code, 401)

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()
