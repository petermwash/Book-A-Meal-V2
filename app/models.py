from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from flask import current_app

"""local imports"""
from app import db

class User(db.Model):
	"""This class represents a user model schema"""

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	public_id = db.Column(db.String(75), nullable=False)
	f_name = db.Column(db.String(75), nullable=False)
	l_name = db.Column(db.String(75), nullable=False)
	u_name = db.Column(db.String(75), unique=True, nullable=False)
	email = db.Column(db.String(75), unique=True, nullable=False)
	password = db.Column(db.String(225), nullable=False)
	type_admin = db.Column(db.Boolean, nullable=False, default=False)
	"""ordercart = db.relationship(
		'Order', order_by='Order.cart_id', cascade="all, delete-orphan")"""

	def __init__(self, public_id, f_name, l_name, email, u_name, password, type_admin=False):
		self.public_id = public_id
		self.f_name = f_name
		self.l_name = l_name
		self.email = email
		self.u_name = u_name
		self.password = password 
		self.type_admin = type_admin

	def save(self):
		"""Persist the user in the database"""
		db.session.add(self)
		db.session.commit()


	def __repr__(self):
		"""Return a representation of a user instance."""
		return "<User: {}>".format(self.u_name)

class BlacklistToken(db.Model):
	"""Token Model for storing blacklisted JWT tokens"""

	__tablename__ = 'blacklist_tokens'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	token = db.Column(db.String(500), unique=True, nullable=False)
	blacklisted_on = db.Column(db.DateTime, nullable=False)

	def __init__(self, token):
		self.token = token
		self.blacklisted_on = datetime.now()

	def add(self):
		"""Persist the blacklisted token in the database"""
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def check_token_blacklist(auth_token):
		"""The method checks whether token has been blacklisted"""
		result = BlacklistToken.query.filter_by(token=str(auth_token)).first()
		if result:
			return True
		else:
			return False

	def __repr__(self):
		return '<id: token: {}>'.format(self.token)


class Meal(db.Model):
	"""Class to represent the meal model schema"""

	__tablename__ = 'meals'
	id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
	m_name = db.Column(db.String(200), nullable=True)
	category = db.Column(db.String(200), nullable=True)
	price = db.Column(db.Float, nullable = False)

	def __init__(self, m_name, category, price):
		self.m_name = m_name
		self.category = category
		self.price = price

	def save(self):
		
		"""Persist the meal option in the database"""
		
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_all():
		return Meal.query.all()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def __repr__(self):
		"""Return a representation of meal instance."""
		return "<Meal: {}>".format(self.m_name)

class Order(db.Model):

	"""This class defines the order model schema."""
	__tablename__ = 'orders'

	id = db.Column(db.Integer, primary_key=True)
	meal_name = db.Column(db.String(75), nullable=False)
	quantity = db.Column(db.Integer)
	owner = db.Column(db.String(75), nullable=False)
	ordered_on = db.Column(db.DateTime, nullable=False)
	
	def __init__(self, meal_name, quantity, owner):
		
		"""Initialize an order with a meal_name, quantity, and its owner."""
		
		self.meal_name = meal_name
		self.quantity = quantity
		self.owner = owner
		self.ordered_on = datetime.now()

	def save(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_all():

		"""This method gets all the orders"""
		
		return Order.query.all()

	def __repr__(self):
		"""Return a representation of order instance."""
		return "<Order: {}>".format(self.meal_name)


class Menu(db.Model):
	"""Class to represent the menu model schema"""

	__tablename__ = 'menus'
	id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
	m_name = db.Column(db.String(200), nullable=False)
	category = db.Column(db.String(200), nullable=False)
	price = db.Column(db.Float, nullable = False)
	day = db.Column(db.Date, default=db.func.current_timestamp())

	def __init__(self, m_name, category, price):
		self.m_name = m_name
		self.category = category
		self.price = price

	def save(self):
		
		"""Persist the menu meal in the database"""
		
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_all():
		
		return Menu.query.all()


	def __repr__(self):
		"""Return a representation of menu instance."""
		return "<Menu: {}>".format(self.m_name)

