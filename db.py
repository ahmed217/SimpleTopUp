import mysql.connector
from mysql.connector import errorcode
import logging

class DB:
	def __init__(self,host,user,passwd,db):
		self.config = {
  			'user': user,
  			'password': passwd,
  			'host': host,
  			'database': db,
  			'raise_on_warnings': True,
			}
		logging.basicConfig(level=logging.INFO)
		self.logger = logging.getLogger(__name__)

		try:
  			self.connection = mysql.connector.connect(**self.config)
		except mysql.connector.Error, e:
			self.logger.error("Error %d: %s" %(e.args[0],e.args[1]))
			sys.exit()

	def query(self,q,action=''):
		cursor = self.connection.cursor()
		self.logger.info('Executing '+q)
		cursor.execute(q) 
		rows = None
		if (action == 'select'):
			rows = cursor.fetchall()
		cursor.close()
		if (action =='select'):
			return rows 

