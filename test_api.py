import os
import unittest
import json

#here are my local imports
from app import create_app, db

class UserTestCase(unittest.TestCase):
	"""
	This class will contain tests for a user endpoits
	"""
	def setUp(self):
		"""
		Defininng test varibles to be used and initialize the app
		"""
		# import ipdb; ipdb.set_trace()
		self.app = create_app("testing")
		self.client = self.app.test_client()
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
		"""
		Test API can create a user (POST request)
		"""
		response = self.client.post(
			'/api/v2/signup', data = 
				self.user_data , content_type = 'application/json')
		result = json.loads(response.data.decode())
		#print (result)
		self.assertEqual(result["message"], "User created")
		self.assertEqual(response.status_code, 201)


		"""
		response = self.client().post('/api/v2/signup', data=self.user_data)
		self.assertEqual(response.status_code, 201)
		response_msg = json.loads(response.data.decode("UTF-8"))
		self.assertIn("created", response_msg["message"])
		"""

