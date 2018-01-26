from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class VM(Base):
	__tablename__ = 'vms'
	
	ip = Column(String, primary_key=True)
	rancher_id = Column(String)
	blocked = Column(Boolean)

	def __repr__(self):
		return "<VM(ip='%s', blocked='%s', rancher_id='%s')>" % (
		self.ip, str(self.blocked), self.rancher_id)


