import serial
import time
import sys
import modem
import db
import sched

class Banglalink(modem.Modem):
    def __init__(self, port,speed,pin,taskQ):

        super(Banglalink, self).__init__(port,speed)
   	self.pin = pin
	self.taskQ = taskQ
	# for GP the sparkfun modem should be initialized 
	# by at+cnmi=3,3,0,0 to get the msg nofitication
	# by at+cmgf=1 to read the sms in text mode not pdu mode
	self.command('ATZ')
	self.command('ATZ')
	self.command('AT+CNMI=3,3,0,0')
	self.command('AT+CMGF=1')

        self.s = sched.scheduler(time.time, time.sleep)

    def readLastRecharge(self):
	self.serialport.flushInput()
	self.serialport.flushOutput()
	
	msg = 'reading last recharge'
	self.command('AT+CFUN=0')
	self.command('AT+CFUN=1')
	self.command('AT+STGI=0')
	self.command('AT+STGR=0,1,1')
	self.command('AT+STGI=6')
	self.command('AT+STGR=6,1,3')
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(self.pin)
	self.command('AT+STGI=9')
	self.command('AT+STGR=1')
	time.sleep(5)
	self.logger.info('Wait for 5 sec to arrive the sms ')
	msg = self.command('AT+CMGL="REC UNREAD"')
	if msg != None:
		msg = ' '.join(msg.split())
  	return msg		
    
    def doTransfer(self,id,to,amount,type,d):
	self.serialport.flushInput()
	self.serialport.flushOutput()

	amount = int(amount)

	self.command('AT+STGI=0')
	self.command('AT+STGR=0,1,1')
	self.command('AT+STGI=6')
	if type == 'prepaid':
		self.command('AT+STGR=6,1,1')
	else:
		self.command('AT+STGR=6,1,2')
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(to)
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(to)
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(amount)
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(amount)
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(self.pin)
	msg = self.command('AT+STGI=1')
	self.command('AT+STGR=1')
	self.command('AT+STGI=9')

	if msg != None:
		msg = ' '.join(msg.split())

	msg = 'Recipient: '+str(to)+' Amount: '+str(amount)+' '+msg
	
	self.logger.info('Id: %s Msg: %s' % (id,msg) )
	# updating the status from 'Q' to 'S'
	d.query('update smsserver_out set status=\'S\', commandmsg=\''+msg+'\' where id = ' + str(id) +' and status = \'Q\'')
	
	# we need to store the msg somewhere too
	# read the sms and update the successmsg with the id
	# wait for sms to arrive 
	successmsg = self.readLastRecharge()
	d.query('update smsserver_out set successmsg=\''+successmsg+'\',transfer_success=\'success\' where id = ' + str(id))

        d.query('update wf_operator set balance = balance - '+str(amount)+' where op_code = \'019\'')
	
	#now delete all the sms
	self.logger.info('Deleting all sms')
 	self.command('AT+CMGD=1,4')	
		
		
    def run(self):
	d = db.DB('b4that.com','root','roott987!!','cavoxnetbt')
	#count = 500
        while True:
	    if not self.modemOk('BANGLALINK'):
		self.logger.error('Please restart BANGLALINIK MODEM')
		sys.stdout.write("\a")
		
		self.sendEmail('BANGLALINK')

		continue

            # look for incoming request
            if not self.taskQ.empty():
                (id,recp,amount,type) = self.taskQ.get()

		self.logger.info('Task found id:%s recp:%s amount:%s type:%s' % (id,recp,amount,type))	
		self.doTransfer(id,recp,amount,type,d)

	    self.s.enter(60, 1, self.reopen, ())
            self.s.run()		
	    #count -= 1
	    #if (count == 0):
	#	self.reopen()
	#	count = 500
