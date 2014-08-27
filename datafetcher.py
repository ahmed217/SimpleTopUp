import db
import multiprocessing
import time
import logging

class DataFetcher(multiprocessing.Process):
	def __init__(self,wdq,gpq,rbq,blq):
        	multiprocessing.Process.__init__(self)
		logging.basicConfig(format='%(asctime)-15s File:%(filename)s Method:%(funcName)s(): Line:%(lineno)d :: %(message)s',level=logging.INFO)
		self.logger = logging.getLogger(__name__)
		
		
		self.wdq = wdq # queue for warid, we will add 5 more queues 

		self.gpq = gpq # queue for grameen

		self.rbq = rbq # queue for robi 

		self.blq = blq # queue for banglalink

	def updateQ(self,db,strid):
		# get the data, update the status from 'U' - unsent to 'Q' - inside queue 
		# so that this data do not come again in the queue
		# later on, the 'Q' status will be updated to 'S' - sent 
		updateQ = 'update smsserver_out set status = \'Q\',transfer_success=\'pending\' where id in '+ strid
		self.logger.info('Update query ' + updateQ )	
		if len(strid) > 2:
			db.query(updateQ)	
	
	def getBL(self,db):
		# query to select banglalink numbers 	
		queryRB = 'select id,recipient,amount,type from smsserver_out where status=\'U\' and recipient like \'019%\''
		rows = db.query(queryRB,'select')
		self.logger.info('Banglalink-Found rows %s' % rows )
		
		# strid is the string of id to update the status to 'Q'-data in queue	
			
		strid = '('	
			
		# fillup the dataqueue using the query
		
		for row in rows:
			self.blq.put(row)
			self.logger.info('Found row %s id %s' % (row, row[0]))
			strid += str(row[0])+','

		# replace last comma of strid with ')'
	
		if len(strid) == 1:
			strid += ')'
		else:
			strid = strid[0:len(strid)-1]+ ')'
		
		self.updateQ(db,strid)	
		
	def getRB(self,db):
		# query to select warid numbers 	
		queryRB = 'select id,recipient,amount,type from smsserver_out where status=\'U\' and recipient like \'018%\''
		rows = db.query(queryRB,'select')
		self.logger.info('Robi-Found rows %s' % rows )
		
		# strid is the string of id to update the status to 'Q'-data in queue	
			
		strid = '('	
			
		# fillup the dataqueue using the query
		
		for row in rows:
			self.rbq.put(row)
			self.logger.info('Found row %s id %s' % (row, row[0]))
			strid += str(row[0])+','

		# replace last comma of strid with ')'
	
		if len(strid) == 1:
			strid += ')'
		else:
			strid = strid[0:len(strid)-1]+ ')'
		
		self.updateQ(db,strid)	
			
	def getWD(self,db):
		# query to select warid numbers 	
		queryWD = 'select id,recipient,amount,type from smsserver_out where status=\'U\' and recipient like \'016%\''
		rows = db.query(queryWD,'select')
		self.logger.info('Warid-Found rows %s' % rows )
		
		# strid is the string of id to update the status to 'Q'-data in queue	
			
		strid = '('	
			
		# fillup the dataqueue using the query
		
		for row in rows:
			self.wdq.put(row)
			self.logger.info('Found row %s id %s' % (row, row[0]))
			strid += str(row[0])+','

		# replace last comma of strid with ')'
	
		if len(strid) == 1:
			strid += ')'
		else:
			strid = strid[0:len(strid)-1]+ ')'
		
		self.updateQ(db,strid)	
			

	def getGP(self,db):
		# query to select grameen numbers 	
		queryGP = 'select id,recipient,amount,type from smsserver_out where status = \'U\' and recipient like \'017%\''
		rows = db.query(queryGP,'select')
		self.logger.info('Grameen-Found rows %s' % rows )
		
		# strid is the string of id to update the status to 'Q'-data in queue	
			
		strid = '('	
			
		# fillup the dataqueue using the query
		
		for row in rows:
			self.gpq.put(row)
			self.logger.info('Found row %s id %s' % (row, row[0]))
			strid += str(row[0])+','

		# replace last comma of strid with ')'
	
		if len(strid) == 1:
			strid += ')'
		else:
			strid = strid[0:len(strid)-1]+ ')'
		
		self.updateQ(db,strid)	
		
	def run(self):
		d = db.DB('b4that.com','root','roott987!!','cavoxnetbt')
		
		self.logger.info('Started Data fetching')

		while True:
	
			self.getWD(d)	

			self.getGP(d)
			
			self.getRB(d)

			self.getBL(d)

			time.sleep(20)	
