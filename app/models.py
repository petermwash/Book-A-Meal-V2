from app import db

class User(db.Model):
	"""
	This class represents a user table schema
	"""
	__tablename__ = "users"

	u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	f_name = db.Column(db.String(75), nullable=False)
	l_name = db.Column(db.String(75), nullable=False)
	u_name = db.Column(db.String(75), unique=True, nullable=False)
	email = db.Column(db.String(75), unique=True, nullable=False)
	password = db.Column(db.String(75), nullable=False)

	def __init__(self, f_name, l_name, u_name, email, password):
		self.f_name = f_name
		self.l_name = l_name
		self.u_name = u_name
		self.email = email
		self.password = password

	def save(self):
		"""
		Persist the user in the database
		"""
		db.session.add(self)
		db.session.commit()

	def __repr__(self):
		return "<User: {}>".format(self.u_name)


class Meal(db.Model):
	"""
	Class to represent the meal model
	"""
	__tablename__ = 'meals'
	id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
	m_name = db.Column(db.String(200), nullable=False)
	category = db.Column(db.String(200), nullable=True)
	price = db.Column(db.String(200), nullable = False)

	def __init__(self):
		self.m_name = m_name
		self.category = category
		self.price = price

	def save(self):
		"""
		Persist the meal option in the database
		"""
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def __repr__(self):
		return "<Meal: {}>".format(self.m_name)

