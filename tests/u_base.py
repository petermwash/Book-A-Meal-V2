import os
import unittest
import json
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

"""here are my local imports"""
from app import create_app, db
from app.models import User

class BaseTest(unittest.TestCase):
	"""This class represents the base for creating authenticating test users"""

	def login_user(self):
		with self.app.app_context():
			"""creating a tempu user admin"""
			user = User(
				public_id=str(uuid.uuid4()),
				f_name='Peter',
				l_name='Mwaura',
				u_name='Pemwa',
				email='pemwa@gm.com',
				password= generate_password_hash('12345', method='sha256')
				)
			user.save()

		return self.client().post(
			'/api/v2/auth/login', data = json.dumps({
				'u_name': 'Pemwa',
				'password': '12345'
				}) , 
			content_type = 'application/json')
			
	def login_admin_user(self):
		with self.app.app_context():
			"""creating a tempu user admin"""
			admin = User(
				public_id=str(uuid.uuid4()),
				f_name='Peter',
				l_name='Mwaura',
				u_name='Admin',
				email='admin@gm.com',
				password= generate_password_hash('12345', method='sha256'),
				type_admin=True
				)
			admin.save()

		return self.client().post(
			'/api/v2/auth/login', data = json.dumps({
				'u_name': 'Admin',
				'password': '12345'
				}) , 
			content_type = 'application/json')

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			db.session.remove()
			db.drop_all()
