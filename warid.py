import serial
import time
import sys
import modem
import db

class Warid(modem.Modem):
    def __init__(self, port,speed,pin,taskQ):
        super(Warid, self).__init__(port,speed)
   	self.pin = pin
	self.taskQ = taskQ
 
    def doTransfer(self,id,to,amount,type,d):

      	cusd = ''
        if (type == 'prepaid'):
            cusd = '*444*1*'+str(to)+'*'+str(amount)+'*'+self.pin+'#'
        else:
            cusd = '*444*10*'+str(to)+'*'+str(amount)+'*'+self.pin+'#'
            
        self.command('AT+CUSD=1,\"' + cusd + '\"')
	msg = self.waitFor('+CUSD: 1')
	if msg == None:
		msg = ''

	msg = ' '.join(msg.split())
	self.logger.info('Id: %s Msg: %s' % (id,msg) )

	# updating the status from 'Q' to 'S'
	d.query('update smsserver_out set status=\'S\', commandmsg=\''+msg+'\' where id = ' + str(id) +' and status = \'Q\'')
	
	self.logger.info('Wait for 5 sec to arrive the sms ')
	time.sleep(5)
	# we need to store the msg somewhere too
	# read the sms and update the successmsg with the id
	# wait for sms to arrive 
	self.waitFor('+CMTI: \"SM\"')

	#now read the sms
	successmsg = self.command('AT+CMGR=1')
	successmsg = ' '.join(successmsg.split())
	d.query('update smsserver_out set successmsg=\''+successmsg+'\' where id = ' + str(id))
	
	#now delete all the sms
	self.logger.info('Deleting all sms')
 	self.command('AT+CMGD=1,4')	
	

    def run(self):
	d = db.DB('b4that.com','root','roott987!!','cavoxnetbt')
        while True:
            # look for incoming request
            if not self.taskQ.empty():
                (id,recp,amount,type) = self.taskQ.get()

		
		self.logger.info('Task found id:%s recp:%s amount:%s type:%s' % (id,recp,amount,type))	
		self.doTransfer(id,recp,amount,type,d)	
