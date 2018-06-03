import os
import unittest
import json
import uuid
import time

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

	def test_valid_user_logout(self):
		""" Test for user logout before token expires """
		user_data = {
			'public_id': str(uuid.uuid4()),
			'f_name': 'Peter',
			'l_name': 'Mwaura',
			'u_name': 'Pemwa',
			'email': 'pemwa@gm.com',
			'password': '12345'
			#'type_admin': True
			}

		register = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		result = json.loads(register.data)
		self.assertEqual(result["message"], "New user created!")
		self.assertEqual(register.status_code, 201)
		
		signin = self.client().post(
			'/api/v2/auth/login', data = json.dumps({
				'u_name': 'Pemwa',
				'password': '12345'
				}) , content_type = 'application/json')
		result = json.loads(signin.data)
		self.assertEqual(signin.status_code, 200)

		access_token = json.loads(signin.data.decode('UTF-8'))['access_token']

		response = self.client().post(
			'/api/v2/auth/logout',
			headers={"x-access-token": access_token}
			)
		result = json.loads(response.data.decode())
		self.assertEqual(result['message'], "Successfully logged out.")
		self.assertEqual(response.status_code, 200)
	def test_invalid_user_logout(self):
		"""Testing logout with an invalid token"""
		user_data = {
			'public_id': str(uuid.uuid4()),
			'f_name': 'Peter',
			'l_name': 'Mwaura',
			'u_name': 'Pemwa',
			'email': 'pemwa@gm.com',
			'password': '12345'
			}

		register = self.client().post(
			'/api/v2/auth/signup', data = json.dumps(
				self.user_data) , content_type = 'application/json')
		result = json.loads(register.data)
		self.assertEqual(result["message"], "New user created!")
		self.assertEqual(register.status_code, 201)
		
		signin = self.client().post(
			'/api/v2/auth/login', data = json.dumps({
				'u_name': 'Pemwa',
				'password': '12345'
				}) , content_type = 'application/json')
		result = json.loads(signin.data)
		self.assertEqual(signin.status_code, 200)

		access_token = json.loads(signin.data.decode('UTF-8'))['access_token']+'invalidate'

		response = self.client().post(
			'/api/v2/auth/logout',
			headers={"x-access-token": access_token}
			)
		result = json.loads(response.data.decode())
		self.assertEqual(result['message'], "Token is invalid!. You need to sign in first")
		self.assertEqual(response.status_code, 401)

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()
