from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	full_name = Column(String)
	username = Column(String, primary_key=True)
	user_email = Column(String)
	password = Column(String)

	def __repr__(self):
		return "<User(username='%s', fullname='%s', user_email='%s',password='%s')>" % (
		self.name, self.full_name, self.user_email, self.password)

